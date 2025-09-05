import datetime
import uuid
from dataclasses import dataclass, field

import sqlalchemy as sa
import typer

from worker_safety_service import models
from worker_safety_service.cli.utils import TyperContext, run_async, with_session

# from worker_safety_service.dal.activities import ActivityManager
# from worker_safety_service.dal.library import LibraryManager
# from worker_safety_service.dal.tasks import TaskManager

app = typer.Typer()

get_task_categories = """
 select
   l.id as location,
   t.id as task
 from project_locations l
 join tasks t on l.id = t.location_id
 join projects p on p.id = l.project_id
 join tenants ten on p.tenant_id = ten.id
 where t.archived_at is null
 and t.activity_id is null
 and ten.tenant_name = '{}'
 group by l.id,t.id
"""


@dataclass
class ActivityCreateData:
    location_id: uuid.UUID
    name: str
    start_date: datetime.date | None = None
    end_date: datetime.date | None = None
    status: str | None = None
    tasks: list[uuid.UUID] = field(default_factory=list)


@app.command(name="t2a")
@run_async
@with_session
async def tasks_to_activities(ctx: TyperContext, tenant_name: str) -> None:
    tenants = (await ctx.session.execute(sa.text("select * from tenants"))).all()
    assert tenant_name in [tenant.tenant_name for tenant in tenants]
    _tenant_name = [
        tenant.tenant_name for tenant in tenants if tenant.tenant_name == tenant_name
    ][0]
    # user = (
    #     await ctx.session.execute(
    #         sa.select(models.User)
    #         .join(models.Tenant, onclause=models.Tenant.id == models.User.tenant_id)
    #         .where(models.User.email == email)
    #         .where(models.Tenant.tenant_name == _tenant_name)
    #     )
    # ).one()[0]
    # assert user

    tbyl = (
        await ctx.session.execute(sa.text(get_task_categories.format(_tenant_name)))
    ).all()
    dbtasks = {
        r[0].id: r[0] for r in (await ctx.session.execute(sa.select(models.Task))).all()
    }
    lts = {
        r[0].id: r[0]
        for r in (await ctx.session.execute(sa.select(models.LibraryTask))).all()
    }

    # order tasks by location and library task category
    # could do this in sql but it's not a lot of data
    data: dict[uuid.UUID, dict[str, list[models.Task]]] = {}
    for row in tbyl:
        location_value = data.setdefault(row.location, {})
        task = dbtasks[row.task]
        lt = lts[task.library_task_id]
        category_value = location_value.setdefault(lt.category, [])
        category_value.append(task)

    # group tasks in a category by date range
    for location, categories in data.items():
        for category, tasks in categories.items():
            # ignore typing to allow redefinition
            # order by start date
            tasks: list[models.Task] = sorted(tasks, key=lambda t: t.start_date)  # type: ignore
            grouped = []
            while len(tasks) > 0:
                grouping_task = tasks.pop(0)
                group = [grouping_task]
                ungrouped_tasks = []
                for i, task in enumerate(tasks):
                    group_start_date = min([t.start_date for t in group])
                    group_end_date = max([t.end_date for t in group])
                    if (task.start_date <= group_end_date) and (
                        task.end_date >= group_start_date
                    ):
                        group.append(task)
                    else:
                        ungrouped_tasks.append(task)
                tasks = ungrouped_tasks
                grouped.append(group)
            data[location][category] = grouped  # type: ignore

    # create an activity per task category group
    # lm = LibraryManager(ctx.session)
    # tm = TaskManager(ctx.session, lm)
    # am = ActivityManager(ctx.session, tm)
    tasks_in_activity = {}
    for location, categories in data.items():
        for category, task_groups in categories.items():
            for group in task_groups:  # type: ignore
                start_date = min([t.start_date for t in group])
                end_date = max([t.end_date for t in group])
                task_status = [t.status for t in group]
                status = (
                    task_status[0]
                    if all([task_status[0] == ts for ts in task_status])
                    else "in_progress"
                )
                insert_sql = f"insert into activities values ('{uuid.uuid4()}', '{location}', '{status}', '{start_date}', '{end_date}', NULL, '{category}', NULL) returning *;"
                activity = (await ctx.session.execute(sa.text(insert_sql))).one()
                tasks_in_activity[activity.id] = group

                # if we want audit history use the dal create method
                # ac = models.ActivityCreate(
                #     location_id=location,
                #     name=category,
                #     start_date=start_date,
                #     end_date=end_date,
                #     status=status,
                # )
                # activity, _ = await am.create_activity(ac, [], user)

    # update tasks
    for activity_id, tasks in tasks_in_activity.items():
        for task in tasks:
            await ctx.session.execute(
                sa.text(
                    f"update tasks set activity_id = '{activity_id}' where id = '{task.id}';"
                )
            )

    await ctx.session.commit()

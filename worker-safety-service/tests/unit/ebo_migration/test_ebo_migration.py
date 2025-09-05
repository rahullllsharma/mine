import json

ebo_file_path = "tests/unit/ebo_migration/ebo.json"
library_activity_groups_file_path = (
    "tests/unit/ebo_migration/library_activity_groups.json"
)


def update_ebo_contents(
    ebos: list[dict], activity_group_name_id_map: dict[str, str]
) -> list[dict]:
    for _, ebo in enumerate(ebos):
        contents = json.loads(ebo.get("contents", {}))

        activities = contents.get("activities", []) or []
        high_energy_tasks = contents.get("high_energy_tasks", []) or []

        task_count_per_activity: dict[str, int] = {}
        tasks_with_instance_id = []

        # Processing activities
        for activity in activities:
            tasks = activity.get("tasks", [])
            for task in tasks:
                activity_name = activity.get("name")
                activity["id"] = activity_group_name_id_map.get(activity_name)
                task_id = task.get("id")
                key = f"{activity_name}*{task_id}"
                if key in task_count_per_activity:
                    task_count_per_activity[key] += 1
                else:
                    task_count_per_activity[key] = 1
                task_instance_id = task_count_per_activity[key]
                task["instance_id"] = task_instance_id
                # Just introducing the `hazard` key here, data will be added in the next loop
                task["hazards"] = []
                tasks_with_instance_id.append(task)

        # Matching high energy tasks with corresponding tasks from activities

        for index, high_energy_task in enumerate(high_energy_tasks):
            # adding activity_id values to high_energy_task["activity_id"]
            if not high_energy_task["activity_id"]:
                high_energy_task["activity_id"] = activity_group_name_id_map.get(
                    high_energy_task["activity_name"], None
                )
            # Only if len(high_energy_tasks) is less than total activity->tasks.
            if index < len(tasks_with_instance_id):
                corresponding_task = tasks_with_instance_id[index]
                # Just a precaution, this is unlikely to happen, but if the corresponding task
                # has a different id than the high_energy_task-> id,
                # i.e they are different then we will assign that particular
                # high_energy_task's instance_id as 1.
                if corresponding_task.get("id") == high_energy_task["id"]:
                    high_energy_task["instance_id"] = corresponding_task["instance_id"]
                    corresponding_task["hazards"] = high_energy_task.get(
                        "observations", []
                    )
                else:
                    high_energy_task["instance_id"] = 1

            else:
                # If there are fewer tasks than high-energy tasks, handle the edge case gracefully
                high_energy_task["instance_id"] = 1

        ebo["contents"] = contents

    return ebos


# This test case is being used to test the alembic revision `95b2a2c82d88`with integration data,
# once this migration is successfully deployed to prod and if needed
# this test case and it's related data can be skipped/removed as per requirements
def test_ebo_migration() -> None:
    ebo_data = {}
    activity_group_data = {}

    with open(ebo_file_path, "r") as file:
        ebo_data = json.load(file)
    with open(library_activity_groups_file_path, "r") as file:
        activity_group_data = json.load(file)

    ebos: list[dict] = ebo_data["energy_based_observations"]

    activity_group_name_id_map: dict[str, str] = {}
    for lag in activity_group_data["library_activity_groups"]:
        activity_group_name_id_map[lag["name"]] = lag["id"]
    updated_ebos: list[dict] = update_ebo_contents(
        ebos=ebos, activity_group_name_id_map=activity_group_name_id_map
    )
    assert updated_ebos
    for ebo in updated_ebos:
        contents = ebo.get("contents", {})

        activities = contents.get("activities", []) or []
        high_energy_tasks = contents.get("high_energy_tasks", []) or []

        if activities:
            for activity in activities:
                tasks = activity.get("tasks", [])
                for task in tasks:
                    assert task["instance_id"] is not None
                    if high_energy_tasks:
                        assert "hazards" in task
        if high_energy_tasks:
            for high_energy_task in high_energy_tasks:
                # here we are excluding `Civil Work` specifically because for the data that
                # is being used here, this library_activity_group does not exists anymore,
                # i.e. it was deleted or renamed,
                # hence we are not able to find the corresponding id
                if high_energy_task["activity_name"] and high_energy_task[
                    "activity_name"
                ] not in ["Civil work"]:
                    assert high_energy_task["activity_id"] is not None
                assert high_energy_task["instance_id"] is not None

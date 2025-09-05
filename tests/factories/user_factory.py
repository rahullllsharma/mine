from uuid import UUID, uuid4

from faker import Faker
from polyfactory.factories.pydantic_factory import ModelFactory

from ws_customizable_workflow.models.users import User, UserBase

fake = Faker()


class UserBaseFactory(ModelFactory):
    __model__ = UserBase
    id: UUID = uuid4()
    first_name: str = fake.name()
    last_name: str = fake.name()
    role: str = "Administrator"
    tenant_name: str = "asgard_test"


class UserFactory(ModelFactory):
    __model__ = User
    first_name: str = fake.first_name()
    last_name: str = fake.last_name()
    role: str = "Administrator"
    tenant_name: str = "asgard_test"

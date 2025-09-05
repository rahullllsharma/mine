import typing
import uuid
from functools import cache
from types import GenericAlias
from typing import Any, Generic, NamedTuple, Type, TypeVar

from pydantic import BaseModel, Field, HttpUrl, create_model
from pydantic.generics import GenericModel

T = TypeVar("T", bound=BaseModel)


# Public
class RelationshipFieldAttributes(NamedTuple):
    type: str | None
    url_supplier: typing.Callable[[uuid.UUID], HttpUrl]
    alias: str | None = None  # Used to override the key in the relationships dict


class RelatedLink(BaseModel):
    related: HttpUrl


class SelfLink(BaseModel):
    self: HttpUrl


class PaginatedLinks(SelfLink):
    self: HttpUrl = Field(description="Link to this endpoint.")
    next: typing.Optional[HttpUrl] = Field(
        default=None, description="The link to the next batch of elements."
    )


class PaginationMetaData(BaseModel):
    """
    Our API will return a paginated response in the endpoints that return multiple elements.
    It is formatted according to the JSON:API spec. The results are returned as an array in the data attribute.
    Each of the results will include a link to itself.
    Besides the results, the response will include the limit as well as a link to the next elements
    in the collection and the link to itself. In the meta and links section respectively.

    The limit returned by the server is not guaranteed to be the same as the limit requested by the client.
    The server will reserve the right to truncate the limit to ensure integrity of the system.

    Additionally, the server will return the total number of elements in the collection and the number of remaining
    elements after the cursor. These properties are optional because they are hard to compute.
    The user may request them by specifying the show_results=true query param.
    """

    limit: int = Field(
        default=20,
        description="The maximum number of elements returned by this endpoint.",
    )
    total: int | None = Field(
        default=None,
        description="The total number of elements that exist in the server.",
    )
    remaining: int | None = Field(
        default=None, description="The remaining elements after this batch."
    )


class RelationshipDescriptor(NamedTuple):
    entity_field_name: str  # Name of the field in the EntityModel
    relationship_name: str  # Name of the relationship in the relationships dict
    target_entity_name: str  # Target Entity Name
    is_many: bool  # True if is a many relationship
    url_supplier: typing.Callable[[uuid.UUID], HttpUrl]


class BaseEntityType(BaseModel):
    __model_class__: type[BaseModel]


class DataWrapper(GenericModel, Generic[T]):
    data: T

    @classmethod
    def get_target_class(cls) -> type[BaseEntityType]:
        resp_class: type[BaseEntityType] = cls.__annotations__["data"]
        if isinstance(resp_class, GenericAlias):
            origin = typing.get_origin(resp_class)
            assert origin and issubclass(origin, list)
            resp_class = typing.get_args(resp_class)[0]
        return resp_class

    @classmethod
    def build_element(cls, id: uuid.UUID | None, attributes: BaseModel) -> Any:
        resp_class = cls.get_target_class()
        attr_class = resp_class.__fields__["attributes"].type_
        self_link_supplier = getattr(
            resp_class.__model_class__, "__entity_url_supplier__"
        )

        _, relationships = _analyse_model_fields(resp_class.__model_class__)
        attrs = attr_class(**attributes.dict())
        # TODO: Simplify this relationship class code. It's a bit difficult to read.
        if "relationships" in resp_class.__fields__:
            relationship_class = resp_class.__fields__["relationships"].type_
            if id is not None:
                many_relationships = {
                    rel_descr.relationship_name: {
                        "links": RelatedLink(related=rel_descr.url_supplier(id)),
                    }
                    for rel_descr in relationships
                    if rel_descr.is_many
                }
            else:
                many_relationships = {}

            rel = {
                "relationships": relationship_class(
                    **{
                        rel_descr.relationship_name: {
                            "data": {
                                "id": attributes.dict()[rel_descr.entity_field_name],
                            },
                            "links": RelatedLink(
                                related=rel_descr.url_supplier(
                                    attributes.dict()[rel_descr.entity_field_name]
                                )
                            ),
                        }
                        for rel_descr in relationships
                        if not rel_descr.is_many
                    },
                    **many_relationships,
                )
            }
        else:
            rel = {}

        return resp_class(
            id=id, attributes=attrs, links=SelfLink(self=self_link_supplier(id)), **rel
        )

    @classmethod
    def build_entity(cls, entity_data: Any) -> BaseModel:
        """
        !!!WARNING!!! We cannot rely on this method to build the many relationship up from the response/request because
        there is not enough information in the payload.
        """
        # TODO: Implement a lazy loading mecanism for many relationships.

        resp_class = cls.get_target_class()
        model_class = resp_class.__model_class__
        _, relationships = _analyse_model_fields(model_class)

        return model_class(
            **dict(
                **entity_data.attributes.dict(),
                **{
                    rel_descr.entity_field_name: getattr(
                        entity_data.relationships, rel_descr.target_entity_name
                    ).data.id
                    for rel_descr in relationships
                    if not rel_descr.is_many
                },
            )
        )

    @classmethod
    def build_entity_with_id(cls, entity_data: Any) -> tuple[uuid.UUID, BaseModel]:
        entity_obj = cls.build_entity(entity_data)
        return entity_data.id, entity_obj


class ResponseWrapper(DataWrapper[T], Generic[T]):
    @classmethod
    def pack(cls, id: uuid.UUID, attributes: T) -> Any:
        return cls(data=cls.build_element(id, attributes))

    def unpack(self) -> tuple[uuid.UUID, BaseModel]:
        return self.build_entity_with_id(self.data)


class RequestWrapper(DataWrapper[T], Generic[T]):
    @classmethod
    def pack(cls, attributes: T) -> Any:
        return cls(data=cls.build_element(None, attributes))

    def unpack(self) -> BaseModel:
        return self.build_entity(self.data)


# TODO: Fix List[T] as the generic argument
class BulkResponseWrapper(DataWrapper[list[T]], Generic[T]):  # type: ignore
    @classmethod
    def pack_many(cls, elements: list[tuple[uuid.UUID, BaseModel]]) -> Any:
        arr = []
        for id, model in elements:
            built_e = cls.build_element(id, model)
            arr.append(built_e)

        return cls(data=arr)

    def unpack(self) -> list[tuple[uuid.UUID, BaseModel]]:
        ret = []
        for data_elem in self.data:
            e = self.build_entity_with_id(data_elem)
            ret.append(e)
        return ret


# TODO: Fix List[T] as the generic argument
class BulkRequestWrapper(DataWrapper[list[T]], Generic[T]):  # type: ignore
    @classmethod
    def pack_many(cls, elements: list[BaseModel]) -> Any:
        arr = []
        for e in elements:
            built_e = cls.build_element(None, e)
            arr.append(built_e)
        return cls(data=arr)

    def unpack(self) -> list[BaseModel]:
        ret = []
        for data_elem in self.data:
            e = self.build_entity(data_elem)
            ret.append(e)
        return ret


class PaginatedBulkResponseWrapper(DataWrapper[list[T]], Generic[T]):  # type: ignore
    meta: PaginationMetaData | None
    links: PaginatedLinks

    @classmethod
    def pack_many(
        cls,
        elements: list[tuple[uuid.UUID, BaseModel]],
        paginated_links: PaginatedLinks,
        pagination_meta: PaginationMetaData | None = None,
    ) -> Any:
        arr = list(map(lambda e: cls.build_element(e[0], e[1]), elements))
        return cls(links=paginated_links, data=arr, meta=pagination_meta)

    def unpack(self) -> list[tuple[uuid.UUID, BaseModel]]:
        ret = list(map(self.build_entity_with_id, self.data))
        return ret


@cache
def _analyse_model_fields(
    a_type: Type[T],
) -> tuple[list, list[RelationshipDescriptor]]:
    actual_fields = []
    relationships: list[RelationshipDescriptor] = []
    for model in a_type.__fields__.values():
        relationship_attributes: RelationshipFieldAttributes | None = (
            model.field_info.extra.get("relationship", None)
        )
        if relationship_attributes:
            is_many = (
                isinstance(model.outer_type_, GenericAlias)
                and typing.get_origin(model.outer_type_) is list
            )
            target_entity_name = relationship_attributes.type or model.name
            if relationship_attributes.alias:
                relationship_name = relationship_attributes.alias
            else:
                relationship_name = (
                    target_entity_name if not is_many else target_entity_name + "s"
                )

            relationships.append(
                RelationshipDescriptor(
                    entity_field_name=model.name,
                    relationship_name=relationship_name,
                    target_entity_name=target_entity_name,
                    is_many=is_many,
                    url_supplier=relationship_attributes.url_supplier,
                )
            )
        else:
            actual_fields.append(model)

    return (actual_fields, relationships)


def create_models(model_type: Type[T]) -> tuple[Type, Type, Type, Type, Type]:
    # TODO: Clean-up this method, its a mess.
    # TODO: Fix My Typing
    actual_fields, relationships = _analyse_model_fields(model_type)

    attributes_type = create_model(  # type: ignore
        model_type.__name__,
        **{
            model_field.name: (model_field.type_, model_field.field_info)
            for model_field in actual_fields
        },
    )

    request_relationship_types = {}
    response_relationship_types = {}
    for model_field in relationships:
        if not model_field.is_many:
            # TODO Extract to a separate method, its terrible to read this.
            relationship_entry_type = create_model(
                f"JSON:API_Relationship[{model_type.__name__}][{model_field.relationship_name}]",
                id=(uuid.UUID, ...),
                type=Field(
                    default=model_field.target_entity_name,
                    const=True,
                ),
            )

            relationship_type = create_model(
                f"JSON:API_Relationship_Request[{model_type.__name__}][{model_field.relationship_name}]",
                data=(relationship_entry_type, ...),
            )

            relationship_type_response = create_model(
                f"JSON:API_Relationship_Response[{model_type.__name__}][{model_field.relationship_name}]",
                __base__=relationship_type,
                links=(RelatedLink, ...),
            )

            request_relationship_types[model_field.relationship_name] = (
                relationship_type,
                ...,
            )
            response_relationship_types[model_field.relationship_name] = (
                relationship_type_response,
                ...,
            )
        else:
            many_relationship_type_response = create_model(
                f"JSON:API_Relationship_Response[{model_type.__name__}][{model_field.relationship_name}]",
                links=(RelatedLink, ...),
            )

            response_relationship_types[model_field.relationship_name] = (
                many_relationship_type_response,
                ...,
            )

    include_relationships_field = {}
    if len(request_relationship_types) > 0:
        request_relationship_type = create_model(  # type: ignore
            f"JSON:API_Relationship_Request[{model_type.__name__}]",
            **request_relationship_types,
        )
        include_relationships_field = {
            "relationships": (request_relationship_type, ...)
        }

    response_relationship_type = create_model(  # type: ignore
        f"JSON:API_Relationship_Response[{model_type.__name__}]",
        **response_relationship_types,
    )

    request_entity_type = create_model(  # type: ignore
        f"JSON:API_Request[{model_type.__name__}]",
        __base__=BaseEntityType,
        __model_class__=model_type,
        type=Field(default=getattr(model_type, "__entity_name__"), const=True),
        attributes=(attributes_type, ...),
        **include_relationships_field,
    )

    response_entity_type = create_model(
        f"JSON:API_Response[{model_type.__name__}]",
        __base__=request_entity_type,
        id=(uuid.UUID, ...),
        relationships=(response_relationship_type, ...),
        links=(SelfLink, ...),
    )

    return (
        RequestWrapper[request_entity_type],  # type: ignore
        BulkRequestWrapper[request_entity_type],  # type: ignore
        ResponseWrapper[response_entity_type],  # type: ignore
        BulkResponseWrapper[response_entity_type],  # type: ignore
        PaginatedBulkResponseWrapper[response_entity_type],  # type: ignore
    )

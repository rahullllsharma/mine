from typing import Any, NamedTuple, Type


class EncodedObject(NamedTuple):
    module: str
    name: str
    data: dict[str, Any]
    injectables: dict[str, Any]


def encode_object(obj: Any, injectables: dict[Type, Any] = {}) -> EncodedObject:
    cls = type(obj)
    data_fields = {}
    injectable_fields = {}
    if hasattr(cls, "__getstate__"):
        data_fields = obj.__getstate__
    elif hasattr(cls, "__dict__"):
        # if they are injectables: put with type
        for k, v in obj.__dict__.items():
            if (t := type(v)) in injectables:
                # Will add as a placeholder
                injectable_fields[k] = t
            elif (t := v.__class__) in injectables:
                # Will add as a placeholder
                injectable_fields[k] = t
            elif not k.startswith("_"):
                # Private attributes won't be included
                data_fields[k] = v
    else:
        raise RuntimeError(f"Could not deserialize class: {cls}")

    return EncodedObject(
        module=cls.__module__,
        name=cls.__name__,
        data=data_fields,
        injectables=injectable_fields,
    )

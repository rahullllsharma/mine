from typing import Any

try:
    import google.protobuf.descriptor

    google.protobuf.descriptor._Deprecated.count = 0
except:  # noqa: E722
    pass

from worker_safety_service.clustering import vector_tile_p3_pb2

PROPERTIES_TYPES = [i.name for i in vector_tile_p3_pb2._TILE_VALUE.fields]


def decode_tile(binary: bytes) -> dict:
    tile = vector_tile_p3_pb2.tile()
    tile.ParseFromString(binary)
    return {
        layer.name: {
            "extent": layer.extent,
            "version": layer.version,
            "features": [
                {
                    "geometry": None,  # TODO
                    "properties": parse_tags(layer.keys, layer.values, feature.tags),
                    "id": feature.id,
                    "type": feature.type,
                }
                for feature in layer.features
            ],
        }
        for layer in tile.layers
    }


def parse_tags(keys: Any, values: Any, tags: Any) -> dict:
    properties = {}
    assert len(tags) % 2 == 0, "Unexpected number of tags"
    for key_idx, val_idx in zip(tags[::2], tags[1::2]):
        key = keys[key_idx]
        value = values[val_idx]
        for candidate in PROPERTIES_TYPES:
            if value.HasField(candidate):
                properties[key] = getattr(value, candidate)
                break
        else:
            raise ValueError("%s is an unknown value")
    return properties

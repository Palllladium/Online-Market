from common.common.models.products import Product
from typing import Union, get_args, get_origin, Dict
from sqlmodel import SQLModel
from datetime import datetime
from elasticsearch import AsyncElasticsearch


PYDANTIC_TO_ES = {
    str: {"type": "text"},
    int: {"type": "integer"},
    float: {"type": "float"},
    bool: {"type": "boolean"},
    datetime: {"type": "date"}
}


def generate_es_mappings(model: type[SQLModel]) -> Dict:
    properties = {}

    for field_name, field in model.model_fields.items():
        field_type = field.annotation

        if get_origin(field_type) is Union:
            field_type = [arg for arg in get_args(field_type) if arg is not type(None)][0]

        field_type = getattr(field_type, '__origin__', field_type)

        es_type = PYDANTIC_TO_ES.get(field_type, {"type": "text"})
        properties[field_name] = es_type

    return {"mappings": {"properties": properties}}


async def ensure_index_exists(es: AsyncElasticsearch, index: str):
    if not (await es.indices.exists(index=index)):
        await es.indices.create(
            index=index, 
            body=generate_es_mappings(Product)
        )
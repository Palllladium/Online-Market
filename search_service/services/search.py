from common.common.core.db_config import es, INDEX, SIZE


async def search_products(
    name: str | None = None, 
    description: str | None = None
):
    must_clauses = []

    if name:
        must_clauses.append({"match": {"product_name": name}})
    if description:
        must_clauses.append({"match": {"product_description": description}})

    query = {
        "size": SIZE,
        "query": {
            "bool": {
                "must": must_clauses
            }
        }
    }

    response = await es.search(index=INDEX, body=query)
    return [hit["_source"] for hit in response["hits"]["hits"]]
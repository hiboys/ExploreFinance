import argparse
import asyncio
import json

import httpx

from common import ENTITY_API, SUPPORTED_CLASS_CODES, EntityInfo, auth_headers


async def validate_entity(query: str) -> EntityInfo:
    headers = {"Content-Type": "application/json", **auth_headers()}
    payload = {"content": query}
    data = {}
    async with httpx.AsyncClient(timeout=30.0, verify=True) as client:
        resp = await client.post(ENTITY_API, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

    # Compatible parse for dialogTagsV2 possible shapes.
    first = None
    if isinstance(data, dict):
        d = data.get("data")
        if isinstance(d, dict) and isinstance(d.get("entityMetricList"), list):
            entity_list = d.get("entityMetricList")
            first = entity_list[0][0] if entity_list and isinstance(entity_list[0], list) and entity_list[0] else None
        elif isinstance(d, dict) and isinstance(d.get("entityList"), list) and d.get("entityList"):
            first = d.get("entityList")[0]
        elif isinstance(d, list) and d and isinstance(d[0], dict):
            first = d[0]
    if not isinstance(first, dict):
        raise RuntimeError("实体识别未找到有效实体")

    class_code = str(first.get("classCode") or "")
    if class_code not in SUPPORTED_CLASS_CODES:
        raise RuntimeError("目前仅支持沪深京港美实体进行业绩点评")
    secu_code = str(first.get("secuCode") or "")
    if not secu_code:
        raise RuntimeError("实体识别缺少 secuCode")

    return EntityInfo(
        class_code=class_code,
        secu_code=secu_code,
        market_char=str(first.get("marketChar") or ""),
        secu_name=str(first.get("shortName") or ""),
    )


def run_cli() -> None:
    parser = argparse.ArgumentParser(description="Validate entity from query.")
    parser.add_argument("--query", required=True)
    args = parser.parse_args()

    async def _main() -> None:
        entity = await validate_entity(args.query)
        print(
            json.dumps(
                {
                    "classCode": entity.class_code,
                    "secuCode": entity.secu_code,
                    "marketChar": entity.market_char,
                    "secuName": entity.secu_name,
                    "emCode": entity.em_code,
                },
                ensure_ascii=False,
                indent=2,
            )
        )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_main())
    finally:
        loop.close()


if __name__ == "__main__":
    run_cli()


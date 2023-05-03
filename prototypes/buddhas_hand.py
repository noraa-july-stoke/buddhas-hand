import asyncio
from typing import Dict, Union
import sys


# import strawberry
import graphql
from tortoise import Tortoise
import aioredis


class BuddhasHand:
    def __init__(self, db_configs: Dict[str, Dict[str, Union[str, int]]]):
        self.db_configs = db_configs
        self.app = None

    async def setup(self):
        tasks = []
        # goes through all the database config objects and connects them
        for db_name, db_config in self.db_configs.items():
            if db_config.get("type") == "tortoise":
                tasks.append(self.connect_tortoise(db_name, db_config))
            elif db_config.get("type") == "redis":
                tasks.append(self.connect_redis(db_name, db_config))
            else:
                raise ValueError(f"Unsupported database type: {db_config.get('type')}")
        await asyncio.gather(*tasks)
        from ..schema import schema
        self.app = graphql.GraphQL(schema)

    async def connect_tortoise(self, db_name: str, db_config: Dict[str, Union[str, int]]):
            db_url = db_config.get("db_url")
            modules = db_config.get("modules")
            print(f"db_url: {db_url}")
            print(f"modules: {modules}")
            await Tortoise.init(db_url=db_url, modules=modules)
            await Tortoise.generate_schemas()

    async def connect_redis(self, db_name: str, db_config: Dict[str, Union[str, int]]):
        redis = await aioredis.create_redis_pool(
            db_config.get("db_url"),
            db=db_config.get("db", 0),
        )
        setattr(self, f"{db_name}_redis", redis)

    async def shutdown(self):
        tasks = []
        for db_name, db_config in self.db_configs.items():
            db_type = db_config.get("type")
            if db_type == "tortoise":
                tasks.append(self.disconnect_tortoise(db_name, db_config))
            elif db_type == "redis":
                tasks.append(self.disconnect_redis(db_name, db_config))
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
        await asyncio.gather(*tasks)

    async def disconnect_tortoise(self, db_name: str, db_config: Dict[str, Union[str, int]]):
        await Tortoise.close_connections()

    async def disconnect_redis(self, db_name: str, db_config: Dict[str, Union[str, int]]):
        redis = getattr(self, f"{db_name}_redis", None)
        if redis:
            redis.close()
            await redis.wait_closed()
            delattr(self, f"{db_name}_redis")


# db_configs = {
#     "tortoise_db": {
#         "type": "tortoise",
#         "db_url": "sqlite://db.sqlite3",
#         "modules": {
#             "app": ["app.models"]
#         }
#     },
#     "redis_db": {
#         "type": "redis",
#         "db_url": "redis://localhost:6379",
#         "db": 0
#     }
# }

# async def test_buddhas_hand():
#     bh = BuddhasHand(db_configs)
#     await bh.setup()
#     # perform some database operations here
#     await bh.shutdown()

# asyncio.run(test_buddhas_hand())

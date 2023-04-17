# buddhas-hand
The default ORM for Tangerine



## This is an idea sheet for how to implement buddhas hand
## Some parts of this document may not make full sense yet as I am working it out still


### Buddha's Hand class structural ideas

```python
import asyncio
from typing import Dict, Union

from strawberry.asgi import GraphQL
from tortoise import Tortoise
from aioredis import create_redis_pool


class BuddhasHand:
    def __init__(self, db_configs: Dict[str, Dict[str, Union[str, int]]]):
        self.db_configs = db_configs
        self.app = None

    async def setup(self):
        tasks = []
        for db_name, db_config in self.db_configs.items():
            db_type = db_config.get("type")
            if db_type == "tortoise":
                tasks.append(self.connect_tortoise(db_name, db_config))
            elif db_type == "redis":
                tasks.append(self.connect_redis(db_name, db_config))
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
        await asyncio.gather(*tasks)
        from .schema import schema
        self.app = GraphQL(schema)

    async def connect_tortoise(self, db_name: str, db_config: Dict[str, Union[str, int]]):
        await Tortoise.init(
            db_url=db_config.get("conn_string"),
            modules=db_config.get("modules", {}).get(db_name, []),
        )

    async def connect_redis(self, db_name: str, db_config: Dict[str, Union[str, int]]):
        redis = await create_redis_pool(
            db_config.get("conn_string"),
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
```




### Example usage of Buddha's Hand

```python
from os import environ
from tangerine import Tangerine, Router, Ctx, TangerineError
from key_limes import KeyLimes
from buddhas_hand import BuddhasHand

# Create a dict of database configurations
# there is an optional redis caching option for performance
db_configs = {
    "mongo": {
        "conn_string": environ.get("MONGO_CONN_STRING"),
        "redis_cache": True,
        "redis_host": environ.get("REDIS_HOST"),
        "redis_port": environ.get("REDIS_PORT"),
        "redis_db": 0
    },
    "postgres": {
        "provider": "tortoise",
        "conn_string": environ.get("POSTGRES_CONN_STRING")
    }
}

# Initialize the BuddhasHand instance with the database configurations
db = BuddhasHand(db_configs)

# Initialize the Tangerine server
tangerine = Tangerine()

# Initialize the KeyLimes keychain
keychain = KeyLimes(
    google_cloud=environ.get("GOOGLE_CLOUD_CREDENTIAL"),
    secret_keys=[environ.get("SECRET_KEY_1"), environ.get("SECRET_KEY_2")],
    db_host=environ.get("DB_HOST"),
    db_conn_string=environ.get("DB_CONN_STRING")
)

# Initialize the Yuzu authentication instance
yuzu = Yuzu(
    strategies={"providers": ["google", "facebook", "twitter", "github"], "local": True},
    keychain=keychain
)

# Set the auth instance of Tangerine to Yuzu
tangerine.auth = yuzu

# Define some routes
router = Router()

@router.get("/")
async def index(ctx: Ctx):
    return {"message": "Hello World!"}

# Mount the router to the Tangerine server
tangerine.use(router)

# Start the server
tangerine.start()


```



```python
from graphene import ObjectType, String, Int, Schema, List
from buddhas_hand import BuddhasHand

db = BuddhasHand(host="localhost", port=27017, database="mydb")

class Author(ObjectType):
    name = String()
    email = String()

class Post(ObjectType):
    title = String()
    content = String()
    author = Author()

class Query(ObjectType):
    post = Post(title=String())

    async def resolve_post(parent, info, title):
        post = await db.posts.find_one({"title": title})
        author = await db.authors.find_one({"_id": post["author_id"]})
        return Post(title=post["title"], content=post["content"], author=Author(name=author["name"], email=author["email"]))

    posts = List(Post)

    async def resolve_posts(parent, info):
        posts = await db.posts.find().to_list()
        return [Post(title=post["title"], content=post["content"]) for post in posts]

schema = Schema(query=Query)

```

## More Details TBD

# buddhas-hand
The default ORM for Tangerine



## This is an idea sheet for how to implement buddhas hand from the user's perspective
## Some parts of this document may not make full sense yet as I am working it out still


### Buddha's Hand class structural ideas

```python

from typing import Any, Dict
from aioredis import Redis, create_redis_pool

class BuddhasHand:
    def __init__(
        self,
        mongo_uri: str,
        mongo_database: str,
        redis_uri: str = None,
        redis_password: str = None,
        redis_db: int = 0,
        redis_ttl: int = 3600,
    ) -> None:
        self.mongo_uri = mongo_uri
        self.mongo_database = mongo_database

        self.redis_uri = redis_uri
        self.redis_password = redis_password
        self.redis_db = redis_db
        self.redis_ttl = redis_ttl

        self.redis: Redis = None

    async def connect(self) -> None:
        # Connect to MongoDB
        await Tortoise.init(
            db_url=self.mongo_uri,
            modules={"models": ["app.models"]},
        )
        await Tortoise.generate_schemas()

        # Connect to Redis
        if self.redis_uri:
            self.redis = await create_redis_pool(
                self.redis_uri, db=self.redis_db, password=self.redis_password
            )

    async def close(self) -> None:
        # Close MongoDB connection
        await Tortoise.close_connections()

        # Close Redis connection
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()

    async def get_cached(self, key: str) -> Any:
        if self.redis:
            cached_data = await self.redis.get(key)
            if cached_data:
                return pickle.loads(cached_data)

        return None

    async def set_cached(self, key: str, value: Any) -> None:
        if self.redis:
            cached_data = pickle.dumps(value)
            await self.redis.setex(key, self.redis_ttl, cached_data)


```

```python
from os import environ
from tangerine import Tangerine, Keychain, Router, Ctx, TangerineError
from key_limes import KeyLimes
from buddhas_hand import BuddhasHand
from tortoise import Tortoise, run_async
from aioredis import create_redis_pool

db = BuddhasHand(
    host=environ.get("DB_HOST"),
    conn_string=environ.get("DB_CONN_STRING")
)

# Set up Tortoise ORM with multiple databases
TORTOISE_ORM = {
    "connections": {
        "default": environ.get("DB_CONN_STRING"),
        "secondary": environ.get("SECONDARY_CONN_STRING"),
    },
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        },
        "secondary_models": {
            "models": ["app.secondary_models"],
            "default_connection": "secondary",
        },
    },
}

async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

# Set up a NoSQL engine, in this case Redis
async def init_redis():
    redis = await create_redis_pool(environ.get("REDIS_CONN_STRING"))
    return redis

async def start():
    await init_db()
    redis = await init_redis()
    app = Tangerine()

    keychain = KeyLimes(
        google_cloud=environ.get("GOOGLE_CLOUD_CREDENTIAL"),
        secret_keys=[environ.get("SECRET_KEY_1"), environ.get("SECRET_KEY_2")],
        db_host=environ.get("DB_HOST"),
        db_conn_string=environ.get("DB_CONN_STRING")
    )

    # Use Tortoise ORM with the app instance
    app.db = Tortoise.get_db_client("default")
    app.secondary_db = Tortoise.get_db_client("secondary")

    # Use the Redis instance with the app instance
    app.redis = redis

    yuzu = Yuzu(
        strategies={"providers": ["google", "facebook", "twitter"], "local": True},
        keychain=keychain
    )

    app.auth = yuzu
    app.start()

if __name__ == "__main__":
    run_async(start())

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

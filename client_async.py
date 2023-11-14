import asyncio
import json
from random import random
from uuid import uuid4

from redis.asyncio import Redis
from redis.asyncio.client import PubSub

RPC_ID = "DemoServer"


async def async_range(count):
    for i in range(count):
        yield (i)
        await asyncio.sleep(0.0)


async def process_result(pubsub: PubSub):
    async for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            try:
                return data["result"]
            except KeyError:
                raise Exception(data["error"]["message"])


async def rpc(client: Redis, message: dict):
    async with client.pubsub() as pubsub:
        await pubsub.subscribe(message["id"])
        future = asyncio.create_task(process_result(pubsub))
        await client.lpush(RPC_ID, json.dumps(message))
        return await future


async def main():
    client = Redis(protocol=3)
    tasks = []
    for _ in range(5):
        async def task():
            message_id = str(uuid4())
            a = int(random()*10)
            b = int(random()*10)
            message = {
                "jsonrpc": "2.0",
                "id": message_id,
                "method": "add",
                "params": {
                    "a": a,
                    "b": b
                }
            }
            result = await rpc(client, message)
            print(f"{a} + {b} = {result}")

        tasks.append(asyncio.create_task(task()))
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass

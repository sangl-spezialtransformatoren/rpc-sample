import asyncio
import json

from openrpc import RPCServer
import redis.asyncio as redis
from redis.asyncio import Redis

title = "DemoServer"

rpc = RPCServer(title=title, version="1.0.0")


@rpc.method()
async def add(a: int, b: int) -> int:
    # await asyncio.sleep(1)
    return a + b


async def process_message(client: Redis, message: bytes | str):
    print("Message:", message)
    parsed_message = json.loads(message)
    message_id = parsed_message["id"]
    result = await rpc.process_request_async(data=message)
    await client.publish(channel=message_id, message=result)


async def main():
    client = redis.Redis(protocol=3)
    while True:
        _queue, message = await client.brpop(keys=[title], timeout=0)
        asyncio.create_task(process_message(client, message=message))


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

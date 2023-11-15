import asyncio
import json
from uuid import uuid4

from openrpc import RPCServer
import redis.asyncio as redis
from redis import ResponseError
from redis.asyncio import Redis

title = "DemoServer"
TTL = 60

rpc = RPCServer(title=title, version="1.0.0")


@rpc.method()
async def add(a: int, b: int) -> int:
    await asyncio.sleep(10)
    return a + b


async def process_message(client: Redis, stream_message_id: bytes | str, message: bytes | str):
    parsed_message = json.loads(message)
    message_id = parsed_message["id"]

    # Process openrpc message
    result = await rpc.process_request_async(data=message)

    # Use a transaction for returning the result
    pipeline = await client.pipeline(transaction=True)

    # Push result to a queue that expires after a TTL, in that time, the client must consume the result
    await pipeline.lpush(message_id, result)
    await pipeline.expire(name=message_id, time=TTL)

    # Acknowledge the task in the stream and delete it
    await pipeline.xack(title, title, stream_message_id)
    await pipeline.xdel(title, stream_message_id)

    # Commit transaction
    await pipeline.execute()


async def main():
    worker_id = str(uuid4())
    client = redis.Redis(protocol=3)

    # Create consumer group
    try:
        await client.xgroup_create(
            name=title,
            groupname=title,
            id=0,
            mkstream=True
        )
    except ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise e
    while True:
        # Check for stale messages
        response = await client.xautoclaim(
            name=title,
            groupname=title,
            consumername=worker_id,
            min_idle_time=60 * 1000,
            start_id=0,
            count=1
        )

        if len(response[1]) > 0:
            message_id = response[1][0][0]
            message = response[1][0][1][b'data']
            asyncio.create_task(process_message(client, stream_message_id=message_id, message=message))
            continue

        # Claim next message
        response = await client.xreadgroup(
            streams={title: '>'},
            groupname=title,
            consumername=worker_id,
            count=1,
            block=2000
        )
        if len(response) > 0:
            print(response)
            message_id = response[title.encode()][0][0][0]
            message = response[title.encode()][0][0][1][b'data']
            asyncio.create_task(process_message(client, stream_message_id=message_id, message=message))


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

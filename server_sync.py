import json
import time

from openrpc import RPCServer
import redis as redis
from redis import Redis

title = "DemoServer"

rpc = RPCServer(title=title, version="1.0.0")


@rpc.method()
def add(a: int, b: int) -> int:
    time.sleep(1)
    return a + b


def process_message(client: Redis, message: bytes | str):
    print("Message:", message)
    parsed_message = json.loads(message)
    message_id = parsed_message["id"]
    result = rpc.process_request(data=message)
    client.publish(channel=message_id, message=result)


if __name__ == "__main__":
    client = redis.Redis()
    while True:
        _queue, message = client.brpop(keys=[title], timeout=0)
        process_message(client, message=message)

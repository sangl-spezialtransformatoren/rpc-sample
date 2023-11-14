import json
from uuid import uuid4

from redis import Redis
from redis.client import PubSub

RPC_ID = "DemoServer"


def process_result(pubsub: PubSub):
    for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            try:
                return data["result"]
            except KeyError:
                raise Exception(data["error"]["message"])


def rpc(client: Redis, message: dict):
    with client.pubsub() as pubsub:
        pubsub.subscribe(message["id"])
        client.lpush(RPC_ID, json.dumps(message))
        return process_result(pubsub)


if __name__ == "__main__":
    client = Redis(protocol=3)
    for i in range(5):
        message_id = str(uuid4())
        message = {
            "jsonrpc": "2.0",
            "id": message_id,
            "method": "add",
            "params": {
                "a": 7,
                "b": 5
            }
        }
        result = rpc(client, message)
        print(result)

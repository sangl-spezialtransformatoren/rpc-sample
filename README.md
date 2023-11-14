# RPC Sample

Approach: Combine OpenRPC with redis queues/pub-sub as transport.

The client enqueues a JsonRPC message into a redis queue, named after the RPC function.
The worker listens to the queue and processes the request. The result is published to
a redis channel named after the message ID (-> use UUIDs!), which the client is subscribed to.

Advantages: By using OpenRPC, typed clients can be auto-generated in different languages. By using redis
as transport, the system is easily deployed distributed/with high availability.

Asynchronous *and* synchronous Redis clients are available, so the approach can be used for
async, sync and mixed codebases.

## Running the examples

A redis instance must be available, easily deployed with docker:

    docker run --name redis -p 6379:6379 -d redis/redis-stack:latest

## Resources

* Redis Queues and Pub/Sub https://redis.com/glossary/redis-queue/
* OpenRPC python library https://python-openrpc.burkard.cloud/
* OpenRPC client generator https://python-openrpc.burkard.cloud/generate_clients
* redis-py https://github.com/redis/redis-py
* JSON RPC https://www.jsonrpc.org/
* OpenRPC https://open-rpc.org/
# Caching Proxy

A CLI tool that starts a caching proxy server. It forwards requests to a real
origin server, caches the responses, and serves cached responses back on
repeat requests instead of hitting the origin again.

Built as a hands-on way to understand how HTTP caching actually works —
request forwarding, cache key design, and correctly handling both text and
binary response bodies.

## Features

- Start a proxy server on any port, pointed at any origin server
- Per-path + query-string cache keys (so `/products/1` and `/products/2`
  are cached separately, not collapsed into one entry)
- Redis-backed cache storage
- Correctly handles binary content (images, etc.) as well as JSON/text, by
  storing raw response bytes rather than decoded text
- `X-Cache: HIT` / `X-Cache: MISS` response header so you can see whether a
  response came from cache or the origin
- Clear the entire cache with a single command

## Requirements

- Python 3.9+
- A running Redis instance (default: `localhost:6379`)

## Setup

```bash
git clone <your-repo-url>
cd caching-proxy
python -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Make sure Redis is running locally before starting the proxy.

## Usage

Start the proxy server:

```bash
python main.py --port 3000 --origin http://dummyjson.com
```

This starts the caching proxy on `http://localhost:3000` and forwards
requests to `http://dummyjson.com`.

Example:

```bash
curl -i http://localhost:3000/products
```

First request → forwarded to the origin, cached, response includes:

```
X-Cache: MISS
```

Second request to the same path → served from cache:

```
X-Cache: HIT
```

Clear the cache:

```bash
python main.py --clear-cache
```

## Project Structure

```
caching-proxy/
├── main.py          # CLI entry point (argument parsing, starts server or clears cache)
├── server.py         # Flask app: request forwarding + caching logic
├── storage.py        # Redis connection/client
├── requirements.txt
└── README.md
```

## How it works

1. A request comes in to the proxy (e.g. `/products/1?category=phones`).
2. The full path + query string is used as the cache key, so distinct
   resources are cached separately.
3. If that key exists in Redis, the stored response bytes and content type
   are returned immediately, with `X-Cache: HIT`.
4. If not, the request is forwarded to the real origin server (including
   query parameters), the response body is stored as raw bytes (so it
   works for JSON, HTML, and binary content like images alike), and
   returned with `X-Cache: MISS`.

## What I learned

- The difference between storing a response as text vs. raw bytes, and why
  binary content (images) breaks if you don't use raw bytes
- Why a cache key needs to represent the *whole* requested resource
  (path + query string), not just the origin — an early version of this
  project cached everything under one key, so every request returned the
  same cached response regardless of what was actually asked for
- How to pass query parameters correctly when forwarding a request with
  `requests`, instead of building the URL as a raw string
- Basic Redis usage as an external cache store, and the storage
  trade-offs vs. an in-memory dict

## Next steps

- Cache expiry (TTL), so entries don't live forever
- Strip `Content-Encoding` / `Transfer-Encoding` headers before caching,
  to avoid re-serving a stale `gzip` header against already-decompressed
  content
- Handle non-GET methods and non-OK upstream responses more gracefully
- Optional: rebuild the listening layer using raw sockets instead of
  Flask, to understand what Flask abstracts away
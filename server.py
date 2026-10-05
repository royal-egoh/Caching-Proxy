from flask import Flask, jsonify, Response, request
import requests
import redis
from storage import storage

TTL_4_DAYS = 60 * 60 * 24 * 4


def start(url, port):
    app = Flask(__name__)

    @app.route('/')
    @app.route('/<path:path>')
    def proxy(path=''):
        cache_key = url + request.full_path
        cached_data = storage.hgetall(cache_key)
        if cached_data:
            print("Cache HIT", cache_key)
            raw_type = cached_data.get(b'content_type')
            raw = Response(cached_data[b'response.content'], status=200,
                           content_type=raw_type.decode())
            raw.headers['X-cache'] = 'HIT'
            return raw

        print("Cache MISS")
        try:
            response = requests.get(cache_key, timeout=5)
        except requests.exceptions.Timeout:
            return jsonify({
                "error": "The server took too long to respond.",
                "status": 504
            }), 504
        except requests.exceptions.RequestException:
            return jsonify({
                "error": "Network error occured.",
                "status": 500
            }), 500
        print("UPSTREAM:", cache_key)
        #!TEST
        print("PATH:", request.full_path)
        print("REQUEST.PATH:", request.path)
        print("PATH ARG:", path)

        if response.ok:
            raw = Response(response=response.content, status=response.status_code,
                           content_type=response.headers.get('Content-Type'))
            raw.headers['X-cache'] = 'MISS'
            storage.hset(cache_key, mapping={"response.content": response.content, "content_type": response.headers.get(
                'Content-Type', 'application/json; charset=utf-8')})
            storage.expire(cache_key, TTL_4_DAYS)
        return raw

    app.run(port=port, debug=True)

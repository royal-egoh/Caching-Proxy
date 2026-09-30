import requests, redis, argparse
from storage import storage
from server import start


# url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
# url='https://jsonplaceholder.typicode.com/posts/1'

def main():
    parser = argparse.ArgumentParser()


    parser.add_argument('--port', type=int, help="Port for server")
    parser.add_argument('--origin', type=str, help="URL to server")

    parser.add_argument('--clear-cache', action="store_true", help="Clear the cache")
    args = parser.parse_args()

    if args.port:
        port = args.port
        if args.origin:
            url = args.origin
            print(f"Server running on port: {port}, URL: {url}")
            start(url=url, port=port)
            

    if args.clear_cache:
        try:
            all_keys = storage.keys('*')
            storage.flushdb()
            print(f"<Cache cleared: {len(all_keys)} items cleared>")
        except Exception as e:
            print(f"An error occured: {e}")


if __name__ == "__main__":
    main()

import redis

storage = redis.Redis(host='localhost', port=6379)

all_keys = storage.keys('*')
# print(storage.hgetall('https://fastly.picsum.photos/id/0/5000/3333.jpg?hmac=_j6ghY5fCfSD6tvtcV74zXivkJSPIfR9B8w34XeQmvU').keys())
# print(all_keys)
# print(len(all_keys))
import redis

storage = redis.Redis(host='localhost', port=6379)

all_keys = storage.keys('*')
print(storage.keys())
# print(all_keys)
# print(len(all_keys))
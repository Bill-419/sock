import redis
import json

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def get_data_from_redis(key):
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None

def save_data_to_redis(key, data):
    delete_data_from_redis(key)  # 先删除原有的数据
    redis_client.set(key, json.dumps(data))

def delete_data_from_redis(key):
    redis_client.delete(key)

def get_data(key, table_name):
    from database import load_data  # 动态导入以避免循环依赖
    data = get_data_from_redis(key)
    if data:
        return data
    data = load_data(table_name)
    save_data_to_redis(key, data)
    return data

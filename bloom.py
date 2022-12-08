import redis

r = redis.Redis(host='192.168.1.245', port=6379, db=0)

r.bf.reserve(.001, 10)
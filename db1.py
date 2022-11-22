import redis
import pickle
import time

DBDATA = 'crawldata'
IDCOUNTER = 'crawlkey'

#connect to db
r = redis.Redis(host='192.168.1.245', port=6379, db=0)

#format of redis db
respones = r.hgetall(DBDATA) #{b'subdirectory': b'string', b'domain': b'string', b'parent': b'string', b'lastcrawl': b'time', b'scrapedata': b'pickle', b'parsed': b'int'}
print(respones)

#class for storing/manipulating data
class scrapedata:
    def __init__(self, domain, subdirectory, parent, html = None):
        self.subdirectory = subdirectory
        self.domain = domain
        self.parent = parent
        self.html = html
    #create db entry for this record
    def addtodb(self):
        key = DBDATA + ":" + str(r.incr(IDCOUNTER))
        r.hset(key, "domain", self.domain) 
        r.hset(key, "subdirectory", self.subdirectory)
        r.hset(key, "parent", self.parent)
        r.hset(key, "lastcrawl", time.ctime())
        r.hset(key, "scrapedata", pickle.dumps(self.html)) 
        r.hset(key, "parsed", 0)
        return key
    def __str__(self):
        return f"{self.domain}{self.subdirectory} from {self.parent}"

#proof of concept for pickling class
ex = scrapedata("www.example.com", "/wiki", "/home")
ex.html=[1,1,1,1,1,1]
print(ex)

mykey = ex.addtodb()
print(r.hgetall(mykey))



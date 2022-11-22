#crawldata = {'subdirectory': 'string', 'domain': 'string', 'html': 'html', 'parent': 'string', 'lastcrawl': 'time'}
#array = [1,2,3,4,5,6]

import redis
import pickle
import time

r = redis.Redis(host='192.168.1.245', port=6379, db=0)

#r.set('foo', 'bar')
#print(r.get('foo').decode())

#print(r.hgetall('data'))
#r.hset('data', 'hi', pickle.dumps(array))

respones = r.hgetall('data')['hi'.encode()]
print(pickle.loads(respones))

#class for storing/manipulating data
class scrapedata:
    def __init__(self, domain, subdirectory, parent, html = None):
        self.subdirectory = subdirectory
        self.domain = domain
        self.parent = parent
        self.html = html
    def __str__(self):
        return f"{self.domain}{self.subdirectory} from {self.parent}"

#proof of concept for pickling class
ex = scrapedata("www.example.com", "/wiki", "/home")
ex = pickle.dumps(ex)
ex = pickle.loads(ex)
print(ex) 
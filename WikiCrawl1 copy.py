from bs4 import BeautifulSoup
import requests
import pickle
import sys
import validators
import RabbitWrap
import redis
import time

TIMEOUT = 5                         #timeout(s) for requests
DBDATA = 'crawldata'                #name of db items ex: DBDATA:1
IDCOUNTER = 'crawlkey'              #key for the data counter in the db
DOMAIN = 'https://en.wikipedia.org' #domain being scanned

#connect to db
r = redis.Redis(host='192.168.1.245', port=6379, db=0)

#format of redis db
#respones = r.hgetall(DBDATA) #{b'subdirectory': b'string', b'domain': b'string', b'parent': b'string', b'lastcrawl': b'time', b'scrapedata': b'pickle', b'parsed': b'int'}

#class for storing/manipulating data
class scrapedata:
    #TODO load this object from the db as an option for initialiazation
    def __init__(self, domain, subdirectory, parent, html = None):
        self.subdirectory = subdirectory
        self.domain = domain
        self.parent = parent
        self.html = html
        self.nextsubdirectories = []
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
    def extractlinks(self):
        aTags = self.html.find_all('a')
        for string in aTags:
            newSubDir = string.get('href')        
            if newSubDir != None and validators.url(self.domain+newSubDir, True) == True and newSubDir.startswith('//') != True:
                self.nextsubdirectories.append(newSubDir)
    def __str__(self):
        return f"{self.domain}{self.subdirectory} from {self.parent}"

class crawler:
    def __init__(self, domain, subdirectory):
        self.domain = domain
        self.subdirectory = subdirectory
        self.start = domain+subdirectory
        self.parent = "start"
        self.response = requests.get(self.start, timeout=TIMEOUT)
        self.html = BeautifulSoup(self.response.text,'lxml')
        self.nextsubdirectories = []
        
    def extractlinks(self):
        aTags = self.html.find_all('a')
        for string in aTags:
            newSubDir = string.get('href')        
            if newSubDir != None and validators.url(self.domain+newSubDir, True) == True and newSubDir.startswith('//') != True:
                self.nextsubdirectories.append(newSubDir)
    def queuelinks(self):
        #TODO move Q to redis
        channel = RabbitWrap.connect()
        for subdirectory in self.nextsubdirectories:
            RabbitWrap.send(subdirectory, channel, self.domain)
        channel.close()
        print(f"Queued {len(self.nextsubdirectories)} links")

    def sendpagetodb(self):
        key = DBDATA + ":" + str(r.incr(IDCOUNTER))
        r.hset(key, "domain", self.domain) 
        r.hset(key, "subdirectory", self.subdirectory)
        r.hset(key, "parent", self.parent)
        r.hset(key, "lastcrawl", time.ctime())
        r.hset(key, "response", pickle.dumps(self.response)) 
        r.hset(key, "parsed", 0)
        print(f"Inserted {key} into the db")
        return key

#TODO move this into the class above
def processpage(subdirectory):
    print(f"Processing {DOMAIN}{subdirectory}")
    spider = crawler("https://en.wikipedia.org", subdirectory)
    spider.extractlinks()
    spider.queuelinks()
    spider.sendpagetodb()


def callback(ch, method, properties, body):
    subdir = body.decode()
    processpage(subdir)

    if (int(r.get(IDCOUNTER).decode()) > 1000):
        channel.stop_consuming()

if __name__ == "__main__":
    #processpage('/wiki/Mexico') #start page
    channel = RabbitWrap.connect()
    RabbitWrap.recieve(DOMAIN, channel, callback)
    channel.close()
    


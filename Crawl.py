from bs4 import BeautifulSoup
import requests
import pickle
import sys
import validators
import RabbitWrap
import redis
import time
from redisbloom.client import Client
import pika.exceptions

TIMEOUT = 5                         #timeout(s) for requests
DBDATA = 'crawldata'                #name of db items ex: DBDATA:1
IDCOUNTER = 'crawlkey'              #key for the data counter in the db
DOMAIN = 'https://en.wikipedia.org' #domain being scanned

#connect to db
r = redis.Redis(host='192.168.1.245', port=6379, db=0)
rb = Client(host='192.168.1.245')

#format of redis db
#respones = r.hgetall(DBDATA) #{b'subdirectory': b'string', b'domain': b'string', b'parent': b'string', b'lastcrawl': b'time', b'scrapedata': b'pickle', b'parsed': b'int'}

class crawler:
    def __init__(self, domain, subdirectory):
        self.domain = domain
        self.subdirectory = subdirectory
        self.start = domain+subdirectory
        self.parent = "start"
        self.nextsubdirectories = []
        self.trail = [subdirectory]
        if(self.request()):
            self.crawl()
            
    def crawl(self):
        if(self.onbloom() != 1):
            self.processpage()
            #self.navigate() #TODO figure out how to feed the next page into this method
        else:
            print(f"Already Processed {DOMAIN}{self.subdirectory}")
    
    def processpage(self):
            self.extractlinks() #TODO dont add links that are on the bloom filter to the Q
            self.queuelinks()
            self.addtobloom()
            self.sendpagetodb()

    def request(self):
        try:
            self.response = requests.get(self.start, timeout=TIMEOUT)
            self.html = BeautifulSoup(self.response.text,'lxml')
            return True
        except requests.exceptions.ReadTimeout:
            print("Request Timed Out!")
            return False
    
    def navigate(self, destination):
        self.parent = self.subdirectory
        self.trail.append(self.subdirectory)
        self.subdirectory = destination #put new subdir in as directory

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
    
    def addtobloom(self):
        return rb.bfAdd(DOMAIN, self.subdirectory)
    
    def onbloom(item):
        return rb.bfExists(DOMAIN, item)

#TODO move this into the class above
def processpage(subdirectory):
    if rb.bfExists(DOMAIN, subdirectory) != 1:
        print(f"Processing {DOMAIN}{subdirectory}")
        #TODO move crawler around instead of making a new crawler every page
        spider = crawler(DOMAIN, subdirectory)
        #spider.extractlinks() #TODO dont add links that are on the bloom filter to the Q
        #spider.queuelinks()
        #spider.addtobloom()
        #spider.sendpagetodb()
    else:
        print(f"Already Processed {DOMAIN}{subdirectory}")

def callback(ch, method, properties, body):
    subdirectory = body.decode()
    if spider == None:
        spider = crawler(DOMAIN, subdirectory)
    else:
        spider.navigate(subdirectory)
        spider.crawl()
    if (int(r.get(IDCOUNTER).decode()) > 100000):
        channel.stop_consuming()

if __name__ == "__main__":
    #processpage('/wiki/Mexico') #start page

    #opt 1
    #TODO create crawler
    #TODO call crawl method on first crawler manually
    #TODO tell navigate all other crawlers

    #opt2
    #TODO create a thread that manages the Q of a crawler
    #TODO add items to Q
    #TODO Have crawler pull items off the Q and visit those pages

    while(True):
        try:
            channel = RabbitWrap.connect()
            RabbitWrap.recieve(DOMAIN, channel, callback())
            channel.close()
        except pika.exceptions.StreamLostError:
            print("Connection Error!")
            print("Attempting to reconnect")
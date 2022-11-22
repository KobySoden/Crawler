import pickle
import sys
import WikiCrawl as crawl
import RabbitWrap
import pika


def callback(ch, method, properties, body):
    subdir = body.decode()
    crawl.main("")
    channel.stop_consuming()

if __name__ == "__main__":
    channel = RabbitWrap.connect()
    RabbitWrap.recieve('hello', channel, callback)
    channel.close()


#with open("data/"+'links.pickle', 'rb') as f:
    #data = pickle.load(f)
    #print(len(data))
    #print(data[0])
    #f.close()

#iterate through all links 
#fileSuffix = 0
#for i in data:
    #crawl.main(i[0], i[1], "links" + str(fileSuffix) + ".pickle")
    #fileSuffix +=1
    
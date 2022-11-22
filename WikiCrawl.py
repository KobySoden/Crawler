"""
This command line program takes a domain and a subdirectory in and prints out all the links on the page
and then saves them to a destination file specified
"""

from bs4 import BeautifulSoup
import requests
import pickle
import sys
import validators
import RabbitWrap

#domain = 'https://en.wikipedia.org'
#subdirectory = '/wiki/Mexico'

TIMEOUT = 5

"""
pass urls in and get the links on the page returned
"""
def GetLocalLinks(url, domain):
    #get html from webpage
    r=requests.get(url, timeout=TIMEOUT)
    html = BeautifulSoup(r.text,'lxml')

    print(html.head.title.text)

    aTags = html.find_all('a')

    output = []
    channel = RabbitWrap.connect()
    for string in aTags:
        newSubDir = string.get('href')
        
        #good link
        if newSubDir != None and validators.url(domain+newSubDir, True) == True and newSubDir.startswith('//') != True:
            #print(domain + newSubDir)

            #add newsubdir to Q named domain
            RabbitWrap.send(newSubDir, channel, domain)
            
    channel.close()
    return output

def main(domain, subdirectory, destination):
    
    url = domain+subdirectory
    links = GetLocalLinks(url, domain)

    with open("data/"+destination, 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(links, f, pickle.HIGHEST_PROTOCOL)
        print("Saved ",len(links), "links")
        f.close()
        
if __name__ == "__main__":
    #Checks for proper usage of the program
    if (len(sys.argv) < 4):
        print("\n\n______________________USAGE______________________________")
        print("WikiCrawl.py <domain> <subdirectory> <destination.pickle>\n")
        print("_____________________EXAMPLE_____________________________ \nWikiCrawl.py https://en.wikipedia.org /wiki/Mexico data.pickle\n\n")
        exit()

    domain = sys.argv[1]
    subdirectory = sys.argv[2]
    destination = sys.argv[3]

    main(domain, subdirectory, destination)




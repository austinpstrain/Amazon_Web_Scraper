#Read list of ip addresses from proxies.txt and find one that will return a request response 200 and a valid Amazon web page. get_soup returns soup object
#USE https://proxyscrape.com/free-proxy-list 
#SSL = yes. Anonymity = transparent

from bs4 import BeautifulSoup
import re # import Regular expression operations module
import requests
import random
import time

def firewallCheck(soup):
    try: 
        robotCheck = soup.find('p', attrs={'class' : 'a-last'})
        if "S" == robotCheck.text[0] and "address" == robotCheck.text[1]:
            print('Blocked by robot firewall \n"' + robotCheck.text+ '\"' )
            return False
        else:
            return True
    except:
        return True

def firewallCheck2(soup):
    try: 
        robotCheck = soup.find_all('img', alt=True)
        robotCheckText = robotCheck[1]['alt']
        if robotCheckText[0] == 'S' and robotCheckText[1] == 'o':
            print('Blocked by robot firewall \n\"' + robotCheckText+'\"')
            return False
        else:
            return True
    except:
        return True

def get_soup(url):
    IP = 'failed'
    while IP == 'failed':
        headers = { 
                'dnt': '1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'referer': 'https://www.amazon.com/',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }

        #Get random IP address from proxies.txt
        s=open("proxies.txt","r")
        m=s.readlines()
        l=[]
        for i in range(0,len(m)-1):
            x=m[i]
            z=len(x)
            a=x[:z-1]
            l.append(a)
        l.append(m[i+1])
        address=random.choice(l)
        print('\nChecking authenticaty of new proxy IP: https:'+address)
        s.close()
        proxies = {
            'https': address
            }
        try:
            s = requests.Session()
            a = requests.adapters.HTTPAdapter(max_retries=5)
            s.mount('http://', a)

            r = s.get(url, headers=headers, proxies=proxies, timeout=30)
            #self.__resp_obj__ = r
            
            print('HTTP Connection: ' , r) # print request to see if Response 200
            time.sleep(random.uniform(2.5,8)) #Wait between each request to avoid getting blocked
            soup = BeautifulSoup(r.content, "html.parser")
            if firewallCheck(soup) and firewallCheck2(soup):
                IP = address
            else:
                 IP = 'failed'
        except:
            IP = 'failed'
        if IP != 'failed':
            print('Authentication passed')
        else:
            print('Authentication failed')
    
    r.close()
    return soup

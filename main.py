#NOTES
'''
Amazon will block for searching more than 5 pages.
HTTP 500 status means that Amazon blocked request
Amazon returns can return a blank html to the beautiful soup web scrapper

'''

from bs4 import BeautifulSoup
import re # import Regular expression operations module
import requests
from time import gmtime, strftime
import csv
from scrape_page import *
import time
import random
from proxy_authenticator import *

mode = input("Append (a) data file or write (w) over existing file? (a/w): ")
if mode == 'w':
	check = input("Are you sure you want to overwrite the data file? (y/n): ")
	if check == 'n':
		mode = 'a'

url_str = input("Enter the product keyword to search for: ")

#Check to see if the keyword has already been used or not
if mode == 'w': #If writing to new data file, overwrite keywords.txt too.
	txt = open("keywords.txt","w")

txt = open("keywords.txt","r+")
lines = txt.readlines()
for line in lines:
    if url_str == line.replace("\n",""):
        print("This keyword has already been used!")
txt = open("keywords.txt",'a+')
txt.writelines(url_str+"\n")
txt.close()

pages = int(input("Number of pages of product results to search: "))

# Csv writing setup
filename = "products.csv"
f = open(filename, mode, encoding='utf-8')

#write headers of csv file
writer = csv.writer(f, lineterminator = '\n')
if mode == 'w':
    writer.writerow(['Items Scraped','Search Word','Product','ASIN','Brand','Category','Seller','Price','Image','Customer Images','URL','MPN','ISBN'])

url = []
words = url_str.split()
var = len(words)

if var == 1:
	url = "https://www.amazon.com/s/ref=nb_sb_noss_1?url=search-alias%3Daps&field-keywords=" + words[0]
if var == 2:
	url = "https://www.amazon.com/s/ref=nb_sb_noss_1?url=search-alias%3Daps&field-keywords=" + words[0] + "+" + words[1]
if var == 3:
	url = "https://www.amazon.com/s/ref=nb_sb_noss_1?url=search-alias%3Daps&field-keywords=" + words[0] + "+" + words[1] + "+" + words[2]
elif var == 4:
	url = "https://www.amazon.com/s/ref=nb_sb_noss_1?url=search-alias%3Daps&field-keywords=" + words[0] + "+" + words[1] + "+" + words[2] + "+" + words[3]

# Add header to avoid Amazon robot firewall
headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.com/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

maxPages = 'failed'
print('\n------------------------------\nRetreiving results from search\n------------------------------\n')
soup = get_soup(url)
maxPages = get_maxPages(soup)
while maxPages == 'failed':
	if maxPages == 'failed':
		soup = get_soup(url)
		maxPages = get_maxPages(soup)
	else:
		print('\n------------------------------\nFailed to return search results... Retrying\n------------------------------\n')


print('\n------------------------------\nTotal pages of results: ',maxPages,'\n------------------------------\n')
if pages > maxPages:
	pages = maxPages

with open("search_results.html", "w", encoding='utf-8') as file:
	file.write(str(soup))

#Get links of products based on search.
links = []
i = 0
exceptCount = 0
while i < pages:
	productDiv = soup.findAll('a', attrs = {'class':'a-link-normal a-text-normal'})
	for div in productDiv:
		try:
			link = div['href']
			links.append("https://www.amazon.com/"+link)
			check = True
		except:
			print("\n------------------------------\nFailed to retrieve Amazon product links\n------------------------------\n")
	if check == True:
		print('\n------------------------------\nProduct links succesfully collected from search page\n------------------------------\n')
	#Find the url link for the next page
	try:
		li = soup.find('li', attrs={'class','a-last'})
		if str(li) == 'None':
			print('\n------------------------------\nFailed to retrieve next page of search results... Retrying\n------------------------------\n')
			soup = get_soup(nextButtonURL)
			li = soup.find('li', attrs={'class','a-last'})
		else:
			nextButton = li.find('a')
			nextButtonURL = "https://www.amazon.com/"+nextButton['href']
			print('\n------------------------------\nSuccesfully retrieved next page of search results URL:', nextButtonURL,'\n------------------------------\n')
			i +=1
			exceptCount = 0
			soup = get_soup(nextButtonURL)
	except:
		print('\n------------------------------\nException: Error finding next button\n------------------------------\n')
		exceptCount += 1
		if exceptCount > 5:
			i += 1
			exceptCount = 0
	time.sleep(random.uniform(2.5,8)) #Wait between each request to avoid getting blocked
		

#Asin, Brand, UPC, EAN, MPN, and ISBN are listed differently each page
#Get data for each product
count = 0 #Count keeps track number of products scraped
for url in links:
	print('---------------------------------------')
	
	time.sleep(0.9 * random.random()) #Wait between each request to avoid getting blocked
	r = requests.get(url, headers=headers)
	soupy = BeautifulSoup(r.content, "html.parser")
	product = get_title(soupy)
	print('scraping product:', product)
	#If the product isn't parsing, retry
	if product == "None" or product == "N/A" or product == " ":
		print('Unable to retrieve product information... Retrying.')
		soupy = get_soup(url)
		product = get_title(soupy)
	if not product == "None" and not product == "N/A": 
		print('Succesfully retrived product data')
		count+=1
		asin = get_asin(soupy)
		brand = get_brand(soupy)
		description = get_description(soupy)
		category = get_category(soupy)
		seller = get_seller(soupy)
		price = get_price(soupy)
		image = get_image(soupy)
		isbn = get_isbn(soupy)
		mpn = get_mpn(soupy)
		customerImage = get_customerImage(soupy)

		try:
			writer.writerow([count,url_str,product,asin,brand,category,seller,price,image,customerImage,url,mpn,isbn])
		except:
			print('\nExcepetion: error writing to csv file, filed closed')
			f.close()
	else:
		print('Failed to retrieve product data')
		

f.close()

"""
       .__(.)< (MEOW)
        \___)   
 ~~~~~~~~~~~~~~~~~~
 """
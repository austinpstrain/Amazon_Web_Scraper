import requests
from urllib3.util import Retry
from requests.adapters import HTTPAdapter

import time
import re
from bs4 import BeautifulSoup
from time import localtime

def get_maxPages(soup):
    try:
        maxPages = soup.find_all('li', attrs={'class':'a-disabled'})
        maxPages = int(maxPages[1].text)
    except:
        maxPages = 'failed'
    return maxPages

def get_nextButtonURL(soup):
    try:
        li = soup.find('li', attrs={'class','a-last'})
        nextButton = li.find('a')
        nextButtonURL = "https://www.amazon.com/"+nextButton['href']
        print('\nNext pages URL:', nextButtonURL)
    except:
        print('\nException: Error finding next button\n')
        nextButtonURL = 'failed'
    try:
        if nextButtonURL == 'failed':
            li = soup.select('.a-last a')
            nextButton = li.find('a')
            nextButtonURL = "https://www.amazon.com/"+nextButton['href']
            print('\nNext pages URL:', nextButtonURL)
    except:
        print('\nException: Error finding next button\n')
        nextButtonURL = 'failed'
    return nextButtonURL

def get_title(soup):
    try:
        title = soup.find('span', attrs={'id':'productTitle'})
        title=title.text
        title = title.strip() 
    except:
        title = "N/A"
    try: #Attempt 2
        if title == "N/A":
            title = soup.find('div', attrs={'id' : 'titleSection'})
            title = title.text
            title = title.strip()
    except:
        title = "N/A"
    return title

def get_description(soup):
    try:
        description = soup.find('ul', attrs={'class':"a-unordered-list a-vertical a-spacing-mini"})
        description = description.text
        description = description.strip()
    except:
        return "N/A"
    return description

def get_brand(soup):
    try: #Attempt 1
        infoTable = soup.find('div', attrs={'class',"wrapper USlocale"})
        infoTable = infoTable.text
        infoTable = infoTable.strip() 
        infoTable = infoTable.replace(" ","")
        infoTable = re.sub(r'\n\s*\n','\n',infoTable,re.MULTILINE)
        Startbrand = infoTable.find('Manufacturer')
        if Startbrand == -1:    
            brand = "N/A"
        else:
            brand = infoTable[Startbrand+12:Startbrand+22]
            brand = brand.replace("\n","")
    except:
        brand = "N/A"
    try: #Attempt 2
        if brand == "N/A":
            infoTable = soup.find('div', attrs={'class':'a-row a-expander-container a-expander-inline-container'})
            infoTable = infoTable.text
            infoTable = infoTable.strip() 
            infoTable = infoTable.replace(" ","")
            infoTable = re.sub(r'\n\s*\n','\n',infoTable,re.MULTILINE)
            Startbrand = infoTable.find('Manufacturer')
            if Startbrand == -1:
                brand = "N/A"
            else:
                brand = infoTable[Startbrand+12:Startbrand+22]
                brand = brand.replace("\n","")
    except:
        brand = "N/A"
    try: #Attempt 3
        if brand == "N/A":
            infoTable = soup.select('#productDetails_techSpec_section_1 .a-size-base')
            results = [r.text.split('<span>')[0].strip() for r in infoTable]
            #print("RESULTS: ", results)
            index = 0
            for i in results:
                if i == "Manufacturer:" or i == "Manufacturer" or i == "Brand":
                    #print("Found brand: ", results[index+1])
                    brand = results[index+1]
                index += 1
    except:
        brand = "N/A"
    try: #Attempt 4
        if brand == "N/A":
            infoTable = soup.select('#productDetails_detailBullets_sections1 .a-size-base')
            results = [r.text.split('<span>')[0].strip() for r in infoTable]
            #print("RESULTS: ", results)
            index = 0
            for i in results:
                if i == "Manufacturer:" or i == "Manufacturer" or i == "Brand":
                    #print("Found brand: ", results[index+1])
                    brand = results[index+1]
                index += 1
    except:
        brand = "N/A"
    try: #Attempt 5
        if brand == "N/A":
            infoTable = soup.select("#productDetailsTable li")
            results = [r.text.split('<span>')[0].strip() for r in infoTable]
            index = 0
            for i in results:
                if "Manufacturer: " in i or "Brand: " in i:
                    #print("Found asin: ", i[6:])
                    brand = i[6:]
                index += 1
    except:
        brand == "N/A"
    try: #Attempt 6
        if brand == "N/A":
            infoTable = soup.select("#prodDetails .a-size-base")
            results = [r.text.split('<span>')[0].strip() for r in infoTable]
            index = 0
            #print(results)
            for i in results:
                if i == 'Brand' or i == 'Brand Name':
                    #print("Found brand: ", results[index+1])
                    brand = results[index+1]
                index += 1
    except:
        brand == "N/A"
    try: #Attempt 7
        if brand == "N/A":
            infoTable = soup.find('table', attrs={'id':'HLCXComparisonTable'})
            infoTable = infoTable.text
            infoTable = infoTable.strip() 
            infoTable = infoTable.replace(" ","")
            infoTable = re.sub(r'\n\s*\n','\n',infoTable,re.MULTILINE)
            Startbrand = infoTable.find('Manufacturer')
            if Startbrand == -1:
                brand = "N/A"
            else:
                brand = infoTable[Startbrand+12:Startbrand+22]
                brand = brand.replace("\n","")
    except:
        brand = "N/A"
    try:
        if brand == "N/A":
            brand = soup.find('a' , attrs={'id':'bylineInfo'})
            brand = brand.text.replace('Brand:','')
    except:
        brand = 'N/A'
    return brand

#Product info are either stored under "Product Details" or "Product Information"
def get_asin(soup):
    try: #Attempt 1
        #If there is an product information table
        infoTable = soup.find('div', attrs={'id':'productDetails_feature_div'})
        infoTable = infoTable.text
        infoTable = infoTable.strip() 
        infoTable = infoTable.replace(" ","")
        infoTable = re.sub(r'\n\s*\n','\n',infoTable,re.MULTILINE)

        Startasin = infoTable.find('ASIN')
        asin = infoTable[Startasin+4:Startasin+17]
        asin = asin.replace("\n","")
    except:
        asin = "N/A"
    try: #Attempt 2
        #Product info tables can have different html tags
        if asin == "N/A":
            infoTable = soup.find('div', attrs={'class',"wrapper USlocale"})
            infoTable=infoTable.text
            infoTable = infoTable.strip() 
            infoTable = infoTable.replace(" ","")
            infoTable = re.sub(r'\n\s*\n','\n',infoTable,re.MULTILINE)

            Startasin = infoTable.find('ASIN')
            asin = infoTable[Startasin+4:Startasin+17]
            asin = asin.replace("\n","")
            print("The second")
    except:
        asin = "N/A"
    try: #Attempt 3
        if asin == "N/A":
            infoTable = soup.select("#detailBullets_feature_div span")
            results = [r.text.split('<span>')[0].strip() for r in infoTable]
            #print("RESULTS: ", results)
            index = 0
            for i in results:
                if i == "ASIN:":
                    #print("Found asin: ", results[index+1])
                    asin = results[index+1]
                index += 1
    except:
        asin == "N/A"
    try: #Attempt 4
        if asin == "N/A":
            infoTable = soup.select("#productDetailsTable li")
            results = [r.text.split('<span>')[0].strip() for r in infoTable]
            index = 0
            for i in results:
                if "ASIN: " in i:
                    #print("Found asin: ", i[6:])
                    asin = i[6:]
                index += 1
    except:
        asin == "N/A"
    try: #Attempt 5
        if asin == "N/A":
            asin = soup.find('tr', attrs={'id' : 'detailsAsin'})
            asin = asin.text
            asin = asin.replace("ASIN","").replace("/n","").replace(" ","")
            asin = re.sub(r'\n\s*\n','\n',asin,re.MULTILINE)
    except:
        asin = "N/A"
    try:
        if asin == 'N/A':
            contents = soup.find_all('div', attrs={'class':'content'})
            for i in contents:
                i = str(i)
                Startasin = i.find('asin')
                if Startasin != -1:
                    asin = i[Startasin+5:Startasin+15]
    except:
        asin = 'N/A'
    try: #Attempt 6
        if asin == 'N/A':
            table = soup.find('table', attrs={'id':'productDetails_detailBullets_sections1'})
            print('TABLE: ', table)
            startAsin = table.find('ASIN')
            if startAsin != -1:
                asin = table[startAsin+5:startAsin+15]
                print('ASIN: ', asin)

    except:
        asin = 'N/A'

    return asin


def get_mpn(soup):
    try:
        infoTable = soup.find('div', attrs={'id':'productDetails_feature_div'})
        infoTable=infoTable.text
        infoTable = infoTable.strip() 
        infoTable = infoTable.replace(" ","")
        infoTable = re.sub(r'\n\s*\n','\n',infoTable,re.MULTILINE)
        StartMPN = infoTable.find('Itemmodelnumber')
        if StartMPN == -1:
            mpn = "N/A"
        else:
            mpn = infoTable[StartMPN+17:StartMPN+26]
            mpn = mpn.replace("\n","")
            return mpn
    except:
        mpn = "N/A"
    try:
        if mpn == "N/A":
            infoTable = soup.select("#detailBullets_feature_div span") #Using css in .select() method
            results = [r.text.split('<span>')[0].strip() for r in infoTable]
            index = 0
            for i in results:
                if i =="Item model number:":
                    mpn = results[index+1]
                else:
                    ""
                index += 1
    except:
        mpn = "N/A"
    return mpn

def get_isbn(soup):
    try: #Attempt 1
        infoTable = soup.find('div', attrs={'id':'productDetails_feature_div'})
        infoTable=infoTable.text
        infoTable = infoTable.strip() 
        infoTable = infoTable.replace(" ","")
        infoTable = re.sub(r'\n\s*\n','\n',infoTable,re.MULTILINE)
        Startisbn = infoTable.find('ISBN-13')
        if Startisbn == -1:
            isbn = "N/A"
        else:
            isbn = infoTable[Startisbn+7:Startisbn+20]
    except:
        isbn = "N/A"
    try: #Attempt 2
        if isbn == "N/A":
            infoTable = soup.find('div', attrs={'id':'detail-bullets'})
            infoTable = infoTable.text
            infoTable = infoTable.strip() 
            infoTable = infoTable.replace(" ","")
            infoTable = re.sub(r'\n\s*\n','\n',infoTable,re.MULTILINE)
            Startisbn = infoTable.find('ISBN:')
            if Startisbn == -1:
                isbn = "N/A"
            else:
                isbn = infoTable[Startisbn+5:Startisbn+16]
    except:
        isbn = "N/A"
    try: #Attempt 3
        if isbn == "N/A":
            infoTable = soup.find('div', attrs = {'id':'detail-bullets'})
            infoTable = infoTable.text
            infoTable = infoTable.strip() 
            infoTable = infoTable.replace(" ","")
            infoTable = re.sub(r'\n\s*\n','\n',infoTable,re.MULTILINE)
            Startisbn = infoTable.find('ISBN-13:')
            if Startisbn == -1:
                isbn = "N/A"
            else:
                isbn = infoTable[Startisbn+8:Startisbn+22]
    except:
        isbn = "N/A"
    return isbn

def get_category(soup):
    try:
        category = soup.find('ul', attrs={'class':'a-unordered-list a-horizontal a-size-small'})
        category= category.text
        category = category.strip()
        category = category.replace(" ","")
        category = re.sub(r'\n\s*\n','\n',category,re.MULTILINE)
        category.split("\n")
        
    except:
        return "N/A"
    return category

def get_seller(soup):
    try:
        seller = soup.find('a', attrs={'id':'bylineInfo'})
        seller=seller.text
        seller = seller.strip() 
    except:
        seller = "N/A"
    try: #attempt 2
        if seller == "N/A":
            div = soup.find('span', attrs ={ 'class' : 'author notFaded' })
            seller = div.find('span', attrs = {'class' : 'a-size-medium'})
            seller=seller.text
            seller = seller.strip() 
            seller = seller[:seller.find("(")-2]
    except:
        seller = "N/A"
    return seller

"""def get_condition(soup):
    try:
        condition = soup.find('a', attrs={'id':'bylineInfo'})
        condition=condition.text
        condition = condition.strip() 
    except:
        return "N/A"
    return condition"""

"""def get_location(soup):
    try:
        location = soup.find('span', attrs={'id':'productTitle'})
        location=location.text
        location = location.strip() 
    except:
        return "N/A"
    return location"""

def get_price(soup):
    try:
        price = soup.find('span', attrs={'id':'priceblock_ourprice'})
        price=price.text
        price = price.strip() 
        price = price[1:]
    except:
        price = "N/A"
    try:
        if price == "N/A":
            price = soup.find('span', attrs={'id':'priceblock_saleprice'})
            price=price.text
            price = price.strip() 
            price = price[1:]
    except:
        price = 'N/A'
    try:
        if price == 'N/A':
            price = soup.find('span', attrs={'id':'price'})
            price=price.text
            price = price.strip() 
            price = price[1:]
    except:
        price = 'N/A'
    return price

def get_image(soup):
    try:
        img = soup.find('ul', attrs={'class':'a-unordered-list a-nostyle a-horizontal list maintain-height'})
        im = str(img.find('img'))
        imageStart = im.find('https://')
        imageEnd = im.find('.jpg')
        image = im[imageStart:imageEnd+4]
    except:
        return "N/A"
    return image

def get_customerImage(soup):
    try:
        customerImages = [] 
        for images in soup.find_all('img', attrs={'alt':'Customer image'}):
            string = str(images)
            string.replace('[','').replace(']','')
            imageStart = string.find('src')+5
            imageEnd = string.find('width')-2
            image = string[imageStart:imageEnd]
            customerImages.append(image)
    except:
        customerImages = 'N/A'
    if not customerImages:
        customerImages = 'N/A'
    return customerImages

def get_payment(soup):
    try:
        title = soup.find('span', attrs={'id':'productTitle'})
        title=title.text
        title = title.strip() 
    except:
        return "N/A"
    return title

def get_upc(soup):
    try:
        title = soup.find('span', attrs={'id':'productTitle'})
        title=title.text
        title = title.strip() 
    except:
        return "N/A"
    return title

def get_ean(soup):
    try:
        title = soup.find('span', attrs={'id':'productTitle'})
        title=title.text
        title = title.strip() 
    except:
        return "N/A"
    return title


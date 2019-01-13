# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 14:39:14 2019

@author: Razer
"""

"""importing libraries"""
from bs4 import BeautifulSoup as bs
#import urllib.request #For Security reasons, we cannot use urllib.request 
import requests
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import numpy as np

"""Request a connection to the url and parse the url's html"""
headers = {'User-Agent':'Mozilla/5.0'}
url = 'https://theurge.com.au'
req = requests.get(url, headers=headers)
stores_soup = bs(req.text, "html.parser")


"""Get all <a></a> tags and save all of the href links of the Stores"""
stores_a_tags = stores_soup('a')
stores = []
for link in stores_a_tags:
    link = link.get('href', None)
    store = re.search('/store/.+\?gender-value=female', link)
    if store:
        store = link[store.start():store.end()]
        stores.append(store)


"""Use selenium webdriver to overcome continuously loading webpages"""
browser = webdriver.Chrome(r"C:\chromedriver\chromedriver.exe")


"""Loop in each stores"""
store_product_details = []
for curr_store_url in stores:
    browser.get(url + curr_store_url)
    
    """Press Page down key 20 times"""
    elem = browser.find_element_by_tag_name("body")
    no_of_pagedowns = 20
    while no_of_pagedowns:
        print(no_of_pagedowns)
        elem.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.2)
        no_of_pagedowns-=1
    
    """Get all the links of the products of the current store"""
    ea_product_soup = bs(browser.page_source, "html.parser")
    products_a_tags = ea_product_soup('a')
    products_links = []
    for link in products_a_tags:
        link = link.get('href')
        filtered_product_link = re.match("/s/.+/.+/.+", link)
        if filtered_product_link:
            products_links.append(link)

    """Loops on each product links, and scrape for the 
    details that we are interested in.
    In this case we choose the Brand, Name, Price, 
    Specific product details, Delivery, Returns, 
    Payment, and the Source URL of the product"""
    temp_product_details = []
    for link in products_links[:10]:
        browser.get("https://theurge.com.au" + link)
        single_product_soup = bs(browser.page_source, "html.parser")
        single_product = single_product_soup.find("div", class_="single-product")
        
        if single_product == None:
            continue
        
        single_product_details = single_product.find("div", "single-product_content product-content")
        
        """Scrape all the details using its tag and class.
           I used regex here for cleaning the data."""
        product_brand = single_product_details.find("h2", "product_content_brand").text
        product_name = single_product_details.find("h1", "product_content_name").text
        product_name = re.sub("(?i)" + product_brand, "", product_name).strip()
        product_price = single_product_details.find("span", "product_content_price price").text
        product_price = re.findall("\$\d+\.*\d+", product_price)[-1]
        product_extended_details = single_product_details.find_all("div", "single-product_extended-details")
        product_delivery_returns_payment = product_extended_details[0].text
        product_details = product_extended_details[1].text
        product_tag = single_product_details.find("span", "product_content_store").text.replace("from", "")
        product_source_link = single_product_details.find("a", "single-product_button buy-now").get('href')
        product_source_link = product_source_link.replace("%2F", "/").replace("%3A", ":")
        
        """Append all details to a temp list"""
        temp_product_details.append(product_tag.strip())
        temp_product_details.append(product_name.strip())
        temp_product_details.append(product_price.strip())
        temp_product_details.append(product_delivery_returns_payment.strip())
        temp_product_details.append(product_details.strip())
        temp_product_details.append(product_source_link.strip())
    
    """Make a dataframe of All of the Product's details of the Current Store"""
    product_details = np.array(temp_product_details)
    product_details = product_details.reshape((int(len(product_details)/6) ,6))
    product_columns = ["Product Brand", "Product Name", "Product Price",
                       "Product Delivery, Returns, Payment", "Product Details", "Product Source"]
    product_df = pd.DataFrame(product_details, columns = product_columns)
    store_product_details.append(product_df)

"""Save all of the Store's Product Details into an excel file.
   We will use our excel file later for comparing the Source(ie. Cotton On) product details
   and The Urge product details """
writer = pd.ExcelWriter('{0}.xlsx'.format("The Urge"), engine='xlsxwriter')
result = pd.concat(store_product_details)
result.reset_index(inplace = True)
result.drop(result.columns[0], axis=1, inplace=True)
empty_details = result[result['Product Details'] == "\n\n"]
result.to_excel(writer, index=False)
writer.save()

"""Close webddriver"""
browser.close()

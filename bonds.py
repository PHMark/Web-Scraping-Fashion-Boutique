# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 17:25:15 2019

@author: Razer
"""

from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import numpy as np
import re
from difflib import Differ


"""Some variable for our requests"""
headers = {'User-Agent':'Mozilla/5.0'}
url = 'https://theurge.com.au'

"""Create a dataframe from our excel(Created on the-urge.py)
   This dataframe contains all of the Bonds's
   product details in the urge website"""
source_url_df = pd.read_excel("The Urge.xlsx")
bonds_url_df = (source_url_df[(source_url_df['Product Brand'] == 'Bonds')])


"""Get all the Product Source(Link) of Bonds's products"""
product_url = list(bonds_url_df['Product Source'].values)


"""Get the Name, Price, and Description of the Bonds's product on it's website.
   Here, I assumed that that the delivery, returns, and payment details are common
   for all the products in the Bonds's website"""
source_product_details = []
for i, url in enumerate(product_url):
    print("["+str(i)+"] Scraping: " + url + " ...")
    req = requests.get(url, headers=headers)
    soup = bs(req.text, "html.parser")
    
    """Scrape all the details using a tag with its class.
           I also used regex here for cleaning the data."""
    product_name = soup.find("div", class_="product-name").text.strip()
    product_price = soup.find("span", class_="price").text.strip()
    product_description = soup.find("div", "product-description").text.strip()
    product_description = product_description.replace("•", " ")
    product_description = re.sub("( )+", " ", product_description).replace(" ,", ",")
    product_description = re.sub("(\s)+", " ", product_description)
    
    """Append the details on a list"""
    source_product_details.append(product_name)
    source_product_details.append(product_price)
    source_product_details.append(product_description)
    source_product_details.append(url)    


"""Create a dataframe of the product's details"""
source_product_details = np.array(source_product_details)
source_product_details.resize((int(source_product_details.shape[0]/4), 4))
columns = ['Product Name', 'Product Price', 'Product Details', 'Product Source']
source_product_df = pd.DataFrame(source_product_details, columns = columns)


"""Compare the urge's details and the source's details.
   I didn't include the Product Name in comparing the 2 dataframe
   because of it's pattern."""
theurge_product_df = bonds_url_df[columns].reset_index()
theurge_product_df.drop(theurge_product_df.columns[0], axis=1, inplace=True)
theurge_product_df['Product Details'] = theurge_product_df['Product Details'].str.strip()
truth_df = theurge_product_df == source_product_df



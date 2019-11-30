import csv
import requests
import os
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup


# Specify URl and download the HTML source using requests
url = 'https://www.waves.com/bundles#sort:path~type~order=.hidden-price~number~asc|views:view=grid-view|paging:currentPage=0|paging:number=all'
r = requests.get(url, allow_redirects=True)

# Write the HTML source to a text file
with open('waves_plugins.html', 'wb') as webpage:
    webpage.write(r.content)  

# Open the HTML file and create a new BeautifulSoup object
with open('waves_plugins.html', encoding='utf8') as html_file:
    soup = BeautifulSoup(html_file, 'lxml')

# Remove the HTML file
os.remove("waves_plugins.html")



# Check whether the csv of exists first. 
if os.path.isfile('waves_price_history_bundles.csv') != True:
    
    with open('waves_price_history_bundles.csv', 'a', newline='', encoding='utf-8') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(["date", "product_id", "product_title", "regular_price", "sale_price", "coupon_price"])


# Function for formatting the raw HTML containing prices
def formatter(price_html):
    if price_html != None:

        if str(price_html).count("$") > 0:
            price_html = str(price_html).split("$")[1]
        
            if price_html.count("sup") > 0:
                price_html = price_html.split("<sup>")
                dollar = [s for s in price_html[0] if s.isnumeric() == True]
                dollar = "".join(dollar)
                cents = [s for s in price_html[1] if s.isnumeric() == True]
                cents = "".join(cents)
                price_html = dollar + "." + cents
            else:
                price_html = [s for s in price_html if s.isnumeric() == True]
                price_html = "".join(price_html)
                price_html = price_html + ".00"
        else:
            price_html = "NaN"
    
    else:
        price_html = "NaN"
    
    return price_html


# Create a dictionary 
new_prices_dict = {}

for product in soup.find_all('article'):
    
    product_id = product['id']
    
    product_title = product.find('p', class_='title').get_text(strip=True)
    
    # 
    regular_price = formatter(product.find('div', class_='regular-price align-center'))
    sale_price = formatter(product.find('div', class_='on-sale-price align-center'))
    coupon_price = formatter(product.find('div', class_='with-coupon align-center'))

    entry = [datetime.now().date(), product_id, product_title, regular_price, sale_price, coupon_price]
    
    new_prices_dict[product_id] = entry

    
# make a dictionary with the most recent price recorded for each unique product_id
old_prices_dict = {}

with open('waves_price_history_bundles.csv', 'r', newline='', encoding='utf-8') as csvfile:
    csvfile = csv.reader(csvfile, delimiter=' ', quotechar='|')

    for row in csvfile:
        old_prices_dict[row[1]] = row 



# Create a new dictionary that holds an entry for any product which has as a price change
# Or is a new product that doesnt already exist in the csv
changed_prices = {}

for key in new_prices_dict:
    
    if key in old_prices_dict:
        if new_prices_dict[key][1:] != old_prices_dict[key][1:]:
            changed_prices[key] = new_prices_dict[key]
    
    if key not in old_prices_dict:
        changed_prices[key] = new_prices_dict[key]
        

# Write these changed prices and new products to the csv file.
for key in changed_prices:
    
    with open('waves_price_history_bundles.csv', 'a', newline='', encoding='utf-8') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_ALL)
        spamwriter.writerow(changed_prices[key])
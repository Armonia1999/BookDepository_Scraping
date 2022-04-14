import requests
from bs4 import BeautifulSoup
import pandas as pd

base_url = 'https://www.bookdepository.com/bestsellers'

all_urls = []
for i in range(1,5):
    all_urls.append(base_url + f"?page={i}")
    
# now lets build functions to get the work done.

def get_titles(doc): 
    titles = []
    title_tags = doc.find_all('h3', class_='title')
    titles = [title.text.strip() for title in title_tags]
    return titles


def get_authors(doc):
    authors  = []
    author_tags = doc.find_all('p', class_='author')
    authors = [author.text.strip() for author in author_tags]
    return authors


def get_publish_dates(doc):
    dates = []
    date_tags = doc.find_all('p', class_='published')
    dates = [date.text.strip() for date in date_tags]
    return dates


def get_prices(doc):
    prices = []
    price_tags = doc.find_all('div', class_='price-wrap')  # we use the price wrap and not price because not all books have it.
    prices = [price.text.strip() for price in price_tags]
    return prices 


def get_ISBN(doc):
    ISBN = []
    ISBN_tags = doc.find_all('a', {'itemprop': 'url'})
    for isbn in ISBN_tags:
        ISBN.append(isbn['href'][-13:])
    return ISBN


# Big function to cover all:

def Scrape(url):
    
    response = requests.get(url)
    doc = BeautifulSoup(response.content, 'html.parser')
    
    titles = get_titles(doc)
    authors = get_authors(doc)
    dates = get_publish_dates(doc)
    prices = get_prices(doc)
    ISBN = get_ISBN(doc)
    
    scrape_dict = {
        'Book Title': titles,
        'Author': authors,
        'Publish Date': dates,
        'Price': prices,
        'ISBN 13': ISBN
    }
    
    df = pd.DataFrame(scrape_dict)
    return df


total = [Scrape(all_urls[0]), Scrape(all_urls[1]), Scrape(all_urls[2]), Scrape(all_urls[3])]
total_df= pd.concat(total)

def fix_price(x):
    if len(x) == 0:
        return 0
    else:
        try:
            index_backslash = x.index("\\")
        except:
            return float(x.split('₪')[1])
        else: 
            first_str = x.split('₪')[1]    # you can replace with whatever currency your browser displays.
            return float(first_str[:index_backslash])    


total_df['Price'] = total_df['Price'].apply(fix_price)

# now we convert to a csv file. keep in mind we have 120 books in this DataFrame so let's omit the last 20 rows.
# the file will be created and saved in the same directory.
total_df[:100].to_csv('Top 100 Bestsellers.csv', index=False)
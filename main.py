#!/usr/bin/env python3
from bs4 import BeautifulSoup
import time
driver = __import__('driver').driver


def get_prod_links(link, driver):
    # Navigate to the page
    driver.get(link)

    # Wait for the page to load
    time.sleep(5)

    page_source = driver.page_source

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html5lib')
    products = soup.findAll('div', attrs={'class':'s-product-card-image'})

    prodlinks = []
    for product in products:
        prodlinks.append(product.a['href'])

    return prodlinks



def get_description(description_div):
    description_content = []

    # Extract text content
    for p in description_div.findAll('p'):
        text = p.text
        if text:
            description_content.append(text)

    # Extract image URLs
    for img in description_div.findAll('img'):
        description_content.append(img['src'])

    return ' '.join(description_content)


def get_prod_info(prodlinks, driver):
    products = []
    for i, p in enumerate(prodlinks):
        pid = p.split('/')[-1].lstrip('p')
        driver.get(p)
        time.sleep(5)
        ps = driver.page_source
        psoup = BeautifulSoup(ps, 'html5lib')
        products.append({})
        p = products[i]
        p['name'] = psoup.find('h1').text.strip()
        p['price'] = psoup.find('h2', attrs={'class':'total-price font-bold text-xl inline-block'}).text
        p['price'] = p['price'].strip().split(' ')[0]

        # Extract all picture links
        image_div = psoup.findAll('a', attrs={'data-fslightbox':"product_" + pid})
        image_urls = [img['href'] for img in image_div]
        p['images'] = ','.join(image_urls)

        # Extract classifications
        breadcrumb_div = psoup.find('salla-breadcrumb')
        classifications = ' > '.join([item.text.strip() for item in breadcrumb_div.findAll('li', attrs={'class': 's-breadcrumb-item'})])
        p['classifications'] = classifications

        # Extract description
        description_div = psoup.find('div', attrs={'class': 'product__description'})
        desc = get_description(description_div)
        p['description'] =  desc if desc else 'لا يوجد وصف'

    return products

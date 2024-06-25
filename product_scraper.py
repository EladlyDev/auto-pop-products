#!/usr/bin/env python3
from bs4 import BeautifulSoup
import openpyxl
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import typing
import time
from random import randrange
from typing import List, Dict


class ProductScraper:
    prods_group: List[str] = []
    prods_links: List[str] = []
    categories: Dict = {}
    prods_info: List[Dict] = []

    def __init__(self, driver):
        self.driver = driver

    def add_links(self, link):
        if isinstance(link, str):
            self.prods_group.append(link)
        elif isinstance(link, list):
            self.prods_group.extend(link)

    def get_prod_links(self):
        assert self.prods_group, 'No links to scrape'

        for link in self.prods_group:
            # Wait for the page to load
            while True:
                self.driver.get(link)

                try:
                    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 's-product-card-image')))
                except Exception as e:
                    print(e)
                    continue
                break

            page_source = self.driver.page_source

            # Parse the page source with BeautifulSoup
            soup = BeautifulSoup(page_source, 'html5lib')
            products = soup.findAll('div', attrs={'class': 's-product-card-image'})

            for product in products:
                self.prods_links.append(product.a['href'])

        return self.prods_links

    def get_description(self, description_div):
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

    def update_categories(self, classifications):
        for i, c in enumerate(classifications):
            if c not in self.categories:
                self.categories[c] = []
            if i < len(classifications) - 1:
                if classifications[i+1] not in self.categories[c]:
                    self.categories[c].append(classifications[i+1])

    def get_prod_info(self):
        for i, p in enumerate(self.prods_links):
            pid = p.split('/')[-1].lstrip('p')
            
            while True:
                self.driver.get(p)

                try:
                    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 's-breadcrumb-item')))
                except Exception as e:
                    print(e)
                    continue
                break
                
            ps = self.driver.page_source
            psoup = BeautifulSoup(ps, 'html5lib')
            self.prods_info.append({})
            product = self.prods_info[i]
            product['name'] = psoup.find('h1').text.strip()
            product['price'] = psoup.find('h2', attrs={'class': 'total-price font-bold text-xl inline-block'}).text.strip().split(' ')[0]

            # Extract all picture links
            image_div = psoup.findAll('a', attrs={'data-fslightbox': "product_" + pid})
            image_urls = [img['href'] for img in image_div]
            product['images'] = ','.join(image_urls)

            # Extract classifications
            breadcrumb_div = psoup.find('salla-breadcrumb')
            breadcrumb_items = breadcrumb_div.findAll('li', attrs={'class': 's-breadcrumb-item'})
            classifications = [item.text.strip() for item in breadcrumb_items[1:-1]]  # Exclude the last item
            product['classifications'] = ' > '.join(classifications)
            self.update_categories(classifications)

            # Extract description
            description_div = psoup.find('div', attrs={'class': 'product__description'})
            desc = self.get_description(description_div)
            product['description'] = desc if desc else 'لا يوجد وصف'

        return self.prods_info

    def export_categories(self, filename='sct.xlsx'):
        wb = openpyxl.load_workbook(filename)
        ws = wb.active

        appended = []
        for c in self.categories:
            if c not in appended:
                ws.append([c, 'لا', '', 'لا', 'لا', 'لا'])
            appended.append(c)
            for sc in self.categories[c]:
                if sc not in appended:
                    ws.append([sc, 'نعم', c, 'لا', 'لا', 'لا'])
                    appended.append(sc)

        # out = "c-" + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.xlsx'
        wb.save('c.xlsx')

    def export_to_excel(self, filename='spt.xlsx'):
        assert self.prods_info, 'No products to export'

        wb = openpyxl.load_workbook(filename)
        ws = wb.active  # Get the active worksheet

        # Append product values to the worksheet
        for p in self.prods_info:
            ws.append(['منتج', p['name'], p['classifications'], p['images'], 'منتج جاهز', p['price'], p['description'], 'نعم'])

        # out = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.xlsx'
        wb.save('p.xlsx')
        self.export_categories()

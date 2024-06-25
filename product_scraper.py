import requests
import validators
import typing
from typing import List
import json
import openpyxl
import datetime
from os.path import exists


class ProductScraper:
    API_URL: str = "https://api.salla.dev/store/v1/products?source=categories&filterable=1&source_value[]="
    prod_links: List[str] = []
    scrapped_data: List[dict] = []
    categories: List[str] = []

    def _extract_id(self, url):
        return url.split('/')[-1].replace('c', '')

    def add_links(self, url):
        if (isinstance(url, str) and validators.url(url)):
            id = self._extract_id(url)
            if (id not in self.prod_links):
                self.prod_links.append(id)
        elif (isinstance(url, list)):
            self.prod_links.extend([self._extract_id(link) for link in url if validators.url(link) and link not in self.prod_links])
        else:
            raise ValueError("Invalid URL")

    def get_links(self):
        return self.prod_links

    def scrape(self):
        assert len(self.prod_links) > 0, "No links to scrape"
        for link in self.prod_links:
            response = requests.get(self.API_URL + link, headers={'store-identifier': '1439319247'}) # hard coded for now
            if response.status_code == 200:
                self.scrapped_data.extend(response.json()['data'])
            else:
                print("Failed to fetch data")

    def export(self, p_template: str = 'spt.xlsx', c_template: str = 'sct.xlsx',
                p_output: str = f"p-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx",
                c_output: str = f"c-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"):
        assert len(self.scrapped_data) > 0, "No data to export"
        assert exists(p_template), "Product template file not found"
        assert exists(c_template), "Category template file not found"

        p_wb = openpyxl.load_workbook(p_template)
        p_ws = p_wb.active
        c_wb = openpyxl.load_workbook(c_template)
        c_ws = c_wb.active

        for p in self.scrapped_data:
            p_ws.append(['منتج', p['name'], p['category']['name'], p['image']['url'], 'منتج جاهز', p['price'], p['description'], 'نعم'])
            if p['category']['name'] not in self.categories:
                self.categories.append(p['category']['name'])
                c_ws.append([p['category']['name'], 'لا', '', 'لا', 'لا', 'لا'])

        p_wb.save(p_output)
        c_wb.save(c_output)

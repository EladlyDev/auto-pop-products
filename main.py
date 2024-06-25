#!/usr/bin/env python3
import cmd
from product_scraper import ProductScraper
driver = __import__('driver').driver


class ProductScraperShell(cmd.Cmd):
    intro = 'Welcome to the Product Scraper shell. Type help or ? to list commands.\n'
    prompt = 'product_scraper> '
    scraper = ProductScraper(driver)

    def do_add_links(self, arg):
        'Add links to scrape: add_links <link1> <link2> ...'
        if (not arg):
            print('USAGE: add_links <link1> <link2> ...')
            return
        links = arg.split()[1:]
        self.scraper.add_links(links)
        print(f'Links: {links} added')

    def do_scrape(self, arg):
        'Scrape product information: scrape'
        if (not self.scraper.prods_group):
            print("Please use add_links to add links first.")
            return
        print('Scraping... this might take a while...')
        self.scraper.get_prod_links()
        print('Got the links for each product... almost done...')
        self.scraper.get_prod_info()
        print('Product information scraped')

    def do_export(self, arg):
        'Export product information to a file: export'
        try:
            self.scraper.export_to_excel()
        except Exception as e:
            print(e)
            return
        print(f'Product information exported.')

    def do_clear(self, arg):
        'Clear the product links: clear'
        self.scraper.prods_group = []
        print('Product links cleared.')

    def do_exit(self, arg):
        'Exit the shell: exit'
        print('\nBye')
        driver.quit()
        return True

    def do_quit(self, arg):
        'Quit the shell: quit'
        return self.do_exit(arg)

    def do_EOF(self, arg):
        'Exit the shell: EOF'
        print('\nBye')
        driver.quit()
        return True


if __name__ == '__main__':
    app = ProductScraperShell()
    app.cmdloop()

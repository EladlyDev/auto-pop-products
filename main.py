import cmd
from product_scraper import ProductScraper


class ProductScraperShell(cmd.Cmd):
    intro = 'Welcome to the Product Scraper shell. Type help or ? to list commands.\n'
    prompt = 'product_scraper> '

    def __init__(self):
        super().__init__()
        self.scraper = ProductScraper()


    def do_add_links(self, arg):
        'Add product links to scrape. Usage: add_links <link1> <link2> ...'
        try:
            self.scraper.add_links(arg.split())
        except ValueError as e:
            print(e)
            return

    def do_get_links(self, arg):
        'Get the links to scrape. Usage: get_links'
        print(self.scraper.get_links())

    def do_scrape(self, arg):
        'Scrape the links. Usage: scrape'
        try:
            self.scraper.scrape()
        except Exception as e:
            print(e)
            return

    def do_export(self, arg):
        'Export the scraped data. Usage: export'
        try:
            self.scraper.export()
        except Exception as e:
            print(e)
            return

    def do_exit(self, arg):
        'Exit the shell. Usage: exit'
        return True


if __name__ == '__main__':
    ProductScraperShell().cmdloop()

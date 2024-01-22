"""
QuotesScraper
---------

Scaper for extracting quotes from  http://quotes.toscrape.com/js/
This module uses selenium as the headless browser
"""
import json
import logging
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

logging.basicConfig(filename="quotes_scraper.log",
                filemode='w',
                format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                datefmt='%H:%M:%S',
                level=logging.INFO)


class QuotesScraper:
    """
    Scaper for extracting quotes using selenium as the headless browser.

    Parameters
    ----------
    is_dump : boolean,
        Choose whether to save pages visited

    Attributes
    ----------
    driver: selenium.webdriver.chrome.webdriver.WebDriver
        Selenium driver object used to visit the required pages.

    result : list
        Result of the scraped data.

    res_file : str
        Name of the result file

    logger : logging.Logger
        Logger object used in all methods.

    Methods
    -------
    scrape ()
        Main method to scrape the quotes pages.

    save_page(contents, curr_url)
        Save page of the givent contents.

    parse_quotes_page(contents)
        Parse a single page containing various quotes.

    parse_quote_div(quote_div)
        Parse a single div containg single quote.

    quit()
        Quit the driver.

    """
    def __init__(self, is_dump=False):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "\
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0"\
                    " Safari/537.36"
        chrome_options.add_argument(f'--user-agent={user_agent}')

        self.driver = webdriver.Chrome(options=chrome_options)

        self.is_dump = is_dump
        self.result = []
        self.res_file = "quotes.json"
        self.logger = logging.getLogger('quotes_scraper')

    def scrape(self):
        """
        This functions visits the home page : http://quotes.toscrape.com/js/
        and parses the quotes present.

        If a next page link is present, the page is visited and parsed as well.

        After parsing all available pages, the results are stored in file : quotes.json
        """
        self.driver.set_window_size(1920, 1080)

        self.driver.get("http://quotes.toscrape.com/js/")

        next_element = None

        while True:
            self.parse_quotes_page(self.driver.page_source)

            try:
                next_element = self.driver.find_element(By.LINK_TEXT, "Next →")
            except NoSuchElementException:
                self.logger.info("Next element not found. Finishing execution.")
                break

            next_element.click()

        self.logger.info(f"Saving resuls in file : {self.res_file}")
        with open(self.res_file, "w", encoding="UTF-8") as f:
            json.dump(self.result, f, indent=4, ensure_ascii=False)


    def save_page(self, contents, curr_url):
        """
        This function saves contents in "data_dumps" directory.
        If "data_dumps" directory is not present in current directory, it is created.
        This function is called when self.is_dump = True.
        """
        page_name = "_".join(curr_url.split("/")[-2:])

        data_dumps_dir = os.path.join(os.getcwd(), "data_dumps")
        if not os.path.exists(data_dumps_dir):
            self.logger.info("Creating data_dumps directory.")
            os.mkdir(data_dumps_dir)

        fname = os.path.join(data_dumps_dir, page_name+".html")
        self.logger.info(f"is_dump=True, saving file: {fname}" +
                       f" for response of url: {curr_url}")

        with open(fname, "w", encoding="UTF-8") as f:
            f.write(contents)

    def parse_quotes_page(self, contents):
        """
        Parse all quotes from a single page and append the result in self.result.
        """
        curr_url = self.driver.current_url

        self.logger.info(f"Parsing quotes for url : {curr_url}")

        if self.is_dump:
            self.save_page(contents, curr_url)

        soup = BeautifulSoup(contents, 'html.parser')

        quote_divs = soup.find_all("div", attrs={"class": "quote"})

        for quote_div in quote_divs:
            quote_details = self.parse_quote_div(quote_div)
            self.result.append(quote_details)


    def parse_quote_div(self, quote_div):
        """
        Parse a div containing single quote.
        Extract "quote", "author", "tags" and return as a dictionary.
        """
        quote = quote_div.span.text
        author = quote_div.small.text
        tags = [anchor.text for anchor in quote_div.find_all("a", attrs={"class": "tag"})]

        quote_details = {
                "quote": quote,
                "author": author,
                "tags": tags
                }

        return quote_details

    def quit(self):
        """
        Quit the driver.
        """
        self.driver.quit()

if __name__ == "__main__":
    quotes_scraper = QuotesScraper(is_dump=True)

    quotes_scraper.scrape()

    quotes_scraper.quit()

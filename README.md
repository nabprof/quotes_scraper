Scaper for extracting quotes from  http://quotes.toscrape.com/js/
This module uses selenium as the headless browser.

Installing Dependencies:

    pip install selenium
    pip install beautifulsoup4

Running the scraper:

    python quotes_scraper.py 

The result will be stored in file: quotes.json

In order to specify whether to save the dumps, use 'is_dump' parameter for QuotesScraper constructor.

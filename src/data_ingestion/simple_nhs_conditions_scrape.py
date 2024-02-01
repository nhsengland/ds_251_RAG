from dotenv import load_dotenv
import os
import json
import datetime
import dateutil.parser
from io import StringIO
import io

import scrapy

from src.data_ingestion.corpus.items import HTMLItem

load_dotenv(".secrets")
os.environ["NHS_API_KEY"] = os.getenv("nhs_api_key")

class ItemQueue:
    """This class is used to make sure the Items are ordered by the documents' modification time."""
    def __init__(self):
        self.start_pos = 0
        self.queue = []
        self.size = 0
        self.next_page_url = None

    def put(self, idx, item):
        idx -= self.start_pos
        if idx < 0:
            raise Exception("Item has already been processed")
        if idx >= len(self.queue):
            self.queue.extend([None] * (idx - len(self.queue) + 1))
        if self.queue[idx] is not None:
            raise Exception("Item is already set")
        self.queue[idx] = item

    def poll(self):
        while self.queue and self.queue[0] is not None:
            self.start_pos += 1
            yield self.queue.pop(0)

    def is_empty(self):
        return self.start_pos == self.size


class NHSConditionsAPISpider(scrapy.Spider):
    name = "nhsconditions"
    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 7, # free tier of the API has a rate limit of 10 requests per minute
        "REDIRECT_ENABLED": False,
        "HTTPERROR_ALLOW_ALL": True, # It is important that the response callback is always called, even if there was an error, to update the item queue.
    }

    source_id = "nhs_conditions"
    api_key = os.environ["NHS_API_KEY"]
    headers = {"subscription-key": api_key}

    url="https://api.nhs.uk/conditions/"

    def start_requests(self):
        return [scrapy.Request(url=self.url, 
                headers=self.headers,
                callback=self.parse)]

    def parse(self, response):
        rjson = json.loads(response.text)
           
        # get the links for each of the conditions
        links = rjson["significantLink"]

        item_queue = ItemQueue()
        requests = []
        for link in links:
            rel = link["linkRelationship"]

            if rel == "Result":
                try:
                    req = scrapy.Request(
                        link["url"],
                        self.parse_item,
                        headers=self.headers,
                        meta={
                            "item_queue": item_queue,
                            "position": len(requests),
                            "force_refresh": True,
                        },
                    )
                    req.priority = -len(requests)
                    requests.append(req)
                except Exception as e:
                    print(e)
                    pass
        
        # get the link for the next page
        next_page_url = None
        for link in rjson["relatedLink"]:
            if link["name"] == "Next Page":
                next_page_url = link["url"]
                break

        if requests:
            item_queue.size = len(requests)
            item_queue.next_page_url = next_page_url
            return requests

        if next_page_url is not None:
            return [
                scrapy.Request(next_page_url, self.parse, headers=self.headers)
            ]
        return []

    def parse_item(self, response):

        print(response.url)
        meta = response.request.meta
        if response.status == 200:
            html = response.text
        else:
            html=""
            self.logger.info(
                f"Response code for {response.url} is {response.status}. Skipping..."
            )

        item = HTMLItem(
                html=html, 
                source_url=response.url, 
                retrieved_at=datetime.datetime.now()
            )
    
        item_queue = meta["item_queue"]
        item_queue.put(meta["position"], item)

        for item in item_queue.poll():
            # for each item in the item poll, return the content (which is the html of the page)
            if item.get("html") != "":
                yield item
            else:
                url = item.get("source_url")
                self.logger.warn("Could not extract any text from %s", url)
        if item_queue.is_empty() and item_queue.next_page_url is not None:
            yield scrapy.Request(
                item_queue.next_page_url, self.parse, headers=self.headers
            )

def extract_text_from_main_entity(ent, text=None, key='mainEntityOfPage', text_field ='text'):
        if text is None:
            text = io.StringIO()
        for elt in ent:
            nested = elt.get(key)
            if elt.get("name") == "markdown":
                text.write(elt.get(text_field))
            if isinstance(nested, list):
                extract_text_from_main_entity(nested, text)
        return text

# def determine_page_schema(ent):
#     """The NHS Conditions pages come in a number of schemas, we need to determine which one we have."""

#     if 
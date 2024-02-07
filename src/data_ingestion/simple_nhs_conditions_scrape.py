from dotenv import load_dotenv
import os
import json
import datetime
import dateutil.parser
from io import StringIO
import io
import jsonlines

import scrapy

load_dotenv(".secrets")
os.environ["NHS_API_KEY"] = os.getenv("nhs_api_key")


class BaseItem(scrapy.Item):
    """Base class for items generated by scrapers. The framework ignores any items that are not instances of this class"""
    source_url = scrapy.Field() # Mandatory field. See ../../README.md for details.
    retrieved_at = scrapy.Field() # Optional field. Currently not used.
    modified_at = scrapy.Field() # Optional field. Should not be set in case of multiple documents on the same page.


class CorpusItem(BaseItem):
    """Base class for corpus text items."""
    pass


class HTMLItem(CorpusItem):
    """A corpus item in html format. The framework converts this to plain text before ingesting"""
    html = scrapy.Field()


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


def extract_text_from_html_json_chunk(ent: dict, text: str=None, key: str='mainEntityOfPage') -> io.StringIO:
    """Extracts text from the json object that contains the html for the nhs conditions pages
    Args:
    ent (dict): the json object
    text (str, optional): the text to append to. Defaults to None.
    key (str, optional): the key to look for in the json object. Defaults to "mainEntityOfPage".
    Returns:
    io.StringIO: the text extracted from the json object
    
    Example:
    >>> extract_text_from_html_json_chunk([{"mainEntityOfPage": [{"name": "markdown", "text": "some text"}]}]).getvalue()
    'some text'
    """   
    if text is None:
        text = io.StringIO()
    for elt in ent:
        nested = elt.get(key,"")
        if key == "mainEntityOfPage":
            if elt.get("name") == "markdown":
                text.write(elt.get('text'))
        elif key == "hasPart":
            headline_field = elt.get("headline","")
            text_field = elt.get("text","")
            description_field = elt.get("description","")
            text.write(headline_field + " " + description_field + " " + text_field + " ")

        if isinstance(nested, list):
            extract_text_from_html_json_chunk(nested, text, key = key)
    return text


def process_nhs_conditions_json(json_string: str) -> str:
    """Extracts the text from the json object that contains the html for the nhs conditions pages
    Args:
        json_string (str): the MHS Conditions json object (for a page), from the API.
    Returns:
        str: the text extracted from the json object
    Example:
    >>> process_nhs_conditions_json({"html": '{"mainEntityOfPage": [{"name": "markdown", "text": "some text"}]}'})
    'some text'
    """
    try:
        content = json.loads(json_string['html'])

        # there are currently two types of html structure in the nhs conditions data - one where the mainEntityOfPage holds the text, and one where the hasPart holds the text
        main_entity_text = extract_text_from_html_json_chunk(content.get('mainEntityOfPage',[]), key='mainEntityOfPage').getvalue()
        has_part_text = extract_text_from_html_json_chunk(content.get('hasPart',[]), key='hasPart').getvalue()
        all_text = main_entity_text + has_part_text
    except json.JSONDecodeError as e:
        # some of the pages are just in HTML, not as a json object
        print("Error decoding json for ", json_string['source_url'])
        all_text = ""
    
    return all_text


def unpack_json(json_doc = 'nhsconditions.jsonl', output_dir = 'docs/'):
    """Extracts the json found in `nhsconditions` into individual files, one for each of the conditions
    Args:
        json_doc (str): the path to the json document
        output_dir (str): the path to the directory where the files will be saved
    Returns:
        None
    """
    with jsonlines.open(json_doc) as reader:
        for index, obj in enumerate(reader):
            extracted_text = process_nhs_conditions_json(obj)

            page_name = obj['source_url'].split('/')[-2]
            
            if extracted_text != '':
                    with open(f"{output_dir}{page_name}.txt", "w", encoding='utf-8') as file:
                        file.write(extracted_text)  
            
            print(index, ": ", obj['source_url'])


if __name__ == "__main__":
    import doctest
    doctest.testmod()
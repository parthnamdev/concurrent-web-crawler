from bs4 import BeautifulSoup
import threading

from urllib.request import Request, urlopen, URLError, urljoin
from urllib.request import urlparse
from urllib.request import urljoin

import time
import ssl
import json
from nltk import tokenize, FreqDist
import os

from spacy.lang.en.stop_words import STOP_WORDS
import re

urlinput = "https://vit.ac.in/"
base = "https://vit.ac.in/"
crawler_level = 2


if os.path.exists("urls.txt"):
  os.remove("urls.txt")
if os.path.exists("inverted_index.json"):
  os.remove("inverted_index.json")

urls_parsed = set()
urls_crawled = set()
urls_correct = set()
index = 0

all_freq = dict()
all_words = dict()
all_unique_words = dict()

indexes = []

global_lock = threading.Lock()


def remove_char(webdata):
    text = re.sub("[^A-Za-z0-9]+", " ", webdata)  #removcharacters
    text = text.lower()
    return text


def extract_terms(text):
    tokens = tokenize.word_tokenize(text)
    terms = [
        notStopWords for notStopWords in tokens
        if notStopWords not in STOP_WORDS
    ]  #remove stopwords
    terms = [term for term in terms
             if re.search("[0-9]+", term) == None]  #remove numbers
    return terms


def frequency_of_words(tokenized_file):
    fdist = FreqDist(tokenized_file)
    file_frequency_distribution = dict(
        (word, freq) for word, freq in fdist.items())
    return file_frequency_distribution


def list_count(seq, item):
    start_at = -1
    locs = []
    while True:
        try:
            loc = seq.index(item, start_at + 1)
        except ValueError:
            break
        else:
            locs.append(loc + 1)
            start_at = loc
    return locs


# indexer function -------------------------------------------

def add_to_file(URL_index,unique_terms,term_frequency,terms):
    for term in unique_terms:
        term_indexes = index.get(term, [])
        new_index_entry = f"<d{URL_index},{term_frequency[term]},{list_count(terms,term)}>"
        term_indexes.append(new_index_entry)
        index[term] = term_indexes
    new_data = {"index_list": index}
    indexes.append(new_data)

def create_inverted_index(all_unique_words,all_freq,all_words):
    count = 0
    threads=[]
    for url in urls_correct:
        threads.append(
                threading.Thread(target=add_to_file, args=[int(count),all_unique_words[url], all_freq[url], all_words[url], ]))
        threads[-1].start()
        time.sleep(0.07)
        count+=1
    for t in threads:
            t.join()


# crawler function ---------------------------------------------

def level_crawler(input_url, index):
    my_ssl = ssl.create_default_context()
    my_ssl.check_hostname = False
    my_ssl.verify_mode = ssl.CERT_NONE
    temp_urls = set()
    current_url_domain = urlparse(input_url).netloc
    x = input_url.split(':')[0]
    extension_href = input_url.split(base)[-1]
    extension = "html"
    if ("." in extension_href):
        extension = input_url.split(".")[-1]
    if (input_url not in urls_parsed) and x != 'mailto' and ( extension == "html" or extension == "htm" or extension == "jsp" or extension == "php"):
        urls_parsed.add(input_url)
        try:
            req = Request(input_url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urlopen(req, context=my_ssl)
            beautiful_soup_object = BeautifulSoup(response.read(), "html.parser")
            terms = extract_terms(remove_char(beautiful_soup_object.get_text()))
            # print(f"{input_url}")
        
            print(f"{threading.current_thread().name} - Crawling : {input_url}")
        
            try:
                all_words[input_url].add(terms)
                all_freq[input_url].add(frequency_of_words(terms))
                all_unique_words[input_url].add(sorted(list(set(terms))))
            except:
                all_words[input_url]=terms
                all_freq[input_url]=frequency_of_words(terms)
                all_unique_words[input_url]=sorted(list(set(terms)))

            urls_correct.add(input_url)
            for anchor in beautiful_soup_object.findAll("a"):
                href = anchor.attrs.get("href")
                if (href != "" or href != None):
                    href = urljoin(input_url, href)
                    href_parsed = urlparse(href)
                    href = href_parsed.scheme
                    href += "://"
                    href += href_parsed.netloc
                    href += href_parsed.path
                    final_parsed_href = urlparse(href)
                    is_valid = bool(final_parsed_href.scheme) and bool(final_parsed_href.netloc) and not final_parsed_href.path.endswith('.php') and not final_parsed_href.path.endswith('.svg')
                    if is_valid:
                        if current_url_domain in href and href not in temp_urls:
                            temp_urls.add(href)
                            urls_crawled.add(href)
                
        except UnicodeEncodeError:
            print("inappropriate name")
        except:
            print("ssl rejected by server")
        
        index = index + 1

        if index < crawler_level:
            task(list(temp_urls), index)
    else:
        pass


def task(temp_urls, index):
    if index <= crawler_level-1:
        threads = []

        for url in temp_urls:
            lock = threading.Lock()
            threads.append(
                threading.Thread(target=level_crawler, args=(
                    url,
                    index,
                )))
            threads[-1].start()
            time.sleep(0.05)
            urls_parsed.add(url)
        for t in threads:
            t.join()
    else:
        for url in temp_urls:
            level_crawler(url, index)
            urls_parsed.add(url)


t = time.time()

level_crawler(urlinput, index)

print("\nURLs parsed : ", len(set(urls_parsed)))
print("Total valid links found : ", len(set(urls_crawled)))

t1 = time.time()
print("\nTime taken for crawling")
print(t1 - t)

with open("urls.txt", mode="w") as file:
    file.write("\n".join(urls_crawled))

try:
    with open("inverted_index.json", mode="r") as file:
        json_data = json.load(file)
        index = json_data["index_list"]
except IOError:
    with open("inverted_index.json", mode="w") as file:
        new_data = {"index_list": {}}
        json.dump(new_data, file, indent=2)
    index = {}


 
create_inverted_index(all_unique_words,all_freq,all_words)

with open("inverted_index.json", mode="r") as file:
    json_data = json.load(file)
for new_data in indexes:
    json_data.update(new_data)
with open("inverted_index.json", mode="w") as file:
    json.dump(json_data, file, indent=2)

t2=time.time()

print("\nTime taken for indexing")

print(t2-t1)

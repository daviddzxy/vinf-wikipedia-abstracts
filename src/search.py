import argparse
from analyse import get_number_of_sentences, get_number_of_words
from elasticsearch import Elasticsearch

WIKI_INDEX = "wiki_abstracts"
DBPEDIA_INDEX = "dbpedia_abstracts"

parser = argparse.ArgumentParser("Search abstracts by title.")
parser.add_argument("title", nargs=1, help="Title string")
parser.add_argument("--stats", default=False, action="store_true", help="Print abstract statistics.")
args = parser.parse_args()

search_query = {
    "query": {
        "match": {
            "title": {
                "query": args.title[0]
            }
        }
    }
}

statistics_string = "Number of sentences: {}\n" \
                    "Number of words: {}\n" \
                    "Part of speech histogram: {}\n"


client = Elasticsearch("http://localhost:9200")

wiki_response = client.search(index=WIKI_INDEX, body=search_query)
dbpedia_response = client.search(index=DBPEDIA_INDEX, body=search_query)

if wiki_response["hits"]["total"]["value"] != 0:
    print("Basic abstract:")
    basic = wiki_response["hits"]["hits"][0]["_source"]["basic_abstract"]
    print(basic)
    if args.stats:
        print(statistics_string.format(get_number_of_sentences(basic),
                                       get_number_of_words(basic)))

    print("Text rank abstract:")
    rank = wiki_response["hits"]["hits"][0]["_source"]["rank_abstract"]
    print(rank)
    if args.stats:
        print(statistics_string.format(get_number_of_sentences(rank),
                                       get_number_of_words(rank)))
else:
    print("Parsed abstracts not found.")

if dbpedia_response["hits"]["total"]["value"] != 0:
    print("DBPedia abstract:")
    dbpedia = dbpedia_response["hits"]["hits"][0]["_source"]["abstract"]
    print(dbpedia)
    if args.stats:
        print(statistics_string.format(get_number_of_sentences(dbpedia),
                                       get_number_of_words(dbpedia)))
else:
    print("DBPedia abstract not found.")

import argparse
import utils
from elasticsearch import Elasticsearch

WIKI_INDEX = "wiki_abstracts"
DBPEDIA_INDEX = "dbpedia_abstracts"

parser = argparse.ArgumentParser("Search abstracts by title.")
parser.add_argument("title", nargs=1, help="Title string.")
parser.add_argument("--compare", default=True, action="store_true", help="Print abstract statistics.")
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

client = Elasticsearch("http://localhost:9200")

wiki_response = client.search(index=WIKI_INDEX, body=search_query)
dbpedia_response = client.search(index=DBPEDIA_INDEX, body=search_query)

basic = None
dbpedia = None
rank = None
if wiki_response["hits"]["total"]["value"] != 0:
    print("Basic abstract:")
    basic = wiki_response["hits"]["hits"][0]["_source"]["basic_abstract"]
    print(basic)

    print("Text rank abstract:")
    rank = wiki_response["hits"]["hits"][0]["_source"]["rank_abstract"]
    print(rank)

else:
    print("Parsed abstracts not found.")


if dbpedia_response["hits"]["total"]["value"] != 0:
    print("DBPedia abstract:")
    dbpedia = dbpedia_response["hits"]["hits"][0]["_source"]["abstract"]
    print(dbpedia)

else:
    print("DBPedia abstract not found.")


if args.compare and basic and rank and dbpedia:
    term_query_dbpedia = {
        "fields": ["abstract"],
        "payloads": True,
        "term_statistics": True,
        "field_statistics": True,
        "positions": False,
        "offsets": False
    }

    term_query_basic = {
        "doc": {
            "abstract": basic
        },
        "fields": ["abstract"],
        "payloads": True,
        "term_statistics": True,
        "field_statistics": True,
        "positions": False,
        "offsets": False
    }

    term_query_rank = {
        "doc": {
            "abstract": rank
        },
        "fields": ["abstract"],
        "payloads": True,
        "term_statistics": True,
        "field_statistics": True,
        "positions": False,
        "offsets": False
    }

    db_pedia_terms = client.termvectors(index=DBPEDIA_INDEX, body=term_query_dbpedia, id=dbpedia_response["hits"]["hits"][0]["_id"])
    basic_terms = client.termvectors(index=DBPEDIA_INDEX, body=term_query_basic)
    rank_terms = client.termvectors(index=DBPEDIA_INDEX, body=term_query_rank)

    doc_count = db_pedia_terms["term_vectors"]["abstract"]["field_statistics"]["doc_count"]
    db_pedia_terms = db_pedia_terms["term_vectors"]["abstract"]["terms"]
    basic_terms = basic_terms["term_vectors"]["abstract"]["terms"]
    rank_terms = rank_terms["term_vectors"]["abstract"]["terms"]
    basic_similarity = utils.compare_terms(db_pedia_terms, basic_terms, doc_count)
    rank_similarity = utils.compare_terms(db_pedia_terms, rank_terms, doc_count)
    print("Similarity basic abstract - dbpedia abstract: {}".format(basic_similarity))
    print("Similarity text rank abstract - dbpedia abstract: {}".format(rank_similarity))
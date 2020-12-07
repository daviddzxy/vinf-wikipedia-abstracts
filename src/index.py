import argparse
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from parsers import WikiParser, DBPediaAbstractParser
from abstract_makers import DefaultAbstractMaker, TextRankAbstractMaker

parser = argparse.ArgumentParser("This script parses wikipedia articles, parsed articles are then transformed"
                                 " into abstracts. Abstracts are indexed into elasticsearch.")
parser.add_argument("-e", "--epochs", default=10, type=int, help="Set maximal number of epochs of text rank algorithm.")
parser.add_argument("-d", "--delta", default=0.001, type=float, help="Set delta, which is used to determine early"
                                                                     " stopping criterion of text rank algorithm.")
parser.add_argument("-t", "--top", default=7, type=int, help="Set number of most fitting sentences to be used "
                                                             "in abstracts.")
parser.add_argument("-p", "--port", default=9200, type=int, help="Set elasticsearch port number.")
args = parser.parse_args()

WIKI_INDEX = "wiki_abstracts"
DBPEDIA_INDEX = "dbpedia_abstracts"

wiki_mapping = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "analyzer": {
                "english_analyzer": {
                    "type": "standard",
                    "stopwords": "_english_"
                }
            }
        }
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "title": {
                "type": "text"
            },
            "basic_abstract": {
                "type": "text",
                "analyzer": "english_analyzer"
            },
            "rank_abstract": {
                "type": "text",
                "analyzer": "english_analyzer"
            }
        }
    }
}

dbpedia_mapping = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "analyzer": {
                "english_analyzer": {
                    "type": "standard",
                    "stopwords": "_english_"
                }
            }
        }
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "title": {
                "type": "text"
            },
            "abstract": {
                "type": "text",
                "analyzer": "english_analyzer",
                "term_vector": "yes"
            }
        }
    }
}


def abstract_makers_generator(wiki_parser):
    default_abstract_maker = DefaultAbstractMaker(top_n=args.top)
    text_rank_abstract_maker = TextRankAbstractMaker(top_n=args.top, delta=args.delta, epochs=args.epochs)
    while True:
        article = wiki_parser.get_one_article()
        if article != "EOF":
            basic_abstract = default_abstract_maker(article["article"])
            rank_abstract = text_rank_abstract_maker(article["article"])
            yield {
                "_id": article["id"],
                "title": article["title"],
                "basic_abstract": basic_abstract,
                "rank_abstract": rank_abstract
            }
        else:
            return


def abstract_parser_generator(dbpedia_parser):
    while True:
        article = dbpedia_parser.get_one_abstract()
        if article != "EOF":
            yield {
                "title": article["title"],
                "abstract": article["abstract"]
            }
        else:
            return


wiki_parser = WikiParser("../data/test-wiki.xml")
dbpedia_parser = DBPediaAbstractParser("../data/test-dbpedia.xml")


client = Elasticsearch("http://localhost:{}".format(args.port))

client.indices.create(
    index=WIKI_INDEX,
    body=wiki_mapping,
    ignore=400
)

client.indices.create(
    index=DBPEDIA_INDEX,
    body=dbpedia_mapping,
    ignore=400
)

helpers.bulk(client, abstract_makers_generator(wiki_parser), index=WIKI_INDEX, raise_on_error=True)
helpers.bulk(client, abstract_parser_generator(dbpedia_parser), index=DBPEDIA_INDEX, raise_on_error=True)

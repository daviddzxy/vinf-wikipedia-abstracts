import argparse
import logging
import os
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from parsers import WikiParser, DBPediaAbstractParser
from abstract_makers import DefaultAbstractMaker, TextRankAbstractMaker
from config import index_vars, data_dir, log_dir, wiki_file, dbpedia_file

WIKI_INDEX = "wiki_abstracts"
DBPEDIA_INDEX = "dbpedia_abstracts"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(filename=os.path.join(log_dir, "index_logs.log"),
                    format="%(asctime)s %(levelname)-8s %(message)s",
                    datefmt="%d-%m-%Y %H:%M:%S",
                    filemode="w",
                    level=logging.INFO,
                    force=True)

parser = argparse.ArgumentParser("This script parses wikipedia articles, parsed articles are then transformed"
                                 " into abstracts. Abstracts are indexed into elasticsearch.")
parser.add_argument("-e", "--epochs", default=index_vars["epochs"], type=int, help="Set maximal number of epochs of text rank algorithm.")
parser.add_argument("-d", "--delta", default=index_vars["delta"], type=float, help="Set delta, which is used to determine early"
                                                                     " stopping criterion of text rank algorithm.")
parser.add_argument("-t", "--top", default=index_vars["top"], type=int, help="Set number of most fitting sentences to be used "
                                                             "in abstracts.")
parser.add_argument("-p", "--port", default=index_vars["port"], type=int, help="Set elasticsearch port number.")
parser.add_argument("--wiki-file", default=wiki_file)
parser.add_argument("--dbpedia-file", default=dbpedia_file)
args = parser.parse_args()

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
        try:
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
                logging.info("Wikipedia abstracts\t{}\tindexed.".format(article["title"]))
            else:
                return
        except Exception:
            logging.error("Error occured while indexing article\t{}.".format(article.title()))


def abstract_parser_generator(dbpedia_parser):
    while True:
        try:
            article = dbpedia_parser.get_one_abstract()
            if article != "EOF":
                yield {
                    "title": article["title"],
                    "abstract": article["abstract"]
                }
                logging.info("Dbpedia abstract\t{}\tindexed.".format(article["title"]))
            else:
                return
        except Exception:
            logging.error("Error occured while indexing article\t{}.".format(article.title()))


wiki_parser = WikiParser(os.path.join(data_dir, args.wiki_file))
dbpedia_parser = DBPediaAbstractParser(os.path.join(data_dir, args.dbpedia_file))

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

logging.info("Indexing started.")
helpers.bulk(client, abstract_makers_generator(wiki_parser), index=WIKI_INDEX, raise_on_error=True)
helpers.bulk(client, abstract_parser_generator(dbpedia_parser), index=DBPEDIA_INDEX, raise_on_error=True)
logging.info("Indexing ended.")

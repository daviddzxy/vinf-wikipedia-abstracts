import argparse
import logging
import os
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from parsers import DBPediaAbstractParser
from config import index_vars, data_dir, log_dir, dbpedia_file, dbpedia_index

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(filename=os.path.join(log_dir, "dbpedia_index_logs.log"),
                    format="%(asctime)s %(levelname)-8s %(message)s",
                    datefmt="%d-%m-%Y %H:%M:%S",
                    filemode="w",
                    level=logging.INFO,
                    force=True)

parser = argparse.ArgumentParser("This script parses and indexes dbpedia abstracts.")
parser.add_argument("-p", "--port", default=index_vars["port"], type=int, help="Set elasticsearch port number.")
parser.add_argument("-f", "--file", default=dbpedia_file)
args = parser.parse_args()

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
            logging.error("Error occured.")


dbpedia_parser = DBPediaAbstractParser(os.path.join(data_dir, args.file))

client = Elasticsearch("http://localhost:{}".format(args.port))

client.indices.create(
    index=dbpedia_index,
    body=dbpedia_mapping,
    ignore=400
)

logging.info("Indexing started.")
helpers.bulk(client, abstract_parser_generator(dbpedia_parser), index=dbpedia_index, raise_on_error=True, request_timeout=60)
logging.info("Indexing ended.")

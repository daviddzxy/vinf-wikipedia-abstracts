from elasticsearch import Elasticsearch
from elasticsearch import helpers
from parsers import WikiParser, DBPediaAbstractParser
from abstract_makers import DefaultAbstractMaker, TextRankAbstractMaker

WIKI_INDEX = "wiki_abstracts"
DBPEDIA_INDEX = "dbpedia_abstracts"

wiki_mapping = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "title": {
                "type": "text"
            },
            "basic_abstract": {
                "type": "text"
            },
            "rank_abstract": {
                "type": "text"
            }
        }
    }
}

dbpedia_mapping = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "title": {
                "type": "text"
            },
            "abstract": {
                "type": "text",
                "term_vector": "yes"
            }
        }
    }
}


def abstract_makers_generator(wiki_parser):
    default_abstract_maker = DefaultAbstractMaker(5)
    text_rank_abstract_maker = TextRankAbstractMaker(5)
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

client = Elasticsearch("http://localhost:9200")

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

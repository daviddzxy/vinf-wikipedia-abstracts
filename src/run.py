from parsers import WikiParser, DBPediaAbstractParser
from abstract_makers import DefaultAbstractMaker, TextRankAbstractMaker
import nltk

nltk.download("stopwords")
nltk.download('wordnet')
nltk.download("punkt")


f_da = open("../data/default_abstracts.csv", "w")
f_ta = open("../data/text_rank_abstracts.csv", "w")
f_pa = open("../data/parsed_abstracts.csv", "w")

wiki_parser = WikiParser("../data/small-test.xml")
dbpedia_parser = DBPediaAbstractParser("../data/long_abstracts_en.nq")
default_abstract_maker = DefaultAbstractMaker()
text_rank_abstract_maker = TextRankAbstractMaker()

parsed_article = None
while parsed_article != "EOF":
    parsed_article = wiki_parser.get_one_article()
    if parsed_article != "EOF":
        default_abstract = default_abstract_maker(parsed_article["article"], 5)
        text_rank_abstract = text_rank_abstract_maker(parsed_article["article"], 5)
        f_da.write(parsed_article["title"] + "    " + default_abstract if default_abstract is not None else "" + "\n")
        f_ta.write(parsed_article["title"] + "    " + text_rank_abstract if text_rank_abstract is not None else "" + "\n")


parsed_abstract = None
while parsed_abstract != "EOF":
    parsed_abstract = dbpedia_parser.get_one_abstract()
    if parsed_abstract != "EOF":
        if parsed_abstract["title"] is not None:
            f_pa.write(parsed_abstract["title"] + "    " + parsed_abstract["abstract"] if parsed_abstract is not None else "" + "\n")

f_da.close()
f_ta.close()
f_pa.close()


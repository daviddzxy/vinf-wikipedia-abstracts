from parsers import DefaultParser
from abstract_makers import DefaultAbstractMaker, TextRankAbstractMaker
import nltk

nltk.download("stopwords")
nltk.download("punkt")

parser = DefaultParser('../data/small-test.xml')
abstract_maker = DefaultAbstractMaker()
text_rank_abstract_maker = TextRankAbstractMaker()
result = None
while result != "EOF":
    result = parser.get_one_article()
    print(result)
    if result != "EOF":
        print(abstract_maker(result['article'], 5))
        print(text_rank_abstract_maker(result['article'], 5))
data_dir = "/media/david/DATA/Wiki-Data"
log_dir = "/home/david/school/vinf/logs"
wiki_file = "enwiki-20200920-pages-articles-multistream.xml",
dbpedia_file = "long_abstracts_en.nq"
wiki_index = "wiki_abstracts"
dbpedia_index = "dbpedia_abstracts"
index_vars = {
    "epochs": 10,
    "delta": 0.001,
    "top": 7,
    "port": 9200
    }
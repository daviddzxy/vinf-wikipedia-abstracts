import math


def get_tf_idf(term_freq, doc_freq, word_count, doc_count):
    tf = term_freq / word_count
    idf = math.log(doc_count / doc_freq + 1)  # natural logarithm
    return tf * idf


def compare_terms(terms1, terms2, doc_count):
    terms = set(list(terms1.keys()) + list(terms2.keys()))
    word_count1 = len(terms1.keys())
    word_count2 = len(terms2.keys())
    vector1 = [0] * len(terms)
    vector2 = [0] * len(terms)
    for idx, term in enumerate(terms):
        if term in terms1.keys():
            doc_freq = terms1[term]["doc_freq"] if terms1[term]["doc_freq"] else 0
            vector1[idx] = get_tf_idf(terms1[term]["term_freq"], doc_freq, word_count1, doc_count)
        if term in terms2.keys():
            doc_freq = terms2[term]["doc_freq"] if terms2[term]["doc_freq"] else 0
            vector2[idx] = get_tf_idf(terms2[term]["term_freq"], doc_freq, word_count2, doc_count)




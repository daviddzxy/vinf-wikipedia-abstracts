import re


def get_number_of_sentences(text):
    return len(re.split(r"[.?!]+", text))


def get_number_of_words(text):
    return len(re.split(r" ", text))


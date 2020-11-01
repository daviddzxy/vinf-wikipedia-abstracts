import re
import nltk
import string
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords


class AbstractMaker():
    def __init__(self):
        nltk.download("stopwords")
        nltk.download("punkt")
        self.stopwords = set(stopwords.words("english"))

    @staticmethod
    def lower_case(text):
        return text.lower()

    @staticmethod
    def remove_numbers(text):
        return re.sub(r"\d+", "", text)

    @staticmethod
    def remove_whitespaces(text):
        return text.strip()

    @staticmethod
    def tokenize_sentences(text):
        return sent_tokenize(text)

    @staticmethod
    def tokenize_words(text):
        return word_tokenize(text)

    def remove_stop_words(self, words):
        return [word for word in words if word not in self.stopwords]

    @staticmethod
    def remove_punctation(words):
        return [word for word in words if word not in string.punctuation]


class DefaultAbstractMaker(AbstractMaker):
    def __call__(self, lines):
        if len(lines) == 0:
            return None

        sentences = self.tokenize_sentences(lines)
        preprocessed_sentences = [[]] * len(sentences)
        sentence_scores = [0] * len(sentences)
        word_scores = {}
        for idx, sentence in enumerate(sentences, 0):
            preprocessed_sentence = self.lower_case(sentence)
            preprocessed_sentence = self.remove_numbers(preprocessed_sentence)
            preprocessed_sentence = self.remove_whitespaces(preprocessed_sentence)
            preprocessed_sentence = self.tokenize_words(preprocessed_sentence)
            preprocessed_sentence = self.remove_stop_words(preprocessed_sentence)
            preprocessed_sentence = self.remove_punctation(preprocessed_sentence)
            preprocessed_sentences[idx] = preprocessed_sentence

        for preprocessed_sentence in preprocessed_sentences:
            for word in preprocessed_sentence:
                if word in word_scores:
                    word_scores[word] += 1
                else:
                    word_scores[word] = 0

        for idx, preprocessed_sentence in enumerate(preprocessed_sentences):
            for word in preprocessed_sentence:
                sentence_scores[idx] += word_scores[word]

        result_scores = []
        for sentence, score in sorted(zip(sentences, sentence_scores), reverse=True, key=lambda score: score[1]):
            result_scores.append({"sentence": sentence, })

        return result_scores
import re
import string
import numpy as np
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.cluster.util import cosine_distance


class AbstractMaker:
    def __init__(self, top_n):
        self.stopwords = set(stopwords.words("english"))
        self.lemmatizer = WordNetLemmatizer()
        self.top_n = top_n

    @staticmethod
    def _lower_case(text):
        return text.lower()

    @staticmethod
    def _remove_numbers(text):
        return re.sub(r"\d+", "", text)

    @staticmethod
    def _remove_whitespaces(text):
        return text.strip()

    @staticmethod
    def _tokenize_sentences(text):
        return sent_tokenize(text)

    @staticmethod
    def _tokenize_words(text):
        return word_tokenize(text)

    def _remove_stop_words(self, words):
        return [word for word in words if word not in self.stopwords]

    @staticmethod
    def _remove_punctation(words):
        return [word for word in words if word not in string.punctuation]

    def _lemmatize(self, words):
        return [self.lemmatizer.lemmatize(word) for word in words]

    def _preprocess_sentences(self, sentences):
        preprocessed_sentences = [[]] * len(sentences)
        for idx, sentence in enumerate(sentences, 0):
            preprocessed_sentence = self._lower_case(sentence)
            preprocessed_sentence = self._remove_numbers(preprocessed_sentence)
            preprocessed_sentence = self._remove_whitespaces(preprocessed_sentence)
            preprocessed_sentence = self._tokenize_words(preprocessed_sentence)
            preprocessed_sentence = self._remove_stop_words(preprocessed_sentence)
            preprocessed_sentence = self._remove_punctation(preprocessed_sentence)
            preprocessed_sentence = self._lemmatize(preprocessed_sentence)
            preprocessed_sentences[idx] = preprocessed_sentence

        return preprocessed_sentences


class DefaultAbstractMaker(AbstractMaker):
    def __call__(self, lines):
        if len(lines) == 0:
            return ""

        sentences = self._tokenize_sentences(lines)
        preprocessed_sentences = self._preprocess_sentences(sentences)
        sentence_scores = [0] * len(sentences)
        word_scores = {}

        for preprocessed_sentence in preprocessed_sentences:
            for word in preprocessed_sentence:
                if word in word_scores:
                    word_scores[word] += 1
                else:
                    word_scores[word] = 0

        for idx, preprocessed_sentence in enumerate(preprocessed_sentences):
            for word in preprocessed_sentence:
                sentence_scores[idx] += word_scores[word]
            sentence_scores[idx] = sentence_scores[idx] / len(preprocessed_sentences[idx])

        top_sentences = []
        for sentence, score in sorted(
                zip(sentences, sentence_scores),
                reverse=True,
                key=lambda score: score[1])[0: self.top_n]:
            top_sentences.append(sentence)

        return " ".join(top_sentences)


class TextRankAbstractMaker(AbstractMaker):
    def __init__(self, top_n, delta, epochs):
        super().__init__(top_n=top_n)
        self.delta = delta
        self.epochs = epochs

    @staticmethod
    def get_similarity(sentence1, sentence2):
        combined_words = list(set(sentence1 + sentence2))
        vector1 = [0] * len(combined_words)
        vector2 = [0] * len(combined_words)

        for word1 in sentence1:
            vector1[combined_words.index(word1)] += 1

        for word2 in sentence2:
            vector2[combined_words.index(word2)] += 1

        return 1 - cosine_distance(vector1, vector2)

    def __call__(self, lines):
        if len(lines) == 0:
            return ""

        sentences = self._tokenize_sentences(lines)
        preprocessed_sentences = self._preprocess_sentences(sentences)
        sm = np.zeros([len(sentences), len(sentences)])
        for idx1 in range(len(sentences)):
            for idx2 in range(len(sentences)):
                if idx1 == idx2:
                    continue
                sm[idx1][idx2] = self.get_similarity(
                                                    preprocessed_sentences[idx1],
                                                    preprocessed_sentences[idx2]
                                                    )

        norm = np.sum(sm, axis=0)
        sm = np.divide(sm, norm, where=norm != 0)
        pr = np.array([1] * len(sm))
        dp_factor = 0.85
        prev_pr = 0
        for i in range(0, self.epochs):
            pr = (1 - dp_factor) + dp_factor * np.matmul(sm, pr)
            if abs(prev_pr - np.sum(pr)) < self.delta:
                break
            else:
                prev_pr = np.sum(pr)

        ranks = list(reversed(np.argsort(pr)))
        top_sentences = [""] * self.top_n
        for i in range(self.top_n):
            sentence_idx = ranks[i]
            top_sentences[i] = sentences[sentence_idx]

        return " ".join(top_sentences)

import re


class DefaultAbstractMaker():
    def __call__(self, lines):
        if len(lines) == 0:
            return None
        word_scores = {}
        sentence_scores = {}
        for line in lines:
            for sentence in list(map(str.strip, re.split(r"\.", line))):
                if sentence != "":
                    sentence_scores[sentence] = 0

        for sentence, _ in sentence_scores.items():  # get scores for words
            words = sentence.split()
            for word in words:
                if word in word_scores:
                    word_scores[word] += 1
                else:
                    word_scores[word] = 0

        for sentence, _ in sentence_scores.items():  # get scores for sentences
            words = sentence.split()
            for word in words:
                sentence_scores[sentence] += word_scores[word]

            sentence_scores[sentence] = sentence_scores[sentence] / len(words)

        result = []
        for sentence, score in sorted(sentence_scores.items(), reverse=True, key=lambda score: score[1])[0:5]:
            result.append(sentence + ".")

        print(result)
import re
import logging

logging.basicConfig(filename="logs.log", level=logging.DEBUG)
logger = logging.getLogger()


def make_abstract(lines):
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


def link_text(m):
    if m.group(3) is not None:
        return m.group(3)
    return m.group(1)


def extenal_link_text(m):
    if m.group(3) is not None:
        return m.group(3)
    return ""


def mail_to(m):
    if m.group(1) is not None:
        return m.group(1)
    return ""


replacing_regexes = [(r"\[\[(File|Image|Category):.*\]\]", ""),
                     (r"\[\[(.*?)(\|(.*?))*\]\]", link_text),
                     (r"'{3}(.*?)'{3}", r"\1"),
                     (r"'{2}(.*?)'{2}", r"\1"),
                     (r"\[https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9("
                      r")@:%_\+.~#?&//=]*) ?(.*?)\]", extenal_link_text),
                     (r"\[mailto:[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+ ?(.*)\]", mail_to),
                     (r"~{3,5}", ""),
                     (r"^\*.*", ""),  # lists
                     ("^(\s)*\|.*", ""),  # tables
                     (r"\{\{.*?\}\}", ""),
                     (r"&lt;ref(.*?)&gt;(.*?);/ref&gt;", ""),  # citations
                     (r"&quot;(.*?)&quot;", r"\1"),
                     (r"={2,5}(.*?)={2,5}", ""),  # headers
                     (r"&lt;(.*?)&gt;", ""),
                     (r"^(\{\{).*", ""),  # Library resources box / Infobox
                     (r"^}}$", ""),
                     (r"^(\s)*#", "")]

inside_text = False
inside_table = False
title = None

lines = []
articles = []

with open("../data/small-test.xml") as file:
    for line in file:
        logging.debug("IN: " + line)
        m = re.search(r"<title>(.*)</title>", line)
        if m:
            title = m.group(1)
            continue
        m = re.search(r"<text bytes=.*>", line)
        if m:
            m = re.search(r"#REDIRECT \[\[.*\]\]", line)  # empty text
            if m is None:
                inside_text = True
            continue
        m = re.search(r"</text>", line)
        if m:
            inside_text = False
            make_abstract(lines)
            lines = []
            continue
        if inside_text:
            m = re.search(r"^\{\|", line)
            if m:
                inside_table = True
            m = re.search(r"^\|\}", line)
            if m:
                inside_table = False

            if not inside_table:
                for regex in replacing_regexes:
                    line = re.sub(regex[0], regex[1], line)

                if not line.isspace():
                    logging.debug("ADDED: " + line)
                    line = re.sub(r"\n", r" ", line)
                    lines.append(line)
                else:
                    logging.debug("REJECTED")
            else:
                logging.debug("INSIDE TABLE - REJECTED")

import re
import logging

logging.basicConfig(filename="logs.log", level=logging.DEBUG, filemode='w')
logger = logging.getLogger()


class WikiParser():
    def __init__(self, data_path):
        self.lines = []
        self.file = open(data_path)
        self.is_inside_text = False
        self.is_inside_table = False
        self.article_id_found = False
        self.regexes = [(r"\[\[(File|Image|Category):.*\]\]", ""),
                     (r"\[\[(.*?)(\|(.*?))*\]\]", self._link_text),
                     (r"'{3}(.*?)'{3}", r"\1"),
                     (r"'{2}(.*?)'{2}", r"\1"),
                     (r"\[https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9("
                      r")@:%_\+.~#?&//=]*) ?(.*?)\]", self._extenal_link_text),
                     (r"\[mailto:[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+ ?(.*)\]", self._mail_to),
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
                     (r"^(\s)*#", ""),
                     (r"{{|}}", "")]

    def get_one_article(self):
        lines = []
        article_id = None
        title = None
        while True:
            line = self.file.readline()
            if line == "":
                return "EOF"

            m = re.search(r"</text>", line)
            if m:
                self.is_inside_text = False
                self.article_id_found = False
                return {
                    "title": title,
                    "id": article_id,
                    "article": ' '.join(lines)
                }

            m = re.search(r"<title>(.*)</title>", line)
            if m:
                title = m.group(1)
                title = re.sub(r'([a-z](?=[A-Z])|[A-Z](?=[A-Z][a-z]))', r'\1 ', title)  # WorldWideWeb -> World Wide Web
                continue

            m = re.search(r"<id>(.*)</id>", line)
            if m and not self.article_id_found:
                article_id = m.group(1)
                self.article_id_found = True

            m = re.search(r"<text bytes=.*>", line)
            if m:
                m = re.search(r"#REDIRECT \[\[.*\]\]", line)
                if m is None:
                    self.is_inside_text = True
                continue

            if self.is_inside_text:
                m = re.search(r"^\{\|", line)
                if m:
                    self.is_inside_table = True
                m = re.search(r"^\|\}", line)
                if m:
                    self.is_inside_table = False

                if not self.is_inside_table:
                    for regex in self.regexes:
                        line = re.sub(regex[0], regex[1], line)

                    if not line.isspace():
                        line = re.sub(r"\n", r" ", line)
                        lines.append(line)

    @staticmethod
    def _link_text(m):
        if m.group(3) is not None:
            return m.group(3)
        return m.group(1)

    @staticmethod
    def _extenal_link_text(m):
        if m.group(3) is not None:
            return m.group(3)
        return ""

    @staticmethod
    def _mail_to(m):
        if m.group(1) is not None:
            return m.group(1)
        return ""


class DBPediaAbstractParser():
    def __init__(self, data_path):
        self.file = open(data_path)
        self.file.readline()  # skip first line

    def get_one_abstract(self):
        line = self.file.readline()

        if line == "":
            return "EOF"

        title = None
        abstract = None
        m = re.search(r"\<(.*?)/resource/(.*?)\>", line)
        if m:
            title = m.group(2)
            title = title.replace("_", " ")

        m = re.search(r"\"(.*?)\"@en", line)
        if m:
            abstract = m.group(1)
        return {
            "title": title,
            "abstract": abstract
        }

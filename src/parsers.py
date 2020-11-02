import re
import logging

logging.basicConfig(filename="logs.log", level=logging.DEBUG, filemode='w',)
logger = logging.getLogger()


class DefaultParser():
    def __init__(self, data_path):
        self.lines = []
        self.file = open(data_path)
        self.is_inside_text = False
        self.is_inside_table = False
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
                     (r"^(\s)*#", "")]

    def get_one_article(self):
        lines = []
        title = None
        while True:
            line = self.file.readline()
            logging.debug("IN: " + line)

            if line == "":
                return "EOF"

            m = re.search(r"</text>", line)
            if m:
                self.is_inside_text = False
                return {"title": title, "article": ' '.join(lines)}

            m = re.search(r"<title>(.*)</title>", line)  # rewrtie this to not use continue, add this regex to regexes
            if m:
                title = m.group(1)
                continue

            m = re.search(r"<text bytes=.*>", line)
            if m:
                m = re.search(r"#REDIRECT \[\[.*\]\]", line)  # rewrite as above
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
                        logging.debug("ADDED: " + line)
                        line = re.sub(r"\n", r" ", line)
                        lines.append(line)
                    else:
                        logging.debug("REJECTED")
                else:
                    logging.debug("INSIDE TABLE - REJECTED")

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

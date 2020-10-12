import re


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
                     ("^\|.*", ""),  # tables
                     (r"\{\{.*?\}\}", ""),
                     (r"&lt;ref(.*?)&gt;(.*?);/ref&gt;", ""),  # citations
                     (r"&quot;(.*?)&quot;", r"\1"),
                     (r"={2,5}(.*?)={2,5}", r"\1"),
                     (r"&lt;(.*?)&gt;", ""),
                     (r"^(\{\{).*", ""),  # Library resources box
                     (r"^}}$", "")]

inside_text = False
title = None

lines = []
articles = []

# prepist do classy parser s atributmi state?

with open("../data/test.xml") as file:
    for line in file:
        print("IN: " + line, end="")
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
            print("RESULT\n" + "".join(lines))
            lines = []
            continue
        if inside_text:
            for regex in replacing_regexes:
                line = re.sub(regex[0], regex[1], line)
            if not line.isspace():
                print("ADDED: " + line, end="")
                lines.append(line)
            else:
                print("REJECTED")




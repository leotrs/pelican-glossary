"""
Builds a glossary page containing definition lists found in articles
and pages, and adds a `definitions` variable visible to all page templates.

"""

from pelican import signals
from bs4 import BeautifulSoup


class Definitions():
    definitions = []
    exclude = []


def make_title(def_title):
    return def_title.text


def make_link(def_title, url):
    a_tag = def_title.findChild('a')
    if a_tag and a_tag['href']:
        return url + a_tag['href']
    else:
        return None


def make_def(def_title):
    return ''.join(str(t) for t in def_title.find_next('dd').contents)


def set_definitions(generator, metadata):
    generator.context['definitions'] = Definitions.definitions


def get_excludes(pelican):
    Definitions.exclude = pelican.settings.get('GLOSSARY_EXCLUDE', [])


def parse_all(content_list):
    for content in content_list:
        soup = BeautifulSoup(content.content, 'html.parser')

        for def_list in soup.find_all('dl'):
            defns = []
            for def_title in def_list.find_all('dt'):
                if def_title.text not in Definitions.exclude:
                    defns.append(
                        {'title': make_title(def_title),
                         'link': make_link(def_title, content.url),
                         'definition': make_def(def_title),
                         'source': content})

            for defn in defns:
                defn['see_also'] = [d for d in defns if d is not defn]

            Definitions.definitions += defns


def parse_articles(generator):
    return parse_all(generator.articles)


def parse_pages(generator):
    return parse_all(generator.pages)


def register():
    signals.initialized.connect(get_excludes)
    signals.article_generator_finalized.connect(parse_articles)
    signals.page_generator_finalized.connect(parse_pages)
    signals.page_generator_context.connect(set_definitions)

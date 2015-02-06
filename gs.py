from bs4 import BeautifulSoup
from urllib import urlencode
from collections import OrderedDict
import requests

BASE_URL = 'https://scholar.google.ca'
CITATIONS_URL_EXTENSION = '/citations?'

class Config(object):
    """
    Settings for GS
    """
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        pass


class AuthorQuery(object):
    """
    Represents a query based on the author name and description.
    Pass an author name and optionally a  description string.
    The string should be either the domain name of the university or the name of the university.
    If no description information is known, pass only an author name.
    >>> author_query = AuthorQuery('A Einstein', 'princeton.edu')
    >>> type(author_query) is AuthorQuery
    True
    >>> author_query = AuthorQuery('A Einstein')
    >>> type(author_query) is AuthorQuery
    True
    """
    def __init__(self, author_name, author_description=None):
        query_dict = OrderedDict()
        if author_description:
            query_dict['mauthors'] = author_name + ' ' + author_description
        else:
            query_dict['mauthors'] = author_name
        query_dict['hl'] = 'en'
        query_dict['view_op'] = 'search_authors'
        self.query_URL = self.get_url(query_dict)
        self.search_results = self.search(self.query_URL)

    def get_url(self, query_dict):
        """
        Generate the http request URL submittable to GS
        """
        query_URL = BASE_URL + CITATIONS_URL_EXTENSION + urlencode(query_dict)
        return query_URL

    def search(self, url):
        """
        Return an array of authors found in the search
        """
        # set user agent, GS blocks if not set
        header = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'}
        response = requests.get(url, headers=header)
        if response.status_code != 200:
            raise requests.HTTPError
        query_resp_parser = AuthorQueryResponseParser(response.text)
        return query_resp_parser.results

    def get_first_result_url(self):
        """
        Return the URL of the first search results
        """
        return self.get_nth_result_url(0)

    def get_nth_result_url(self, index):
        """
        Return the URL of the nth search result
        """
        return self.search_results[index]['scholar_page']


class AuthorQueryResponseParser(object):
    """
    Parses the raw response of an AuthorQuery.
    Receives HTML response from author search.
    Returns an OrderedDict of authors found.
    """
    def __init__(self, raw_search_results):
        soup = BeautifulSoup(raw_search_results)
        self.results = self.parse(soup)

    def parse(self, soup):
        parsed_results = []
        author_divs = soup.find_all(class_='gsc_1usr')
        for author_div in author_divs:
            author = {}
            author['name'] = self.parse_name(author_div)
            author['scholar_page'] = self.parse_author_link(author_div)
            author['affiliation'] = self.parse_affiliation(author_div)
            author['research_areas'] = self.parse_research_areas(author_div)
            author['email_domain'] = self.parse_email_domain(author_div)
            parsed_results.append(author)
        return parsed_results

    def parse_name(self, author_div):
        name_h3 = author_div.find(class_='gsc_1usr_name')
        first_name = unicode(name_h3.a.string)
        last_name = unicode(name_h3.a.span.string)
        return first_name + last_name

    def parse_author_link(self, author_div):
        link_h3 = author_div.find(class_='gsc_1usr_name')
        link_suffix = unicode(link_h3.a['href'])
        return BASE_URL + link_suffix

    def parse_affiliation(self, author_div):
        affiliation_div = author_div.find(class_='gsc_1usr_aff')
        affiliation = unicode(affiliation_div.string)
        return affiliation

    def parse_research_areas(self, author_div):
        research_areas_div = author_div.find(class_='gsc_1usr_int')
        research_areas_a = research_areas_div.find_all('a')
        research_areas = []
        for research_area_a in research_areas_a:
            research_area = unicode(research_area_a.string)
            research_areas.append(research_area)
        return research_areas

    def parse_email_domain(self, author_div):
        email_domain_div = author_div.find(class_='gsc_1usr_emlb')
        email_domain = unicode(email_domain_div.string)
        return email_domain

class Author(object):
    """
    Represents an author
    """
    def __init__(self, author_url):
        pass

if __name__ == '__main__':
    author_query = AuthorQuery('Victor Guana')
    author = Author(author_query.first_result_URL)

from bs4 import BeautifulSoup
from urllib import urlencode
from urlparse import parse_qs, urlparse
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
    Pass an author name and optionally a description string and optionally 
    a list of labels.
    The description string should be either the domain name of the 
    university or the name of the university.
    If no description information is known, pass only an author name.
    >>> author_query = AuthorQuery('A Einstein', description='princeton.edu')
    >>> type(author_query) is AuthorQuery
    True
    >>> author_query = AuthorQuery('A Einstein')
    >>> type(author_query) is AuthorQuery
    True
    >>> author_query = AuthorQuery('A Einstein', labels=['Physics'])
    >>> type(author_query) is AuthorQuery
    True
    >>> author_query.query_URL == 'https://scholar.google.ca/citations?mauthors=A+Einstein+label%3APhysics&hl=en&view_op=search_authors'
    True
    >>> search_results = author_query.search()
    >>> search_results.get_first_result_url()
    'https://scholar.google.ca/citations?user=qc6CJjYAAAAJ&hl=en'
    >>> search_results.get_nth_result_url(2)
    'https://scholar.google.ca/citations?user=H5JpaNUAAAAJ&hl=en'
    >>> search_results.get_num_hits()
    '3'
    """
    def __init__(self, author_name, author_description=None, labels=None):
        query_dict = OrderedDict()
        if author_description:
            query_dict['mauthors'] = author_name + ' ' + author_description
        else:
            query_dict['mauthors'] = author_name

        if labels is not None:
            formatted_labels = self.format_labels(labels)
            query_dict['mauthors'] += formatted_labels

        query_dict['hl'] = 'en'
        query_dict['view_op'] = 'search_authors'
        self.query_URL = self.get_url(query_dict)

    def format_labels(self, labels):
        """
        Return labels formatted for url.
        """
        formatted_labels = ""
        for label in labels:
            formatted_labels += ' label:' + label.replace(' ', '_')
        return formatted_labels

    def get_url(self, query_dict):
        """
        Generate the http request URL submittable to GS
        """
        query_URL = BASE_URL + CITATIONS_URL_EXTENSION + urlencode(query_dict)
        return query_URL

    def search(self, url=None):
        """
        Return an array of authors found in the search
        """
        header = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'}
        if url is None:
            response = requests.get(self.query_URL, headers=header)
        else:
            response = requests.get(url, headers=header)
        if response.status_code != 200:
            raise requests.HTTPError
        query_resp_parser = AuthorQueryResponseParser(response.text)
        self.search_results = query_resp_parser.get_results()
        return self.search_results

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

    def get_num_hits(self):
        return self.search_results.length


class AuthorQueryResponseParser(object):
    """
    Parses the html payload of an author query.
    Returns an OrderedDict of authors found.
    """
    def __init__(self, payload):
        soup = BeautifulSoup(payload)
        self.results = self.parse(soup)

    def get_results(self):
        return self.results

    def parse(self, soup):
        parsed_results = []
        author_divs = soup.find_all(class_='gsc_1usr')
        for author_div in author_divs:
            author = OrderedDict()
            author['name'] = self.parse_name(author_div)
            author['scholar_page'] = self.parse_author_link(author_div)
            author['affiliation'] = self.parse_affiliation(author_div)
            author['research_areas'] = self.parse_research_areas(author_div)
            author['email_domain'] = self.parse_email_domain(author_div)
            parsed_results.append(author)
        return parsed_results

    def parse_name(self, author_div):
        # name format varies. sometimes the last name is in a span,
        # other times both the first and last are in the same tag.
        name_h3 = author_div.find(class_='gsc_1usr_name')
        try:
            name = unicode(name_h3.text)
            return name
        except AttributeError:
            print "Couldn't parse name"
            return ''

    def parse_author_link(self, author_div):
        link_h3 = author_div.find(class_='gsc_1usr_name')
        try:
            link_suffix = unicode(link_h3.a['href'])
            return BASE_URL + link_suffix
        except AttributeError:
            print "Couldn't parse author URL."
            return ''

    def parse_affiliation(self, author_div):
        affiliation_div = author_div.find(class_='gsc_1usr_aff')
        try:
            affiliation = unicode(affiliation_div.text)
            return affiliation
        except AttributeError:
            print "Couldn't parse author affiliation."
            return ''

    def parse_research_areas(self, author_div):
        research_areas_div = author_div.find(class_='gsc_1usr_int')
        try:
            research_areas_a = research_areas_div.find_all('a')
        except AttributeError:
            print "Couldn't parse research areas."
            return []
        research_areas = []
        for research_area_a in research_areas_a:
            try:
                research_area = unicode(research_area_a.string)
            except AttributeError as e:
                print e
                research_area = ''
                continue
            research_areas.append(research_area)
        return research_areas

    def parse_email_domain(self, author_div):
        email_domain_div = author_div.find(class_='gsc_1usr_emlb')
        try:
            email_domain = unicode(email_domain_div.string)
            return email_domain
        except AttributeError:
            print "Couldn't parse author email."
            return ''


class Author(object):
    """
    Represents an author
    """
    def __init__(self, author_url):
        query_dict = OrderedDict()
        self.author_url = author_url + '&cstart=0&pagesize=100'  # get first 100 articles


class AuthorParser(object):
    """
    Parses the html payload of an author page on GS.
    """
    def __init__(self, payload):
        soup = BeautifulSoup(payload)
        self.result = self.parse(soup)

    def get_result(self):
        return self.result

    def parse(self, soup):
        author = OrderedDict()
        author['author_name'] = self.parse_name(soup)
        author['author_UID'] = self.parse_author_uid(soup)
        author['article_UIDs'] = self.parse_article_uid(soup)
        author['bio'] = self.parse_author_bio(soup)
        author['research_interests'] = self.parse_author_research_interests(soup)
        author['total_citations'] = self.parse_author_total_citations(soup)
        author['co_authors'] = self.parse_co_authors(soup)
        author['h_index'] = self.parse_h_index(soup)
        author['i10_index'] = self.parse_i10_index(soup)
        author['publications_by_year'] = self.parse_publications_by_year(soup)
        author['author_image_URL'] = self.parse_author_image_URL(soup)
        return author

    def parse_name(self, soup):
        name_div = soup.find(id='gsc_prf_in')
        try:
            name = name_div.text
            return name
        except AttributeError:
            print "Couldn't parse name."
            return ''

    def parse_author_uid(self, soup):
        try:
            link_tag = soup.find(attrs={'rel': 'canonical'})
            href = link_tag.get('href')
            url_components = urlparse(href)
            params = parse_qs(url_components.query)
            uid = params['user'][0]
            return uid
        except AttributeError:
            print "Couldn't parse author UID"
            return ''

    def parse_article_uid(self, soup):
        pass

    def parse_author_bio(self, soup):
        try:
            bio_div = soup.find_all(class_='gsc_prf_il')[0]
            bio = bio_div.text
            print bio
            return bio
        except AttributeError:
            print "Couldn't parse author bio."
            return ''

    def parse_author_research_interests(self, soup):
        try:
            interests_div = soup.find_all(class_='gsc_prf_il')[1]
            interests = []
            for a_tag in interests_div.find_all('a'):
                interests.append(a_tag.text)
            return interests
        except AttributeError:
            print "Couldn't parse interests."
            return []

    def parse_author_total_citations(self, soup):
        try:
            table = soup.find(id='gsc_rsb_st')
            citations_row = table.find_all('tr')[1]
            total_citations = citations_row.find_all('td')[1].text
            return total_citations
        except AttributeError:
            print "Couldn't parse total citations."
            return ''

    def parse_co_authors(self, soup):
        pass

    def parse_h_index(self, soup):
        pass

    def parse_i10_index(self, soup):
        pass

    def parse_publications_by_year(self, soup):
        pass

    def parse_author_image_URL(self, soup):
        pass









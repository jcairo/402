#!/usr/bin/env python
from bs4 import BeautifulSoup
from urllib import urlencode
from urlparse import parse_qs, urlparse
from collections import OrderedDict
import requests
import json
import sys
import time


class GSHelper(object):
    """
    Helper methods and constants for the GS module.
    """

    BASE_URL = 'https://scholar.google.ca'
    CITATIONS_URL_EXTENSION = '/citations?'
    PUB_RESULTS_PER_PAGE = 100

    @staticmethod
    def get_url(url):
        """
        Requests page at url provided, passes back html
        """
        header = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'}
        response = requests.get(url, headers=header)
        if response.status_code != 200:
            raise requests.HTTPError
        return response.text

    @staticmethod
    def search_author(author_name, description=None, labels=None):
        author_name = sys.argv[2]
        if description is not None:
            # Author name and description are part of the same
            # field in the gs url.
            author_name = author_name + description
        if labels is None:
            author_query = AuthorQuery(author_name, AuthorQueryParser)
        else:
            author_query = AuthorQuery(author_name, AuthorQueryParser, labels)
        return author_query.to_json()

    @staticmethod
    def get_author(author_url):
        author = Author(author_url, AuthorParser)
        return author.to_json()

    @staticmethod
    def get_publications(author_uid, page):
        author_pubs = AuthorPublications(author_uid, page, AuthorPublicationsParser)
        return author_pubs.to_json()

    @staticmethod
    def get_publication(author_uid, publication_uid):
        author_pub = AuthorPublication(author_uid, publication_uid, AuthorPublicationParser)
        return author_pub.to_json()

    @staticmethod
    def get_coauthors(author_uid):
        author_coauthors = AuthorCoAuthors(author_uid, AuthorCoAuthorsParser)
        return author_coauthors.to_json()


class ParseHelper(object):
    @staticmethod
    def get_parameter_from_url(url, key):
        """
        Returns an attribute specified in a URL.
        """
        url_components = urlparse(url)
        query_components = url_components.query
        params = parse_qs(query_components)
        value = params[key]
        return value[0]

    @staticmethod
    def exception_wrapper(func):
        """
        Wraps any functions which may cause exceptions in an
        exception handler.
        """
        def exception_wrapped_func(self, author_div):
            try:
                result = func(self, author_div)
            except AttributeError, ValueError:
                class_name = func.__class__
                function_name = func.__name__
                print "Parsing error while executing {0}.{1}".format(class_name, function_name)
                return ''
            return result
        return exception_wrapped_func

    @staticmethod
    def timeit(func):
        def timed_func(self, soup):
            start = time.clock()
            result = func(self, soup)
            end = time.clock()
            print end - start
            return result
        return timed_func


class ScholarObject(object):
    """
    Base class for Google Scholar objects.
    """
    def get_results_dict(self):
        return self.results_dict

    def to_json(self):
        return json.dumps(self.results_dict, indent=4)


class Parser(object):
    """
    Base class for parser objects.
    """
    def get_results(self):
        return self.results


class AuthorQuery(ScholarObject):
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
    def __init__(self, author_name, author_query_parser, author_description=None, labels=None):
        self.query_url = self.get_url(author_name, author_description, labels)
        html = GSHelper.get_url(self.query_url)
        self.results_dict = OrderedDict()
        self.results_dict['author_search_name'] = author_name
        self.results_dict['author_search_description'] = author_description
        self.results_dict['author_search_labels'] = labels
        query_resp_parser = author_query_parser(html, self.results_dict)
        self.search_results = query_resp_parser.get_results()

    def format_labels(self, labels):
        """
        Return labels formatted for url.
        """
        formatted_labels = ""
        for label in labels:
            formatted_labels += ' label:' + label.replace(' ', '_')
        return formatted_labels

    def get_url(self, author_name, author_description=None, labels=None):
        """
        Generate the http request URL submittable to GS
        """
        results_dict = OrderedDict()
        if author_description:
            results_dict['mauthors'] = author_name + ' ' + author_description
        else:
            results_dict['mauthors'] = author_name
        if labels is not None:
            formatted_labels = self.format_labels(labels)
            results_dict['mauthors'] += formatted_labels
        results_dict['hl'] = 'en'
        results_dict['view_op'] = 'search_authors'
        query_URL = GSHelper.BASE_URL + GSHelper.CITATIONS_URL_EXTENSION + urlencode(results_dict)
        return query_URL

    def get_first_result_url(self):
        return self.get_nth_result_url(0)

    def get_nth_result_url(self, index):
        return self.search_results[index]['scholar_page']

    def get_num_hits(self):
        return self.search_results.length

    def get_first_result_uid(self):
        return self.get_nth_result_uid(0)

    def get_nth_result_uid(self, index):
        return self.search_results[index]['uid']


class AuthorQueryParser(Parser):
    """
    Parses the html payload of an author query.
    Returns an OrderedDict of authors found.
    """
    def __init__(self, payload, query_dict):
        soup = BeautifulSoup(payload, 'lxml')
        query_dict['search_results'] = self.parse(soup, query_dict)

    def parse(self, soup, query_dict):
        parsed_results = []
        author_divs = soup.find_all(class_='gsc_1usr')
        for author_div in author_divs:
            author = OrderedDict()
            author['name'] = self.parse_name(author_div)
            author['scholar_page'] = self.parse_author_link(author_div)
            author['affiliation'] = self.parse_affiliation(author_div)
            author['research_areas'] = self.parse_research_areas(author_div)
            author['email_domain'] = self.parse_email_domain(author_div)
            author['uid'] = self.parse_uid(author_div)
            parsed_results.append(author)
        self.results = parsed_results
        return parsed_results

    @ParseHelper.exception_wrapper
    def parse_uid(self, author_div):
        link_h3 = author_div.find(class_='gsc_1usr_name')
        link_suffix_url = link_h3.a['href']
        uid = ParseHelper.get_parameter_from_url(link_suffix_url, 'user')
        return uid

    @ParseHelper.exception_wrapper
    def parse_name(self, author_div):
        # name format varies. sometimes the last name is in a span,
        # other times both the first and last are in the same tag.
        name_h3 = author_div.find(class_='gsc_1usr_name')
        name = name_h3.text
        return name

    @ParseHelper.exception_wrapper
    def parse_author_link(self, author_div):
        link_h3 = author_div.find(class_='gsc_1usr_name')
        link_suffix = link_h3.a['href']
        return GSHelper.BASE_URL + link_suffix

    @ParseHelper.exception_wrapper
    def parse_affiliation(self, author_div):
        affiliation_div = author_div.find(class_='gsc_1usr_aff')
        affiliation = affiliation_div.text
        return affiliation

    @ParseHelper.exception_wrapper
    def parse_research_areas(self, author_div):
        research_areas_div = author_div.find(class_='gsc_1usr_int')
        research_areas_a = research_areas_div.find_all('a')
        research_areas = []
        for research_area_a in research_areas_a:
            try:
                research_area = research_area_a.string
            except AttributeError as e:
                print e
                research_area = ''
                continue
            research_areas.append(research_area)
        return research_areas

    @ParseHelper.exception_wrapper
    def parse_email_domain(self, author_div):
        email_domain_div = author_div.find(class_='gsc_1usr_emlb')
        email_domain = email_domain_div.string
        return email_domain


class Author(ScholarObject):
    """
    Represents an author.
    Pass in an author page url on GS.
    Get parsed information by calling Author.get_author_info()
    """
    def __init__(self, author_uid, author_parser):
        self.results_dict = OrderedDict()
        self.author_url = self.get_author_url(author_uid)
        author_html = GSHelper.get_url(self.author_url)
        self.author_parser = author_parser(author_html, self.results_dict)

    def get_author_url(self, author_uid):
        """
        Returns the url of the authors homepage based on their uid.
        """
        query_dict = OrderedDict()
        query_dict['user'] = author_uid
        query_dict['hl'] = 'en'
        return GSHelper.BASE_URL + GSHelper.CITATIONS_URL_EXTENSION + urlencode(query_dict)


class AuthorParser(Parser):
    """
    Parses the html payload of an author page on GS.
    """
    def __init__(self, payload, author_dict):
        soup = BeautifulSoup(payload, 'lxml')
        self.results = self.parse(soup, author_dict)

    def parse(self, soup, author_dict):
        author_dict['author_name'] = self.parse_name(soup)
        author_dict['author_UID'] = self.parse_author_uid(soup)
        author_dict['bio'] = self.parse_author_bio(soup)
        author_dict['research_interests'] = self.parse_author_research_interests(soup)
        author_dict['total_citations'] = self.parse_author_total_citations(soup)
        author_dict['h_index'] = self.parse_h_index(soup)
        author_dict['i10_index'] = self.parse_i10_index(soup)
        author_dict['publications_by_year'] = self.parse_publications_by_year(soup)
        author_dict['author_image_URL'] = self.parse_author_image_URL(soup)
        return author_dict

    @ParseHelper.exception_wrapper
    def parse_name(self, soup):
        name_div = soup.find(id='gsc_prf_in')
        name = name_div.text
        return name

    @ParseHelper.exception_wrapper
    def parse_author_uid(self, soup):
        link_tag = soup.find(attrs={'rel': 'canonical'})
        url = link_tag.get('href')
        uid = ParseHelper.get_parameter_from_url(url, 'user')
        return uid

    @ParseHelper.exception_wrapper
    def parse_author_bio(self, soup):
        bio_div = soup.find_all(class_='gsc_prf_il')[0]
        bio = bio_div.text
        return bio

    @ParseHelper.exception_wrapper
    def parse_author_research_interests(self, soup):
        interests_div = soup.find_all(class_='gsc_prf_il')[1]
        interests = []
        for a_tag in interests_div.find_all('a'):
            interests.append(a_tag.text)
        return interests

    @ParseHelper.exception_wrapper
    def parse_author_total_citations(self, soup):
        table = soup.find(id='gsc_rsb_st')
        citations_row = table.find_all('tr')[1]
        total_citations = citations_row.find_all('td')[1].text
        return total_citations

    @ParseHelper.exception_wrapper
    def parse_co_authors_page_link(self, soup):
        co_authors_link_tag = soup.find(class_='gsc_rsb_lc')
        co_authors_link = GSHelper.BASE_URL + co_authors_link_tag.get('href')
        return co_authors_link

    @ParseHelper.exception_wrapper
    def parse_h_index(self, soup):
        table = soup.find(id='gsc_rsb_st')
        h_index_row = table.find_all('tr')[2]
        h_index = h_index_row.find_all('td')[1].text
        return h_index

    @ParseHelper.exception_wrapper
    def parse_i10_index(self, soup):
        table = soup.find(id='gsc_rsb_st')
        i10_index_row = table.find_all('tr')[3]
        i10_index = i10_index_row('td')[1].text
        return i10_index

    @ParseHelper.exception_wrapper
    def parse_publications_by_year(self, soup):
        pubs_by_year = []
        graph_div = soup.find(id='gsc_g')
        years_div = graph_div.find(id='gsc_g_x')
        years = years_div.find_all('span')
        counts_div = graph_div.find(id='gsc_g_bars')
        counts = counts_div.find_all('a')
        for year, count in zip(years, counts):
            result_dict = OrderedDict()
            result_dict['year'] = int(year.text)
            result_dict['count'] = int(count.text)
            pubs_by_year.append(result_dict)
        return pubs_by_year

    @ParseHelper.exception_wrapper
    def parse_author_image_URL(self, soup):
        img_tag = soup.find(id='gsc_prf_pup')
        image_url = GSHelper.BASE_URL + img_tag['src']
        return image_url


class AuthorCoAuthors(ScholarObject):
    def __init__(self, author_uid, author_coauthors_parser):
        self.results_dict = OrderedDict()
        self.results_dict['author_uid'] = author_uid
        query_url = self.get_page_url(author_uid)
        html = GSHelper.get_url(query_url)
        self.coauthor_parser = author_coauthors_parser(html, self.results_dict)

    def get_page_url(self, author_uid):
        url = GSHelper.BASE_URL + GSHelper.CITATIONS_URL_EXTENSION
        query_dict = OrderedDict()
        query_dict['view_op'] = 'list_colleagues'
        query_dict['hl'] = 'en'
        query_dict['user'] = author_uid
        query_url = url + urlencode(query_dict)
        return query_url


class AuthorCoAuthorsParser(Parser):
    def __init__(self, payload, coauthors_dict):
        soup = BeautifulSoup(payload, 'lxml')
        self.results = self.parse(soup, coauthors_dict)

    def parse(self, soup, coauthors_dict):
        coauthors_dict['coauthors'] = self.parse_coauthors(soup)
        return coauthors_dict

    def parse_coauthors(self, soup):
        coauthors = []
        try:
            coauthor_div = soup.find(id='gsc_ccl')
            coauthor_divs = coauthor_div.find_all(class_='gs_scl')
        except AttributeError:
            print "Couldn't find coauthors div."
            return coauthors
        for coauthor in coauthor_divs:
            coauthor_dict = OrderedDict()
            coauthor_dict['author_uid'] = self.parse_author_uid(coauthor)
            coauthor_dict['author_url'] = self.parse_author_url(coauthor)
            coauthor_dict['name'] = self.parse_coauthor_name(coauthor)
            coauthor_dict['citation_count'] = self.parse_coauthor_citations(coauthor)
            coauthor_dict['domain'] = self.parse_domain(coauthor)
            coauthor_dict['bio'] = self.parse_bio(coauthor)
            coauthor_dict['author_image_url'] = self.parse_image_url(coauthor)
            coauthors.append(coauthor_dict)
        return coauthors

    @ParseHelper.exception_wrapper
    def parse_author_uid(self, coauthor_soup):
        coauthor_url = coauthor_soup.div.a.get('href')
        coauthor_uid =  ParseHelper.get_parameter_from_url(coauthor_url, 'user')
        return coauthor_uid

    @ParseHelper.exception_wrapper
    def parse_author_url(self, coauthor_soup):
        coauthor_url = GSHelper.BASE_URL + coauthor_soup.find(class_='gsc_1usr_name').a.get('href')
        coauthor_url = coauthor_url
        return coauthor_url

    @ParseHelper.exception_wrapper
    def parse_coauthor_name(self, coauthor_soup):
        coauthor_name = coauthor_soup.find(class_='gsc_1usr_name').text
        return coauthor_name

    @ParseHelper.exception_wrapper
    def parse_coauthor_citations(self, coauthor_soup):
        citation_div = coauthor_soup.find(class_='gsc_1usr_cby')
        citation_count = int(citation_div.text.split()[-1])
        return citation_count

    @ParseHelper.exception_wrapper
    def parse_domain(self, coauthor_soup):
        domain_div = coauthor_soup.find(class_='gsc_1usr_emlb')
        domain = domain_div.text
        return domain

    @ParseHelper.exception_wrapper
    def parse_bio(self, coauthor_soup):
        bio_div = coauthor_soup.find(class_='gsc_1usr_aff')
        bio = bio_div.text
        return bio

    @ParseHelper.exception_wrapper
    def parse_image_url(self, coauthor_soup):
        image_relative_url = coauthor_soup.div.a.img.get('src')
        image_url = GSHelper.BASE_URL + image_relative_url
        return image_url


class AuthorPublications(ScholarObject):
    def __init__(self, author_uid, page, author_publications_parser):
        self.results_dict = OrderedDict()
        self.results_dict['author_uid'] = author_uid
        self.results_dict['page'] = page
        query_url = self.get_page_url(author_uid, page)
        html = GSHelper.get_url(query_url)
        self.author_pubs_parser = author_publications_parser(html, self.results_dict)

    def get_page_url(self, author_uid, page):
        url = GSHelper.BASE_URL + GSHelper.CITATIONS_URL_EXTENSION
        query_dict = OrderedDict()
        query_dict['user'] = author_uid
        query_dict['hl'] = 'en'
        query_dict['cstart'] = page * GSHelper.PUB_RESULTS_PER_PAGE
        query_dict['pagesize'] = GSHelper.PUB_RESULTS_PER_PAGE
        query_url = url + urlencode(query_dict)
        return query_url


class AuthorPublicationsParser(Parser):
    def __init__(self, payload, pubs_dict):
        soup = BeautifulSoup(payload, 'lxml')
        self.results = self.parse(soup, pubs_dict)

    def parse(self, soup, pubs_dict):
        pubs_dict['publications'] = self.parse_publications(soup)
        return pubs_dict

    def parse_publications(self, soup):
        article_uids = []
        try:
            article_table = soup.find(id='gsc_a_t')
            articles = article_table.tbody.find_all('tr')
        except AttributeError:
            print "Couldn't parse publications."
            return article_uids
        for article in articles:
            article_dict = OrderedDict()
            article_dict['url'] = self.parse_article_url(article)
            article_dict['id'] = self.parse_article_uid(article)
            article_dict['title'] = self.parse_article_title(article)
            article_dict['cited'] = self.parse_citation_count(article)
            article_dict['year'] = self.parse_year(article)
            article_uids.append(article_dict)
        return article_uids

    @ParseHelper.exception_wrapper
    def parse_article_url(self, article_soup):
        article_url = article_soup.find('td').a.get('href')
        url = GSHelper.BASE_URL + article_url
        return url

    @ParseHelper.exception_wrapper
    def parse_article_title(self, article_soup):
        title = article_soup.find('td').a.text
        return title

    @ParseHelper.exception_wrapper
    def parse_article_uid(self, article_soup):
        href = article_soup.find('td').a.get('href')
        uid_param = ParseHelper.get_parameter_from_url(href, 'citation_for_view')
        uid = uid_param.split(':')[-1]
        return uid

    @ParseHelper.exception_wrapper
    def parse_citation_count(self, article_soup):
        citations_count = article_soup.find_all('td')[1].a.text
        try:
            count = int(citations_count)
        except ValueError:
            count = 0
        return count

    @ParseHelper.exception_wrapper
    def parse_year(self, article_soup):
        year = article_soup.find(class_='gsc_a_h').text
        try:
            year = int(year)
        except ValueError:
            year = ''
        return year


class AuthorPublication(ScholarObject):
    def __init__(self, author_uid, publication_uid, author_publication_parser):
        self.results_dict = OrderedDict()
        self.results_dict['author_uid'] = author_uid
        self.results_dict['publication_uid'] = publication_uid
        query_url = self.get_page_url(author_uid, publication_uid)
        html = GSHelper.get_url(query_url)
        self.author_pub_parser = author_publication_parser(html, self.results_dict)

    def get_page_url(self, author_uid, publication_uid):
        url = GSHelper.BASE_URL + GSHelper.CITATIONS_URL_EXTENSION
        query_dict = OrderedDict()
        query_dict['view_op'] = 'view_citation'
        query_dict['hl'] = 'en'
        query_dict['user'] = author_uid
        query_dict['citation_for_view'] = author_uid + ':' + publication_uid
        query_url = url + urlencode(query_dict)
        return query_url


class AuthorPublicationParser(Parser):
    def __init__(self, payload, pub_dict):
        soup = BeautifulSoup(payload, 'lxml')
        self.results = self.parse(soup, pub_dict)

    def parse(self, soup, pub_dict):
        pub_dict['publication_url'] = self.parse_publication_url(soup)
        pub_dict['authors'] = self.parse_authors(soup)
        pub_dict['publication_date'] = self.parse_publication_date(soup)
        pub_dict['journal_name'] = self.parse_journal_name(soup)
        pub_dict['page_range'] = self.parse_page_range(soup)
        pub_dict['publisher'] = self.parse_publisher(soup)
        pub_dict['partial_abstract'] = self.parse_abstract(soup)
        pub_dict['citation_count'] = self.parse_citation_count(soup)
        pub_dict['citations_by_year'] = self.parse_citations_by_year(soup)
        return pub_dict

    @ParseHelper.exception_wrapper
    def parse_publication_url(self, soup):
        link_div = soup.find(id='gsc_title').a.get('href')
        return link_div

    @ParseHelper.exception_wrapper
    def parse_authors(self, soup):
        authors_text = soup.find('div', text='Authors').next_sibling.text
        authors = authors_text.split(',')
        return authors

    @ParseHelper.exception_wrapper
    def parse_publication_date(self, soup):
        date = soup.find('div', text='Publication date').next_sibling.text
        return date

    @ParseHelper.exception_wrapper
    def parse_journal_name(self, soup):
        journal_name = soup.find('div', text='Journal').next_sibling.text
        return journal_name

    @ParseHelper.exception_wrapper
    def parse_page_range(self, soup):
        page_range = soup.find('div', text='Pages').next_sibling.text
        return page_range

    @ParseHelper.exception_wrapper
    def parse_publisher(self, soup):
        publisher = soup.find('div', text='Publisher').next_sibling.text
        return publisher

    @ParseHelper.exception_wrapper
    def parse_abstract(self, soup):
        abstract = soup.find('div', text='Description').next_sibling.text
        return abstract

    @ParseHelper.exception_wrapper
    def parse_citation_count(self, soup):
        count_string = soup.find('div', text='Total citations').next_sibling.div.a.text
        count = int(count_string.split()[-1])
        return count

    @ParseHelper.exception_wrapper
    def parse_citations_by_year(self, soup):
        citations_count = []
        graph = soup.find(id='gsc_graph_bars')
        years = graph.find_all('span')
        counts = graph.find_all('a')
        for year, count in zip(years, counts):
            result_dict = OrderedDict()
            try:
                result_dict['year'] = int(year.text)
                result_dict['count'] = int(count.text)
                citations_count.append(result_dict)
            except AttributeError, TypeError:
                print "Couldn't parse publication citation by year."
                break
        return citations_count


if __name__ == '__main__':
    if sys.argv[1] == '--search':
        # cli args = search, author_name
        # python gs.py search 'V Guana'
        author_name = sys.argv[2]
        print GSHelper.search_author(author_name)

    if sys.argv[1] == '--author':
        # /author/search
        # cli args = author, author_uid
        # python gs.py author 'https://scholar.google.ca/citations?user=Q0ZsJ_UAAAAJ&hl=en'
        print GSHelper.get_author(sys.argv[2])

    if sys.argv[1] == '--coauthors':
        # /author/coauthors
        # cli args = coauthors, author_uid
        # python gs.py coauthors 'Q0ZsJ_UAAAAJ'
        author_uid = sys.argv[2]
        print GSHelper.get_coauthors(author_uid)

    if sys.argv[1] == '--publications':
        # /author/publications
        # cli args = publications, author_uid, page
        # python gs.py publications 'Q0ZsJ_UAAAAJ' '0'
        author_uid = sys.argv[2]
        try:
            page = sys.argv[3]
        except IndexError:
            page = 0
        print GSHelper.get_publications(author_uid, page)

    if sys.argv[1] == '--publication':
        # /author/publication
        # cli args = publication, author_uid, pub_uid
        # python gs.py publication 'Q0ZsJ_UAAAAJ' 'u-x6o8ySG0sC'
        author_uid = sys.argv[2]
        publication_uid = sys.argv[3]
        print GSHelper.get_publication(author_uid, publication_uid)

#!/usr/bin/env python
from bs4 import BeautifulSoup
from urllib import urlencode
from urlparse import parse_qs, urlparse
from collections import OrderedDict
import requests
import json
import sys
import re


class GSHelper(object):
    """
    Settings for GS
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
    def search_author(author_name, labels=None):
        author_name = sys.argv[2]
        if labels is None:
            author_query = AuthorQuery(author_name)
        else:
            author_query = AuthorQuery(author_name, labels)
        return author_query.search_results

    @staticmethod
    def get_author(author_url):
        author = Author(author_url)
        return author.get_author_info()

    @staticmethod
    def get_publications(author_uid, page):
        author_pubs = AuthorPublications(author_uid, page)
        return author_pubs.get_pubs_info()

    @staticmethod
    def get_publication(author_uid, publication_uid):
        author_pub = AuthorPublication(author_uid, publication_uid)
        return author_pub.get_pub_info()

    @staticmethod
    def get_coauthors(author_uid):
        author_coauthors = AuthorCoAuthors(author_uid)
        return author_coauthors.get_coauthors_info()


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
        self.search(self.query_URL)

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
        query_URL = GSHelper.BASE_URL + GSHelper.CITATIONS_URL_EXTENSION + urlencode(query_dict)
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
        query_resp_parser = AuthorQueryParser(response.text)
        self.search_results = query_resp_parser.get_results()
        return self.search_results

    def get_first_result_uid(self):
        return self.get_nth_result_uid(0)

    def get_nth_result_uid(self, index):
        return self.search_results[index]['uid']

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

    def get_first_result_uid(self):
        return get_nth_result_uid(0)

    def get_nth_result_uid(self, index):
        return self.search_results[index]['uid']


class AuthorQueryParser(object):
    """
    Parses the html payload of an author query.
    Returns an OrderedDict of authors found.
    """
    def __init__(self, payload):
        soup = BeautifulSoup(payload, 'lxml')
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
            author['uid'] = self.parse_uid(author_div)
            parsed_results.append(author)
        return parsed_results

    def parse_uid(self, author_div):
        link_h3 = author_div.find(class_='gsc_1usr_name')
        try:
            link_suffix = unicode(link_h3.a['href'])
            url_components = urlparse(link_suffix)
            params = parse_qs(url_components.query)
            uid = params['user']
            return uid[0]
        except AttributeError:
            print "Couldn't parse author UID."
            return ''

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
            return GSHelper.BASE_URL + link_suffix
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
    Represents an author.
    Pass in an author page url on GS.
    Get parsed information by calling Author.get_author_info()
    """
    def __init__(self, author_uid):
        self.author_dict = OrderedDict()
        self.author_url = self.get_author_url(author_uid)
        author_html = GSHelper.get_url(self.author_url)
        self.author_parser = AuthorParser(author_html, self.author_dict)

    def get_author_info(self):
        return self.author_dict

    def get_author_url(self, author_uid):
        """
        Returns the url of the authors homepage based on their uid.
        """
        query_dict = OrderedDict()
        query_dict['user'] = author_uid
        query_dict['hl'] = 'en'
        return GSHelper.BASE_URL + GSHelper.CITATIONS_URL_EXTENSION + urlencode(query_dict)


class AuthorParser(object):
    """
    Parses the html payload of an author page on GS.
    """
    def __init__(self, payload, author_dict):
        soup = BeautifulSoup(payload, 'lxml')
        self.result = self.parse(soup, author_dict)

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

    def get_result(self):
        return self.result

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

    def parse_co_authors_page_link(self, soup):
        try:
            co_authors_link_tag = soup.find(class_='gsc_rsb_lc')
            co_authors_link = GSHelper.BASE_URL + co_authors_link_tag.get('href')
            return co_authors_link
        except AttributeError:
            print "Couldn't parse coauthors link."
            return ''

    def parse_h_index(self, soup):
        try:
            table = soup.find(id='gsc_rsb_st')
            h_index_row = table.find_all('tr')[2]
            h_index = h_index_row.find_all('td')[1].text
            return h_index
        except AttributeError:
            print "Couldn't parse h-index."
            return ''

    def parse_i10_index(self, soup):
        try:
            table = soup.find(id='gsc_rsb_st')
            i10_index_row = table.find_all('tr')[3]
            i10_index = i10_index_row('td')[1].text
            return i10_index
        except AttributeError:
            print "Couldn't parse i10-index."
            return ''

    def parse_publications_by_year(self, soup):
        pubs_by_year = []
        try:
            graph_div = soup.find(id='gsc_g')
            years_div = graph_div.find(id='gsc_g_x')
            year_spans = years_div.find_all('span')
            bars_div = graph_div.find(id='gsc_g_bars')
            bars = bars_div.find_all('a')
            for i, year_span in enumerate(year_spans):
                year = int(year_span.text)
                pubs_count = int(bars[i].text)
                pubs_by_year.append({"year": year, "count": pubs_count})
            return pubs_by_year
        except AttributeError:
            print "Couldn't parse publications by year."
            return ''

    def parse_author_image_URL(self, soup):
        try:
            img_tag = soup.find(id='gsc_prf_pup')
            image_url = GSHelper.BASE_URL + img_tag['src']
            return image_url
        except AttributeError:
            print "Couldn't parse image URL."
            return ''


class AuthorCoAuthors(object):
    def __init__(self, author_uid):
        self.coauthors_dict = OrderedDict()
        self.coauthors_dict['author_uid'] = author_uid
        query_url = self.get_page_url(author_uid)
        html = GSHelper.get_url(query_url)
        self.coauthor_parser = AuthorCoAuthorsParser(html, self.coauthors_dict)

    def get_page_url(self, author_uid):
        url = GSHelper.BASE_URL + GSHelper.CITATIONS_URL_EXTENSION
        query_dict = OrderedDict()
        query_dict['view_op'] = 'list_colleagues'
        query_dict['hl'] = 'en'
        query_dict['user'] = author_uid
        query_url = url + urlencode(query_dict)
        return query_url

    def get_coauthors_info(self):
        return self.coauthors_dict


class AuthorCoAuthorsParser(object):
    """
    CoAuthorsParser is passed a link to an authors coauthors page.
    It finds all coauthors names and UIDs.
    """
    def __init__(self, payload, coauthors_dict):
        soup = BeautifulSoup(payload, 'lxml')
        self.result = self.parse(soup, coauthors_dict)

    def get_result(self):
        return self.result

    def parse(self, soup, coauthors_dict):
        coauthors_dict['coauthors'] = self.parse_coauthors(soup)
        return coauthors_dict

    def parse_coauthors(self, soup):
        coauthors = []
        try:
            coauthor_div = soup.find(id='gsc_ccl')
            coauthor_divs = coauthor_div.find_all(class_='gs_scl')
        except AttributeError:
            print "Couldn't find coauthors."
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

    def parse_author_uid(self, coauthor_soup):
        try:
            coauthor_url = coauthor_soup.div.a.get('href')
            coauthor_uid =  ParseHelper.get_parameter_from_url(coauthor_url, 'user')
        except AttributeError:
            print "Couldn't parse coauthor UID."
            coauthor_uid = ''
        return coauthor_uid

    def parse_author_url(self, coauthor_soup):
        try:
            coauthor_url = GSHelper.BASE_URL + coauthor_soup.find(class_='gsc_1usr_name').a.get('href')
            coauthor_url = coauthor_url
        except AttributeError:
            print "Couldn't parse coauthor URL."
            coauthor_url = ''
        return coauthor_url

    def parse_coauthor_name(self, coauthor_soup):
        try:
            coauthor_name = coauthor_soup.find(class_='gsc_1usr_name').text
        except AttributeError:
            print "Couldn't parse coauthor name."
            coauthor_name = ''
        return coauthor_name

    def parse_coauthor_citations(self, coauthor_soup):
        try:
            citation_div = coauthor_soup.find(class_='gsc_1usr_cby')
            citation_count = int(citation_div.text.split()[-1])
        except AttributeError:
            print "Couldn't parse coauthor citation count."
            citation_count = ''
        return citation_count

    def parse_domain(self, coauthor_soup):
        try:
            domain_div = coauthor_soup.find(class_='gsc_1usr_emlb')
            domain = domain_div.text
        except AttributeError:
            print "Couldn't parse coauthor domain."
            domain = ''
        return domain

    def parse_bio(self, coauthor_soup):
        try:
            bio_div = coauthor_soup.find(class_='gsc_1usr_aff')
            bio = bio_div.text
        except AttributeError:
            print "Couldn't parse coauthor bio."
            bio = ''
        return bio

    def parse_image_url(self, coauthor_soup):
        try:
            image_relative_url = coauthor_soup.div.a.img.get('src')
            image_url = GSHelper.BASE_URL + image_relative_url
        except AttributeError:
            print "Couldn't parse author image url."
            image_url = ''
        return image_url


class AuthorPublications(object):
    def __init__(self, author_uid, page):
        self.pubs_dict = OrderedDict()
        self.pubs_dict['author_uid'] = author_uid
        self.pubs_dict['page'] = page
        query_url = self.get_page_url(author_uid, page)
        html = GSHelper.get_url(query_url)
        self.author_pubs_parser = AuthorPublicationsParser(html, self.pubs_dict)

    def get_pubs_info(self):
        return self.pubs_dict

    def get_page_url(self, author_uid, page):
        url = GSHelper.BASE_URL + GSHelper.CITATIONS_URL_EXTENSION
        query_dict = OrderedDict()
        query_dict['user'] = author_uid
        query_dict['hl'] = 'en'
        query_dict['cstart'] = page * GSHelper.PUB_RESULTS_PER_PAGE
        query_dict['pagesize'] = GSHelper.PUB_RESULTS_PER_PAGE 
        query_url = url + urlencode(query_dict)
        return query_url


class AuthorPublicationsParser(object):
    def __init__(self, payload, pubs_dict):
        soup = BeautifulSoup(payload, 'lxml')
        self.result = self.parse(soup, pubs_dict)

    def get_result(self):
        return self.result

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
        
    def parse_article_url(self, article_soup):
        try:
            article_url = article_soup.find('td').a.get('href')
            url = GSHelper.BASE_URL + article_url
        except AttributeError:
            print "Couldn't parse article url." 
            url = ''
        return url

    def parse_article_title(self, article_soup):
        try:
            title = article_soup.find('td').a.text
        except AttributeError:
            print "Couldn't parse article title."
            title = ''
        return title

    def parse_article_uid(self, article_soup):
        try:
            href = article_soup.find('td').a.get('href')
            uid_param = ParseHelper.get_parameter_from_url(href, 'citation_for_view')
            uid = uid_param.split(':')[-1]
        except AttributeError:
            print "Couldn't parse article UID."
            uid = ''
        return uid

    def parse_citation_count(self, article_soup):
        try:
            citations_count = article_soup.find_all('td')[1].a.text 
            try:
                count = int(citations_count)
            except ValueError:
                count = 0
        except AttributeError:
            print "Couldn't parse citations count."
            count = ''
        return count

    def parse_year(self, article_soup):
        try:
            year = article_soup.find(class_='gsc_a_h').text
            try:
                year = int(year)
            except ValueError:
                year = ''
        except AttributeError:
            print "Couldn't parse year."
            year = ''
        return year







class AuthorPublication(object):
    def __init__(self, author_uid, publication_uid):
        self.pub_dict = OrderedDict()
        self.pub_dict['author_uid'] = author_uid
        self.pub_dict['publication_uid'] = author_uid
        query_url = self.get_page_url(author_uid, publication_uid)
        html = GSHelper.get_url(query_url)
        self.author_pub_parser = AuthorPublicationParser(html, self.pub_dict)

    def get_pub_info(self):
        return self.pub_dict

    def get_page_url(self, author_uid, publication_uid):
        url = GSHelper.BASE_URL + GSHelper.CITATIONS_URL_EXTENSION
        query_dict = OrderedDict()
        query_dict['view_op'] = 'view_citation'
        query_dict['hl'] = 'en'
        query_dict['user'] = author_uid
        query_dict['citation_for_view'] = author_uid + ':' + publication_uid
        query_url = url + urlencode(query_dict)
        return query_url


class AuthorPublicationParser(object):
    def __init__(self, payload, pub_dict):
        soup = BeautifulSoup(payload, 'lxml')
        self.result = self.parse(soup, pub_dict)

    def get_result(self):
        return self.result

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

    def parse_publication_url(self, soup):
        try:
            link_div = soup.find(id='gsc_title').a.get('href')
        except AttributeError:
            print "Couldn't parse publication URL."
            link_div = ''
        return link_div

    def parse_authors(self, soup):
        try:
            authors_text = soup.find('div', text='Authors').next_sibling.text
            authors = authors_text.split(',')
        except AttributeError:
            print "Couldn't parse publication authors."
            authors = []
        return authors

    def parse_publication_date(self, soup):
        try:
            date = soup.find('div', text='Publication date').next_sibling.text
        except AttributeError:
            print "Couldn't parse publication date."
            date = ''
        return date

    def parse_journal_name(self, soup):
        try:
            journal_name = soup.find('div', text='Journal').next_sibling.text
        except AttributeError:
            print "Couldn't parse publication journal name."
            journal_name = ''
        return journal_name

    def parse_page_range(self, soup):
        try:
            page_range = soup.find('div', text='Pages').next_sibling.text
        except AttributeError:
            print "Couldn't parse publication page range."
            page_range = ''
        return page_range

    def parse_publisher(self, soup):
        try:
            publisher = soup.find('div', text='Publisher').next_sibling.text
        except AttributeError:
            print "Couldn't parse publication publisher."
            publisher = ''
        return publisher

    def parse_abstract(self, soup):
        try:
            abstract = soup.find('div', text='Description').next_sibling.text
        except AttributeError:
            print "Couldn't parse publication abstract."
            abstract = ''
        return abstract

    def parse_citation_count(self, soup):
        try:
            count_string = soup.find('div', text='Total citations').next_sibling.div.a.text
            count = int(count_string.split()[-1])
        except AttributeError, TypeError:
            print "Couldn't parse publication citation count."
            count = ''
        return count

    def parse_citations_by_year(self, soup):
        citations_count = []
        try:
            graph = soup.find(id='gsc_graph_bars')
            years = graph.find_all('span')
            counts = graph.find_all('a')
        except AttributeError:
            print "Couldn't parse publication citations by year."
            return citations_count
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
        print json.dumps(GSHelper.search_author(author_name), indent=4)

    if sys.argv[1] == '--author':
        # /author/search
        # cli args = author, author_uid
        # python gs.py author 'https://scholar.google.ca/citations?user=Q0ZsJ_UAAAAJ&hl=en'
        print json.dumps(GSHelper.get_author(sys.argv[2]), indent=4)

    if sys.argv[1] == '--coauthors':
        # /author/coauthors
        # cli args = coauthors, author_uid
        # python gs.py coauthors 'Q0ZsJ_UAAAAJ'
        author_uid = sys.argv[2]
        print json.dumps(GSHelper.get_coauthors(author_uid), indent=4)

    if sys.argv[1] == '--publications':
        # /author/publications
        # cli args = publications, author_uid, page
        # python gs.py publications 'Q0ZsJ_UAAAAJ' '0'
        author_uid = sys.argv[2]
        try:
            page = sys.argv[3]
        except IndexError:
            page = 0
        print json.dumps(GSHelper.get_publications(author_uid, page), indent=4)

    if sys.argv[1] == '--publication':
        # /author/publication
        # cli args = publication, author_uid, pub_uid
        # python gs.py publication 'Q0ZsJ_UAAAAJ' 'u-x6o8ySG0sC'
        author_uid = sys.argv[2]
        publication_uid = sys.argv[3]
        print json.dumps(GSHelper.get_publication(author_uid, publication_uid), indent=4)

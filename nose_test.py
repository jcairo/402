# coding: UTF-8
import gs
from bs4 import BeautifulSoup
from collections import OrderedDict
from nose.tools import set_trace

class TestAuthorQuery:
    """
    Testing for AuthorQuery and AuthorQueryResponseParser
    """
    @classmethod
    def setup_class(cls):
        cls.test_url = "https://scholar.google.ca/citations?mauthors=Victor+Guana&hl=en&view_op=search_authors"

    def test_author_query_no_description(self):
        test_url = "https://scholar.google.ca/citations?mauthors=Victor+Guana&hl=en&view_op=search_authors"
        query = gs.AuthorQuery('Victor Guana')
        assert query.query_URL == test_url

    def test_author_query_with_description(self):
        test_url = "https://scholar.google.ca/citations?mauthors=Victor+Guana+ualberta&hl=en&view_op=search_authors"
        query = gs.AuthorQuery('Victor Guana', author_description='ualberta')
        assert query.query_URL == test_url

    def test_author_query_with_description_and_labels(self):
        test_url = 'https://scholar.google.ca/citations?mauthors=Victor+Guana+ualberta+label%3AModel_Driven_Development+label%3ACode_Generation&hl=en&view_op=search_authors'
        query = gs.AuthorQuery('Victor Guana', author_description='ualberta', labels=['Model Driven Development', 'Code Generation'])
        assert query.query_URL == test_url

    def test_result_size(self):
        # retrieve locally stored copy of search for 'A Einstein label:Physics'
        html_file = open('test_data/einstein_search.html', 'r')
        author_query_results = gs.AuthorQueryResponseParser(html_file).get_results()
        assert len(author_query_results) == 3

        assert author_query_results[0]['name'] == 'Albert Einstein'
        assert author_query_results[0]['scholar_page'] == 'https://scholar.google.ca/citations?user=qc6CJjYAAAAJ&hl=en'
        assert author_query_results[0]['affiliation'] == 'Institute of Advanced Studies, Princeton'
        assert author_query_results[0]['research_areas'] == ['Physics']
        assert author_query_results[0]['email_domain'] == ''

        assert author_query_results[1]['name'] == 'James Storey'
        assert author_query_results[1]['scholar_page'] == 'https://scholar.google.ca/citations?user=b3I0YM8AAAAJ&hl=en'
        assert author_query_results[1]['affiliation'] == 'Junior Independent Researcher at the Albert Einstein Center for Fundamental Physics at the'
        assert author_query_results[1]['research_areas'] == ['Physics']
        assert author_query_results[1]['email_domain'] == '@lhep.unibe.ch'

        assert author_query_results[2]['name'] == 'Deniz B Temel'
        assert author_query_results[2]['scholar_page'] == 'https://scholar.google.ca/citations?user=H5JpaNUAAAAJ&hl=en'
        assert author_query_results[2]['affiliation'] == 'Postdoctoral Fellow in Albert Einstein College of Medicine'
        assert author_query_results[2]['research_areas'] == ['Biophysics', 'physics', 'biochemistry', 'structural biology', 'Nuclear magnetic resonance']
        assert author_query_results[2]['email_domain'] == '@einstein.yu.edu'


class TestAuthorParser:
    """
    Testing for AuthorParser.
    """
    @classmethod
    def setup_class(cls):
        cls.html_file = open('test_data/sutton_home_page.html', 'r')
        cls.author_dict = OrderedDict()
        cls.author_parser = gs.AuthorParser(cls.html_file, cls.author_dict)
        cls.author_result = cls.author_parser.get_result()

    @classmethod
    def teardown_class(cls):
        cls.html_file.close()

    def test_parse_author_name(self):
        assert self.author_result['author_name'] == 'Richard S. Sutton'

    def test_parse_author_UID(self):
        assert self.author_result['author_UID'] == 'hNTyptAAAAAJ'

    def test_parse_author_bio(self):
        bio = 'Professor of Computing Science, University of Alberta'
        assert self.author_result['bio'] == bio

    def test_parse_author_research_interests(self):
        print self.author_result['research_interests']
        assert self.author_result['research_interests'] == [
                            'artificial intelligence',
                            'reinforcement learning',
                            'machine learning',
                            'psychology',
                            'computer science']

    def test_parse_author_total_citations(self):
        assert self.author_result['total_citations'] == '41754'

    def test_parse_author_h_index(self):
        assert self.author_result['h_index'] == '55'

    def test_parse_author_i10_index(self):
        assert self.author_result['i10_index'] == '108'

    def test_parse_author_pubs_by_year(self):
        print self.author_result['publications_by_year']
        assert self.author_result['publications_by_year'] == [
                            {'2007': 2712},
                            {'2008': 2687},
                            {'2009': 2828},
                            {'2010': 2902},
                            {'2011': 2983},
                            {'2012': 3148},
                            {'2013': 3113},
                            {'2014': 3149},
                            {'2015': 250}]

    def test_author_image_URL(self):
        url = 'https://scholar.google.ca/citations?'\
                            'view_op=view_photo&user=hNTyptAAAAAJ&citpid=3'
        print self.author_result['author_image_URL']
        assert self.author_result['author_image_URL'] == url


class TestAuthorPublicationsParser:
    """
    Testing for Author Publications Parser
    """
    @classmethod
    def setup_class(cls):
        cls.html_file = open('test_data/sutton_home_page.html', 'r')
        cls.pubs_dict = OrderedDict()
        cls.publications_parser = gs.AuthorPublicationsParser(cls.html_file, cls.pubs_dict)
        cls.pubs_result = cls.publications_parser.get_result()

    @classmethod
    def teardown_class(cls):
        cls.html_file.close()

    def test_result_size(self):
        assert len(self.pubs_result['publications']) == 100

    def test_parse_first_article(self):
        assert self.pubs_result['publications'][0]['id'] == 'u5HHmVD_uO8C'
        assert self.pubs_result['publications'][0]['title'] == 'Reinforcement learning: An introduction'
        assert self.pubs_result['publications'][0]['cited'] == 19552
        assert self.pubs_result['publications'][0]['year'] == 1998
        assert self.pubs_result['publications'][0]['url'] == 'https://scholar.google.ca/citations?view_op=view_citation&hl=en&user=hNTyptAAAAAJ&pagesize=100&citation_for_view=hNTyptAAAAAJ:u5HHmVD_uO8C'

    def test_parse_100th_article(self):
        assert self.pubs_result['publications'][99]['id'] == 'bnK-pcrLprsC'
        assert self.pubs_result['publications'][99]['title'] == 'Tuning-free step-size adaptation'
        assert self.pubs_result['publications'][99]['cited'] == 13
        assert self.pubs_result['publications'][99]['year'] == 2012
        assert self.pubs_result['publications'][99]['url'] == 'https://scholar.google.ca/citations?view_op=view_citation&hl=en&user=hNTyptAAAAAJ&pagesize=100&citation_for_view=hNTyptAAAAAJ:bnK-pcrLprsC'


class TestAuthorCoAuthorsParser:
    """
    Testing for TestAuthorCoAuthorsParser.
    """
    @classmethod
    def setup_class(cls):
        cls.html_file = open('test_data/sutton_coauthors_page.html', 'r')
        cls.coauthors_dict = OrderedDict()
        cls.coauthors_parser = gs.AuthorCoAuthorsParser(cls.html_file, cls.coauthors_dict)
        cls.coauthors_result = cls.coauthors_parser.get_result() 

    @classmethod
    def teardown_class(cls):
        cls.html_file.close()

    def test_result_size(self):
        assert len(self.coauthors_result['coauthors']) == 32

    def test_parse_first_coauthor_name(self):
        assert self.coauthors_result['coauthors'][0]['name'] == 'Doina Precup'

    def test_parse_first_coauthor_uid(self):
        assert self.coauthors_result['coauthors'][0]['author_uid'] == 'j54VcVEAAAAJ' 

    def test_parse_first_coauthor_url(self):
        assert self.coauthors_result['coauthors'][0]['author_url'] == 'https://scholar.google.ca/citations?user=j54VcVEAAAAJ&hl=en' 

    def test_parse_first_coauthor_citation_count(self):
        assert self.coauthors_result['coauthors'][0]['citation_count'] == 3960

    def test_parse_first_coauthor_domain(self):
        assert self.coauthors_result['coauthors'][0]['domain'] == '@cs.mcgill.ca' 

    def test_parse_first_coauthor_bio(self):
        assert self.coauthors_result['coauthors'][0]['bio'] == 'McGill University'

    def test_parse_first_coauthor_image_url(self):
        assert self.coauthors_result['coauthors'][0]['author_image_url'] == 'https://scholar.google.ca/citations/images/avatar_scholar_150.jpg'

    def test_parse_second_coauthor_name(self):
        assert self.coauthors_result['coauthors'][1]['name'] == 'Satinder Singh'

    def test_parse_second_coauthor_uid(self):
        assert self.coauthors_result['coauthors'][1]['author_uid'] == 'q92q8SMAAAAJ' 

    def test_parse_second_coauthor_url(self): 
        assert self.coauthors_result['coauthors'][1]['author_url'] == 'https://scholar.google.ca/citations?user=q92q8SMAAAAJ&hl=en' 

    def test_parse_second_coauthor_citation_count(self): 
        assert self.coauthors_result['coauthors'][1]['citation_count'] == 17853

    def test_parse_second_coauthor_domain(self):
        assert self.coauthors_result['coauthors'][1]['domain'] == '@umich.edu' 

    def test_parse_second_coauthor_bio(self):
        assert self.coauthors_result['coauthors'][1]['bio'] == 'Professor, Computer Science & Engineering, University of Michigan'

    def test_parse_second_coauthor_image_url(self):    
        assert self.coauthors_result['coauthors'][1]['author_image_url'] == 'https://scholar.google.ca/citations?view_op=view_photo&user=q92q8SMAAAAJ&citpid=1'



class TestAuthorPublicationParser:
    """
    Testing for Author Publication Parser
    """
    @classmethod
    def setup_class(cls):
        cls.html_file = open('test_data/sutton_home_page.html', 'r')
        cls.pubs_dict = OrderedDict()
        cls.publications_parser = gs.AuthorPublicationsParser(cls.html_file, cls.pubs_dict)
        cls.pubs_result = cls.publications_parser.get_result()

    @classmethod
    def teardown_class(cls):
        cls.html_file.close()




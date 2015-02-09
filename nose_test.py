# coding: UTF-8
import gs
from bs4 import BeautifulSoup


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


class TestAuthor:
    """
    Testing for Author and AuthorParser
    """
    @classmethod
    def setup_class(cls):
        cls.html_file = open('test_data/sutton_home_page.html', 'r')
        cls.author_result = gs.AuthorParser(cls.html_file).get_result()

    @classmethod
    def teardown_class(cls):
        cls.html_file.close()

    def test_parse_author_name(self):
        assert self.author_result['author_name'] == 'Richard S. Sutton'

    def test_parse_author_UID(self):
        assert self.author_result['author_UID'] == 'hNTyptAAAAAJ'

    def test_parse_article_UIDs(self):
        assert self.author_result['article_UIDs'] == ''

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

    def test_parse_co_authors(self):
        assert self.author_result['co_authors'] == [
                            'Doina Precup',
                            'Satinder Singh',
                            'Chuck Anderson',
                            'Shalabh Bhatnagar',
                            'Csaba Szepesvari',
                            'Patrick M. Pilarski',
                            'Peter Stone',
                            'Hamid Reza Maei',
                            'David Silver',
                            'Thomas Degris',
                            'Elliot Ludvig',
                            'Adam White',
                            'Joseph Modayil',
                            'Amy McGovern',
                            'David McAllester',
                            'Mohammad Ghavamzadeh',
                            'Chris Watkins',
                            'Michael L. Littman',
                            'Martin Müller',
                            'Alborz Geramifard']

    def test_parse_author_h_index(self):
        assert self.author_result['h_index'] == '55'

    def test_parse_author_i10_index(self):
        assert self.author_result['i10_index'] == '108'

    def test_parse_author_pubs_by_year(self):
        assert self.author_result['publications_by_year'] == [
                            {2007: 2712},
                            {2008: 2687},
                            {2009: 2828},
                            {2010: 2902},
                            {2011: 2983},
                            {2012: 3148},
                            {2013: 3113},
                            {2014: 3149},
                            {2015: 250}]

    def test_author_image_URL(self):
        assert self.author_result['author_image_URL'] == \
                            'https://scholar.google.ca/citations?\
                            view_op=view_photo&user=hNTyptAAAAAJ&citpid=3'





















import gs
from bs4 import BeautifulSoup


class TestAuthorQuery:
    """
    Testing for AuthorQuery and AuthorQueryResponseParser
    """
    @classmethod
    def setup_class(klass):
        pass

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
        author_query_results = gs.AuthorQueryResponseParser(html_file).results
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
    def setup_class(klass):
        pass

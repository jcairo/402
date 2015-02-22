# coding: UTF-8
import gs
from bs4 import BeautifulSoup
from collections import OrderedDict
from nose.tools import set_trace


class TestAuthorQuery:
    """
    Testing for AuthorQuery.
    """
    @classmethod
    def setup_class(cls):
        cls.test_url = "https://scholar.google.ca/citations?mauthors=Victor+Guana&hl=en&view_op=search_authors"

    def test_author_query_no_description(self):
        test_url = "https://scholar.google.ca/citations?mauthors=Victor+Guana&hl=en&view_op=search_authors"
        query = gs.AuthorQuery('Victor Guana', gs.AuthorQueryParser)
        assert query.query_url == test_url

    def test_author_query_with_description(self):
        test_url = "https://scholar.google.ca/citations?mauthors=Victor+Guana+ualberta&hl=en&view_op=search_authors"
        query = gs.AuthorQuery('Victor Guana', gs.AuthorQueryParser, author_description='ualberta')
        assert query.query_url == test_url

    def test_author_query_with_description_and_labels(self):
        test_url = 'https://scholar.google.ca/citations?mauthors=Victor+Guana+ualberta+label%3AModel_Driven_Development+label%3ACode_Generation&hl=en&view_op=search_authors'
        query = gs.AuthorQuery('Victor Guana', gs.AuthorQueryParser, author_description='ualberta', labels=['Model Driven Development', 'Code Generation'])
        assert query.query_url == test_url

    def test_author_query_with_no_descriptions_and_labels(self):
        test_url = 'https://scholar.google.ca/citations?mauthors=Guana+label%3Acode_generation+label%3Amodel_driven_development&hl=en&view_op=search_authors'
        query = gs.AuthorQuery('Guana', gs.AuthorQueryParser, labels=['code generation', 'model driven development'])
        assert query.query_url == test_url


class TestAuthorQueryParser:
    """
    Testing for AuthorQueryParser.
    """
    @classmethod
    def setup_class(cls):
        cls.html_file = open('test_data/einstein_search.html', 'r')
        cls.query_dict = OrderedDict()
        cls.author_query_parser = gs.AuthorQueryParser(cls.html_file, cls.query_dict)
        cls.author_query_results = cls.author_query_parser.get_results()

    @classmethod
    def teardown_class(cls):
        cls.html_file.close()

    def test_result_size(self):
        assert len(self.author_query_results) == 3

    def test_first_result_name(self):
        assert self.author_query_results[0]['name'] == 'Albert Einstein'

    def test_first_result_page_url(self):
        assert self.author_query_results[0]['scholar_page'] == 'https://scholar.google.ca/citations?user=qc6CJjYAAAAJ&hl=en'

    def test_first_result_affiliation(self):
        assert self.author_query_results[0]['affiliation'] == 'Institute of Advanced Studies, Princeton'

    def test_first_result_research_areas(self):
        assert self.author_query_results[0]['research_areas'] == ['Physics']

    def test_first_result_email_domain(self):
        assert self.author_query_results[0]['email_domain'] == ''

    def test_second_result_name(self):
        assert self.author_query_results[1]['name'] == 'James Storey'

    def test_second_result_page_url(self):
        assert self.author_query_results[1]['scholar_page'] == 'https://scholar.google.ca/citations?user=b3I0YM8AAAAJ&hl=en'

    def test_second_result_affiliation(self):
        assert self.author_query_results[1]['affiliation'] == 'Junior Independent Researcher at the Albert Einstein Center for Fundamental Physics at the'

    def test_second_result_research_areas(self):
        assert self.author_query_results[1]['research_areas'] == ['Physics']

    def test_second_result_email_domain(self):
        assert self.author_query_results[1]['email_domain'] == '@lhep.unibe.ch'

    def test_third_result_name(self):
        assert self.author_query_results[2]['name'] == 'Deniz B Temel'

    def test_third_result_page_url(self):
        assert self.author_query_results[2]['scholar_page'] == 'https://scholar.google.ca/citations?user=H5JpaNUAAAAJ&hl=en'

    def test_third_result_affiliations(self):
        assert self.author_query_results[2]['affiliation'] == 'Postdoctoral Fellow in Albert Einstein College of Medicine'

    def test_third_result_research_areas(self):
        assert self.author_query_results[2]['research_areas'] == ['Biophysics', 'physics', 'biochemistry', 'structural biology', 'Nuclear magnetic resonance']

    def test_third_result_email_domain(self):
        assert self.author_query_results[2]['email_domain'] == '@einstein.yu.edu'


class TestAuthor:
    """
    Tests for Author class.
    Ensure object construction is done correctly,
    and results are as expected.
    """
    @classmethod
    def setup_class(cls):
        cls.html_file = open('test_data/testfile.html', 'r')
        cls.author = gs.Author('V Guana')

    @classmethod
    def tear_down(cls):
        cls.html_file.close()


class TestAuthorParser:
    """
    Testing for AuthorParser.
    """
    @classmethod
    def setup_class(cls):
        cls.html_file = open('test_data/sutton_home_page.html', 'r')
        cls.author_dict = OrderedDict()
        cls.author_parser = gs.AuthorParser(cls.html_file, cls.author_dict)
        cls.author_result = cls.author_parser.get_results()

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
                            {'year': 2007, 'count': 2712},
                            {'year': 2008, 'count': 2687},
                            {'year': 2009, 'count': 2828},
                            {'year': 2010, 'count': 2902},
                            {'year': 2011, 'count': 2983},
                            {'year': 2012, 'count': 3148},
                            {'year': 2013, 'count': 3113},
                            {'year': 2014, 'count': 3149},
                            {'year': 2015, 'count': 250}]

    def test_author_image_URL(self):
        url = 'https://scholar.google.ca/citations?'\
                            'view_op=view_photo&user=hNTyptAAAAAJ&citpid=3'
        print self.author_result['author_image_URL']
        assert self.author_result['author_image_URL'] == url


class TestAuthorPublications:
    pass


class TestAuthorPublicationsParser:
    """
    Testing for Author Publications Parser
    """
    @classmethod
    def setup_class(cls):
        cls.html_file = open('test_data/sutton_home_page.html', 'r')
        cls.pubs_dict = OrderedDict()
        cls.publications_parser = gs.AuthorPublicationsParser(cls.html_file, cls.pubs_dict)
        cls.pubs_result = cls.publications_parser.get_results()

    @classmethod
    def teardown_class(cls):
        cls.html_file.close()

    def test_result_size(self):
        assert len(self.pubs_result['publications']) == 100

    def test_parse_first_article_id(self):
        assert self.pubs_result['publications'][0]['id'] == 'u5HHmVD_uO8C'

    def test_parse_first_article_title(self):
        assert self.pubs_result['publications'][0]['title'] == 'Reinforcement learning: An introduction'

    def test_parse_first_article_citation_count(self):
        assert self.pubs_result['publications'][0]['cited'] == 19552

    def test_parse_first_arcticle_year(self):
        assert self.pubs_result['publications'][0]['year'] == 1998

    def test_parse_first_article_url(self):
        assert self.pubs_result['publications'][0]['url'] == 'https://scholar.google.ca/citations?view_op=view_citation&hl=en&user=hNTyptAAAAAJ&pagesize=100&citation_for_view=hNTyptAAAAAJ:u5HHmVD_uO8C'

    def test_parse_100th_article_id(self):
        assert self.pubs_result['publications'][99]['id'] == 'bnK-pcrLprsC'

    def test_parse_100th_article_title(self):
        assert self.pubs_result['publications'][99]['title'] == 'Tuning-free step-size adaptation'

    def test_parse_100th_article_citation_count(self):
        assert self.pubs_result['publications'][99]['cited'] == 13

    def test_parse_100th_article_year(self):
        assert self.pubs_result['publications'][99]['year'] == 2012

    def test_parse_100th_article_url(self):
        assert self.pubs_result['publications'][99]['url'] == 'https://scholar.google.ca/citations?view_op=view_citation&hl=en&user=hNTyptAAAAAJ&pagesize=100&citation_for_view=hNTyptAAAAAJ:bnK-pcrLprsC'


class TestCoAuthors:
    pass


class TestAuthorCoAuthorsParser:
    """
    Testing for TestAuthorCoAuthorsParser.
    """
    @classmethod
    def setup_class(cls):
        cls.html_file = open('test_data/sutton_coauthors_page.html', 'r')
        cls.coauthors_dict = OrderedDict()
        cls.coauthors_parser = gs.AuthorCoAuthorsParser(cls.html_file, cls.coauthors_dict)
        cls.coauthors_result = cls.coauthors_parser.get_results()

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


class TestAuthorPublication:
    pass


class TestAuthorPublicationParser:
    """
    Testing for Author Publication Parser
    """
    @classmethod
    def setup_class(cls):
        cls.html_file = open('test_data/sutton_publication.html', 'r')
        cls.pub_dict = OrderedDict()
        cls.publication_parser = gs.AuthorPublicationParser(cls.html_file, cls.pub_dict)
        cls.pub_result = cls.publication_parser.get_results()

    @classmethod
    def teardown_class(cls):
        cls.html_file.close()

    def test_publication_url(self):
        self.pub_result['publication_url'] == 'https://scholar.google.ca/citations?view_op=view_citation&hl=en&user=hNTyptAAAAAJ&pagesize=100&citation_for_view=hNTyptAAAAAJ:u5HHmVD_uO8C'

    def test_publication_authors(self):
        self.pub_result['authors'] == ['Richard S Sutton', 'Andrew G Barto']

    def test_publication_date(self):
        self.pub_result['publication_date'] == '1998/3/1'

    def test_publication_journal_name(self):
        self.pub_result['journal_name'] == ''

    def test_publication_page_range(self):
        self.pub_result['page_range'] == ''

    def test_publication_publisher(self):
        self.pub_result['publisher'] == 'MIT press'

    def test_publication_partial_abstract(self):
        self.pub_result['partial_abstract'] == """
                            This is one of the first books in the new adaptive computation and machine learning series.
                            The goal of this book is to provide a simple account of the key ideas of reinforcement
                            learning: a learning system that adapts its behavior in order to maximize a special signal
                            from its environment. The treatment of the subject takes the point of view of artificial
                            intelligence and engineering but without the rigorous formal mathematical treatment which
                            can distract from the simplicity of the underlying ideas. The book may be used as ...
                            """

    def test_publication_citation_count(self):
        self.pub_result['citation_count'] == 19597

    def test_citation_count_by_year(self):
        self.pub_result['citations_by_year'] == [
                            {'year': 1998, 'count': 74},
                            {'year': 1999, 'count': 205},
                            {'year': 2000, 'count': 309},
                            {'year': 2001, 'count': 442},
                            {'year': 2002, 'count': 536},
                            {'year': 2003, 'count': 721},
                            {'year': 2004, 'count': 877},
                            {'year': 2005, 'count': 1111},
                            {'year': 2006, 'count': 1221},
                            {'year': 2007, 'count': 1431},
                            {'year': 2008, 'count': 1525},
                            {'year': 2009, 'count': 1653},
                            {'year': 2010, 'count': 1674},
                            {'year': 2011, 'count': 1790},
                            {'year': 2012, 'count': 1784},
                            {'year': 2013, 'count': 1885},
                            {'year': 2014, 'count': 1906},
                            {'year': 2015, 'count': 167}
                            ]



import gs
from bs4 import BeautifulSoup


class AuthorQueryTest:

    def test_author_query():
        test_url = gs.BASE_URL + gs.CITATIONS_URL_EXTENSION + 'mauthors=Victor+Guana+ualberta&hl=en&view_op=search_authors'
        query = gs.AuthorQuery('Victor Guana', 'ualberta')
        assert query.get_url() == test_url

    def test_author_query_response():
        sample_response = open('author_response.txt', 'r')
        sample_response.close()
        response = gs.AuthorQueryResponse(sample_response.read())

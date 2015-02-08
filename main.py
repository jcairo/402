author_query = AuthorQuery('Victor Guana', labels=['Code Generation'])
author_query.search() # execute the search
author = Author(author_query.get_first_result_url()) # pass an author URL
author_data = author.get_info() # returns a dictionary of author metadata.
response_body = json.dumps(author_data) # searialize the data and return as response body.

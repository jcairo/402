from collections import OrdererdDict
# Search GS with the given parameters.
author_query = AuthorQuery('Victor Guana', labels=['Code Generation'])
author_url = author_query.get_first_result_url()

# /author/search
# Pass the author URL to the Author class with an empty dict.
author_dict = OrdererdDict()
author = Author(author_url, author_dict) # pass an author URL
author_data = author.get_info() # returns a dictionary of author metadata.
response_body = json.dumps(author_data) # searialize the data and return as response body.

# /author/publications
pubs_dict = OrdererdDict()
pubs = AuthorPublications(author_uid, page, pubs_dict)
pubs_data = pubs.get_info()
reponse_body = json.dumps(pubs_data)

# /author/publications
pub_dict = OrdererdDict()
pub = AuhotPublication(author_uid, publication_id, pub_dict)
pub_data = pub.get_info()
response_body = json.dumps(pub_data)
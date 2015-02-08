import requests
import sys

def get_html_payload(url, file_name):
    """
    This function takes a url, and dumps the received html payload into a
    file for testing.
    Make sure to pass the url as a string on the command line or you'll get errors
    """
    header = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'}
    response = requests.get(url, headers=header)
    f = open(file_name, 'w+')
    f.write(response.text.encode('utf-8'))
    f.close()

if __name__ == '__main__':
    get_html_payload(sys.argv[1], sys.argv[2])

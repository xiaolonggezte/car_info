import requests
from bs4 import BeautifulSoup


def get_soup(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        return None, 'status_code={}'.format(resp.status_code)

    # print('[Debug] resp = ', resp)

    soup = BeautifulSoup(resp.text, "html.parser")
    return soup, None
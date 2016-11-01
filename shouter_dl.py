# coding=utf-8
import requests
import json
import os
from bs4 import BeautifulSoup
import sys

# private key, do not show to anybody
TOKEN = 'Your token'

"""First of all, you need to sign up online
and store the TOKEN it gives to you.
Module to install before running the scipt
- pip install requests
- pip install beautifulsoup4

Exemple: (run it in the terminal)
$ python shouter_dl.py 非常嫌疑犯

This scriptis only for searching the subtitle of film,
the one to search the TV serie will come up soon
"""


def search_subs(film_name, pos=0, cnt=15):
    """Seach the subtitles by the film name.

    :params film_name: name of film
    :type film_name: string
    :params pos: start postion of the page
    :type pos: int
    :params cnt: quantity of subtitle in oen page

    :retrun: all the subtitles of this film
    :rtyepe: list

    .TODO: change pos !
    """
    url_base = 'http://api.makedie.me/v1/sub/search?'
    url_with_token = url_base + 'token=' + TOKEN
    parametre = {'q': film_name,
                 'pos': pos,
                 'cnt': cnt}
    try:
        r = requests.get(url_with_token, params=parametre)
    except Exception as e:
        print (e)  # TODO
    response = json.loads(r.text)
    subs = response['sub']['subs']
    if not subs:
        print ('could not find this subtitle')
        sys.exit(0)
    return subs


def find_the_best_sub(subs):
    """
    Find the best sub according to the vote note.

    :params subs: list of subtitles for the film we search
    :type subs: list

    :return: the most voted subtitle ID
    :rtype: int
    """
    best_sub_id = max(subs, key=lambda s: s['vote_score'])['id']
    return best_sub_id


def download(url, film_name):
    """
    Download the zip/rar file and store it in the local directory.

    :params url: url of zip/rar file
    :type url: string
    :params film_name: name of film
    :type film_name: string
    """
    url = 'http://sub.makedie.me' + url
    current_dir = os.path.dirname(os.path.realpath(__file__))
    headers = trick()
    file_content = requests.get(url, headers=headers)
    _, extension = os.path.splitext(url)
    if 'rar' in extension:
        with open(current_dir + '/%s.rar' % film_name, "w") as local_file:
            for block in file_content.iter_content(1024):
                local_file.write(block)
    elif 'srt' in extension:
        with open(current_dir + '/%s.srt' % film_name, "w") as local_file:
            local_file.write(file_content.text.encode('utf-8'))
    else:
        print('rare extension: %s' % url)
        sys.exit(0)


def get_url(sub_id):
    """
    Get the zip/rar URL.

    :params sub_id: subtitle ID
    :type sub_id: int

    :return: url of zip file
    :rtype: string
    """
    sub_id = str(sub_id)
    id_parent = sub_id[:3]
    # The url of shooter is composed by this way
    url = 'http://sub.makedie.me/xml/sub/%s/%s.xml' % (id_parent, sub_id)
    headers = trick()
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    a = soup.find('a', id="btn_download")
    url = a.get('href')
    return url


def trick():
    """To avoid 403 Forbidden."""
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent}
    return headers

# the script starts here
film = ''.join(sys.argv[1:])
subs = search_subs(film)
best_sub_id = find_the_best_sub(subs)
url = get_url(best_sub_id)
download(url, film)

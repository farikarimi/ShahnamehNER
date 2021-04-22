import csv
import re
import lxml
import ssl
import urllib.request
import urllib.error
from bs4 import BeautifulSoup

# Ignore SSL certificate errors
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def get_shahnameh_lists():
    page_resp = urllib.request.urlopen('https://fa.wikipedia.org/wiki/%D8%B1%D8%AF%D9%87:%D9%81%D9%87%D8%B1%D8%B3%'
                                       'D8%AA%E2%80%8C%D9%87%D8%A7%DB%8C_%D8%B4%D8%A7%D9%87%D9%86%D8%A7%D9%85%D9%87',
                                       context=CTX)
    page_soup = BeautifulSoup(page_resp, 'lxml')
    # save title and link of all Shahnameh list pages in a dict
    lists_dict = {}
    for li in page_soup.find('div', {'class': 'mw-category-group'}).ul.find_all('li'):
        lists_dict[li.a['title']] = li.a['href']
    return lists_dict


def get_list_content(page_link):
    if 'https' not in page_link:
        page_link = 'https://fa.wikipedia.org/' + page_link
    resp = urllib.request.urlopen(page_link, context=CTX)
    page_soup = BeautifulSoup(resp, 'lxml')
    relevant_content = page_soup.find('div', {'class': 'mw-parser-output'})
    entity_names = []
    for ul in relevant_content.find_all('ul', recursive=False):
        for li_tag in ul.find_all('li'):
            if li_tag.contents[0].name == 'a':
                entity_names.append(li_tag.find('a').string)
            else:
                entity_names.append(li_tag.contents[0])
    return entity_names


def clean_names(lst):
    print()
    clean_list = []
    for name in lst:
        print('original name:', name)
        if re.search(r'[a-z]+', name) is not None \
                or any(string in name for string in ['فهرست', '؟', 'ادبیات', 'اساطیر']):
            print('removed non-name\n')
            continue
        if '/' in name:
            print('split into:', name.split('/'))
            clean_names(name.split('/'))
            continue
        # TODO: make all re.sub() replacements in one statement:
        #  https://stackoverflow.com/questions/33642522/python-regex-sub-with-multiple-patterns
        if '(' in name:
            name = re.sub(r'\(.+\)', '', name)
            print('removed further description in parentheses:', name)
        if 'استان' in name:
            name = re.sub(r'^استان ', '', name)
            print('removed "province of":', name)
        if 'بانوی ' in name:
            name = re.sub(r'^بانوی ', '', name)
            print('removed "lady":', name)
        if any(word in name for word in [' پسر', ' دختر']):
            name = re.sub(r'\s{1}(پسر|دختر).+', '', name)
            print('removed "son/daughter of":', name)
        clean_list.append(name.strip())
        print()
    return clean_list


def write_names_to_csv(names_set, file_name):
    path = 'data/' + file_name + '.csv'
    with open(path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        for name in names_set:
            writer.writerow([name])


def create_places_gold_list():
    places_list = get_list_content('/wiki/%D9%81%D9%87%D8%B1%D8%B3%D8%AA_%D8%AC%D8%A7%DB%8C%E2%80%8C%D9'
                                   '%87%D8%A7_%D8%AF%D8%B1_%D8%B4%D8%A7%D9%87%D9%86%D8%A7%D9%85%D9%87')
    write_names_to_csv(set(clean_names(places_list)), 'places_gold_list')


def create_characters_gold_list():
    character_names = []
    for page_title, link in get_shahnameh_lists().items():
        if 'جا' not in page_title:
            character_names.extend(get_list_content(link))
    write_names_to_csv(set(clean_names(character_names)), 'characters_gold_list')


if __name__ == '__main__':
    create_places_gold_list()
    create_characters_gold_list()


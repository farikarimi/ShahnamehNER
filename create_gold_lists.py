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
            # TODO: the second name is not being added to clean_list *cry emoji*
            name = name.split('/')[0]
        # TODO: make all re.sub() replacements in one statement:
        #  https://stackoverflow.com/questions/33642522/python-regex-sub-with-multiple-patterns
        if '(' in name:
            name = re.sub(r'\s?\(.+\)', '', name)
            print('removed further description in parentheses:', name)
        if 'استان' in name:
            name = re.sub(r'^استان ', '', name)
            print('removed "province of":', name)
        if 'بانوی ' in name:
            name = re.sub(r'^بانوی ', '', name)
            print('removed "lady":', name)
        if any(word in name for word in ['پسر', 'دختر', ' پور', 'پدر', 'شاه', 'دوره', 'همسر']):
            name = re.sub(r'\s\u200c?(پسر|دختر|پور|پدر|شاه|دوره|همسر)(.+)?', '', name)
            print('removed "son/daughter/father/king/of the period/partner of":', name)
        if name in ['زو', 'شیر', 'چین', 'پیروز', 'پولاد', 'آرزو', 'گرامی', 'فرود', 'مرغ', 'آزاده', 'شام', 'شاهنامه',
                    'استاد', 'اشک', 'بهمن', 'پارس', 'مشک', 'نار', 'نوش', 'نوشه', 'هشیار', 'ناهید', 'شیرین', 'شادان',
                    'سهی', 'زیبد', 'پرمایه', 'فرخ‌پی', 'بید', 'گلنار', 'طراز']:  # رخش
            print('removed ambiguous name\n')
            continue
        if '\u200c' in name:
            name2 = name.replace('\u200c', ' ')
            print('added variant with space instead of ZWNJ:', name2)
            clean_list.append(name2.strip())
        clean_list.append(name.strip())
        print()
    return clean_list


def write_names_to_csv(names_set, file_name):
    # TODO: use pandas for CSV stuff?
    path = 'data/' + file_name + '.csv'
    with open(path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        for name in names_set:
            writer.writerow([name])


def save_gold_list_from_wiki(wiki_url, file_name):
    gold_list = get_list_content(wiki_url)
    write_names_to_csv(set(clean_names(gold_list)), file_name)
    return gold_list


if __name__ == '__main__':
    print('running create_gold_lists.py...')
    places_gold_list = save_gold_list_from_wiki(wiki_url='/wiki/%D9%81%D9%87%D8%B1%D8%B3%D8%AA_%D8%AC'
                                                         '%D8%A7%DB%8C%E2%80%8C%D9%87%D8%A7_%D8%AF%D8%B'
                                                         '1_%D8%B4%D8%A7%D9%87%D9%86%D8%A7%D9%85%D9%87',
                                                file_name='places_gold_list')

    characters_gold_list = save_gold_list_from_wiki(wiki_url='/wiki/%D9%81%D9%87%D8%B1%D8%B3%D8%AA_%D8%B4%D8'
                                                             '%AE%D8%B5%DB%8C%D8%AA%E2%80%8C%D9%87%D8%A7%DB%8'
                                                             'C_%D8%B4%D8%A7%D9%87%D9%86%D8%A7%D9%85%D9%87',
                                                    file_name='characters_gold_list')


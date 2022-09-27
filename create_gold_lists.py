import re
import ssl
import csv
import time
import lxml
import urllib.error
import urllib.request
from bs4 import BeautifulSoup
from timeit import default_timer as timer

# Ignore SSL certificate errors
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def get_wiki_list_content(page_link: str) -> list[str]:
    """Extract the entity names from the Wikipedia page at the given URL and return them in a list."""
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


def process_names(lst: list[str]) -> list[str]:
    """Process the entity names in the given list and return a list containing the clean names."""
    clean_list = []
    for name in lst:
        print('original name:', name)
        if re.search(r'[a-z]+', name) is not None \
                or any(string in name for string in ['فهرست', '؟', 'ادبیات', 'اساطیر']):
            print('excluding non-name\n')
            continue
        if '/' in name:
            print('splitting and including name(s):', name.split('/'), '\n')
            clean_list.extend(name.split('/'))
        else:
            print('including name\n')
            clean_list.append(name)

    processed_list = []
    for name in clean_list:
        print('original name:', name)
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
            print('removed "son/daughter/father/king/partner of/of the period":', name)
        if name in ['زو', 'شیر', 'چین', 'پیروز', 'پولاد', 'آرزو', 'گرامی', 'فرود', 'مرغ', 'آزاده', 'شام', 'شاهنامه',
                    'استاد', 'اشک', 'بهمن', 'پارس', 'مشک', 'نار', 'نوش', 'نوشه', 'هشیار', 'ناهید', 'شیرین', 'شادان',
                    'سهی', 'زیبد', 'پرمایه', 'فرخ‌پی', 'بید', 'گلنار', 'طراز', 'رخش', 'سرو', 'شهریار', 'مای']:
            print('excluding ambiguous name\n')
            continue
        if '\u200c' in name:
            name2 = name.replace('\u200c', ' ')
            print('added variant with space instead of ZWNJ (\\u200c):', name2)
            processed_list.append(name2.strip())
        processed_list.append(name.strip())
        print()
    return processed_list


def write_names_to_csv(names_set: set[str], path: str) -> None:
    """Save the given set of names in a CSV file at the specified path."""
    with open(path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        for name in names_set:
            writer.writerow([name])


def save_gold_list_from_wiki(wiki_url: str, file_path: str) -> list[str]:
    """Extract the entity names from the Wikipedia list at the given URL, save the names in a CSV file at the specified
    path and return the names in a list."""
    gold_list = get_wiki_list_content(wiki_url)
    write_names_to_csv(set(process_names(gold_list)), file_path)
    return gold_list


if __name__ == '__main__':
    print(f'\n{time.strftime("%d/%m/%Y %H:%M:%S")}: Running create_gold_lists.py...\n')
    start = timer()
    locations_gold_list = save_gold_list_from_wiki(wiki_url='/wiki/%D9%81%D9%87%D8%B1%D8%B3%D8%AA_%D8%AC'
                                                            '%D8%A7%DB%8C%E2%80%8C%D9%87%D8%A7_%D8%AF%D8%B'
                                                            '1_%D8%B4%D8%A7%D9%87%D9%86%D8%A7%D9%85%D9%87',
                                                   file_path=f'data/gold_lists/locations_gold_list_'
                                                             f'{time.strftime("%d%m%Y_%H%M")}.csv')

    persons_gold_list = save_gold_list_from_wiki(wiki_url='/wiki/%D9%81%D9%87%D8%B1%D8%B3%D8%AA_%D8%B4%D8'
                                                          '%AE%D8%B5%DB%8C%D8%AA%E2%80%8C%D9%87%D8%A7%DB%8'
                                                          'C_%D8%B4%D8%A7%D9%87%D9%86%D8%A7%D9%85%D9%87',
                                                 file_path=f'data/gold_lists/persons_gold_list_'
                                                           f'{time.strftime("%d%m%Y_%H%M")}.csv')
    end = timer()
    print(f'{time.strftime("%d/%m/%Y %H:%M:%S")}: Done!\n\nElapsed time: {round((end - start) / 60, 2)} minutes.\n')


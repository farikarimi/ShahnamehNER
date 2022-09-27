import csv
import re
import time
from collections import Counter
from math import ceil
from statistics import mean
from timeit import default_timer as timer
from util_funcs import pickle_obj, unpickle_obj, get_most_recent_file


def get_gold_names(path: str) -> list[str]:
    """Read the CSV file at the specified path and return a list containing the name from each cell as an element."""
    with open(path, newline='') as csv_file:
        return [name for row in csv.reader(csv_file) for name in row]


def get_shahnameh_text() -> str:
    """Read the file containing the Shahnameh text and return the content as a string."""
    # Shahnameh text from www.ganjoor.org
    with open('data/shahnameh_raw.txt', 'r') as shahnameh_file:
        return shahnameh_file.read()


def get_verses() -> list[str]:
    """Return a list containing all verses from the Shahnameh text – excluding titles and tables of contents –
    pickle the list object, and save the verses to a text file."""
    print(f'\n{time.strftime("%H:%M:%S")}: Extracting verses...')
    # remove titles
    text_wo_titles = re.sub(r'\n\n\n.+\n\n\n', '', get_shahnameh_text())
    # exclude other non-verse lines
    verses = [line for line in text_wo_titles.split('\n\n')
              if not re.search(r'بخش \d+', line) and ":" not in line and line]
    print(f'{time.strftime("%H:%M:%S")}: Extracted {len(verses)} verses.\n')
    pickle_obj(verses, f'pickles/all_verses_{time.strftime("%d%m%Y_%H%M")}.pickle')
    with open(f'data/all_verses_{time.strftime("%d%m%Y_%H%M")}.txt', 'w') as verses_txt_file:
        verses_txt_file.write('\n'.join(verses))
    return verses


def get_couplets() -> list[str]:
    """
    Assemble the couplets from the verses, return them in a list, pickle the list object,
    and save the couplets to a text file."""
    print(f'\n{time.strftime("%H:%M:%S")}: Assembling couplets from verses...')
    verses = unpickle_obj(get_most_recent_file(dir_path='pickles', prefix='all_verses'))
    couplets = [' '.join([verse, verses[verses.index(verse)+1]]) for verse in verses if (verses.index(verse) % 2) == 0]
    print(f'{time.strftime("%H:%M:%S")}: Assembled {len(couplets)} couplets.\n')
    pickle_obj(couplets, f'pickles/all_couplets_{time.strftime("%d%m%Y_%H%M")}.pickle')
    with open(f'data/all_couplets_{time.strftime("%d%m%Y_%H%M")}.txt', 'w') as couplets_txt_file:
        couplets_txt_file.write('\n'.join(couplets))
    return couplets


def get_gold_couplets() -> list[str]:
    """
    Return a list of all couplets that contain a name from one of the gold standard lists
    and pickle the list object."""
    print(f'\n{time.strftime("%H:%M:%S")}: Extracting gold couplets...')
    location_names = get_gold_names(get_most_recent_file(dir_path='data/gold_lists', prefix='locations_gold_list'))
    person_names = get_gold_names(get_most_recent_file(dir_path='data/gold_lists', prefix='persons_gold_list'))
    all_couplets = unpickle_obj(get_most_recent_file(dir_path='pickles', prefix='all_couplets'))
    gold_couplets = [*{couplet for couplet in all_couplets
                       if any(f' {name} ' in couplet for name in location_names + person_names)}]
    print(f'{time.strftime("%H:%M:%S")}: Extracted {len(gold_couplets)} gold couplets.\n')
    pickle_obj(gold_couplets, f'pickles/gold_couplets_{time.strftime("%d%m%Y_%H%M")}.pickle')
    with open(f'data/gold_couplets_{time.strftime("%d%m%Y_%H%M")}.txt', 'w') as gold_couplets_file:
        gold_couplets_file.write('\n'.join(gold_couplets))
    return gold_couplets


def replace_spaces_in_names() -> tuple[list[str], list[str], list[str]]:
    """
    Replace the spaces in all names with § in preparation for BIO annotation, return a tuple containing the three
    lists with the modified gold standard location names, person names and couplets, and pickle the list objects."""
    print(f'\n{time.strftime("%H:%M:%S")}: Replacing spaces in gold standard names with §...')
    gold_couplets = unpickle_obj(get_most_recent_file(dir_path='pickles', prefix='gold_couplets'))
    location_names = get_gold_names(get_most_recent_file(dir_path='data/gold_lists', prefix='locations_gold_list'))
    person_names = get_gold_names(get_most_recent_file(dir_path='data/gold_lists', prefix='persons_gold_list'))
    modified_locations = {name: (name.replace(' ', '§') if ' ' in name.strip() else name) for name in location_names}
    modified_persons = {name: (name.replace(' ', '§') if ' ' in name.strip() else name) for name in person_names}
    n = 0
    modified_gold_couplets = []
    for gold_couplet in gold_couplets:
        for original_name, modified_name in {**modified_locations, **modified_persons}.items():
            if '§' in modified_name and f' {original_name} ' in gold_couplet:
                n += 1
                gold_couplet = gold_couplet.replace(f' {original_name} ', f' {modified_name} ')
        modified_gold_couplets.append(gold_couplet)
    print(f'{time.strftime("%H:%M:%S")}: Found and modified {n} occurrences of names with spaces.\n')
    pickle_obj(modified_gold_couplets,
               f'pickles/modified_gold_couplets_{time.strftime("%d%m%Y_%H%M")}.pickle')
    pickle_obj([*modified_locations.values()],
               f'pickles/modified_location_names_{time.strftime("%d%m%Y_%H%M")}.pickle')
    pickle_obj([*modified_persons.values()],
               f'pickles/modified_person_names_{time.strftime("%d%m%Y_%H%M")}.pickle')
    return [*modified_locations.values()], [*modified_persons.values()], modified_gold_couplets


# TODO: Documentation
def get_names_for_testing(name_tokens: list[str]) -> tuple[list[str], list[str], list[str]]:
    tokens_counts = Counter(name_tokens)
    tokens_counts_sorted = tokens_counts.most_common()
    token_average_freq = ceil(mean([t[1] for t in tokens_counts_sorted]))
    twenty_from_middle = []
    for i, t in enumerate(tokens_counts_sorted):
        if t[1] in [token_average_freq, token_average_freq+1, token_average_freq-1]:
            twenty_from_middle.extend(tokens_counts.most_common()[i-10:i+10])
            break
    five_from_middle = [t[0] for t in twenty_from_middle][3::4]
    five_from_top = [t[0] for t in tokens_counts.most_common(20)][3::4]
    five_from_bottom = [t[0] for t in tokens_counts_sorted[-20:]][3::4]
    return five_from_top, five_from_middle, five_from_bottom


# TODO: Documentation
def save_excluded_names_to_csv(names_tuple: tuple[list[str], list[str], list[str]], path: str) -> None:
    """Save each list from the given tuple as a row in a CSV file at the specified path."""
    with open(path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        for names in names_tuple:
            writer.writerow(names)


# TODO: Documentation
def save_names_to_exclude() -> list[str]:
    print(f'\n{time.strftime("%H:%M:%S")}: Getting names to exclude...')
    modified_gold_couplets = unpickle_obj(get_most_recent_file(dir_path='pickles', prefix='modified_gold_couplets'))
    modified_location_names = unpickle_obj(get_most_recent_file(dir_path='pickles', prefix='modified_location_names'))
    modified_person_names = unpickle_obj(get_most_recent_file(dir_path='pickles', prefix='modified_person_names'))
    per_tokens = []
    loc_tokens = []
    for gold_couplet in modified_gold_couplets:
        for word in gold_couplet.split(' '):
            if word in modified_location_names:
                loc_tokens.append(word)
            elif word in modified_person_names:
                per_tokens.append(word)
    per_names_for_testing = get_names_for_testing(per_tokens)
    loc_names_for_testing = get_names_for_testing(loc_tokens)
    save_excluded_names_to_csv(per_names_for_testing,
                               f'data/testing/excluded_per_names_{time.strftime("%d%m%Y_%H%M")}.csv')
    save_excluded_names_to_csv(loc_names_for_testing,
                               f'data/testing/excluded_loc_names_{time.strftime("%d%m%Y_%H%M")}.csv')
    names_for_testing = [name for t in per_names_for_testing + loc_names_for_testing for name in t]
    print(f'{time.strftime("%H:%M:%S")}: Saving {len(names_for_testing)} names to exclude from training data:\n'
          f'person names: {per_names_for_testing}\n'
          f'location names: {loc_names_for_testing}\n')
    pickle_obj(names_for_testing, f'pickles/names_for_testing_{time.strftime("%d%m%Y_%H%M")}.pickle')
    return names_for_testing


def tag_gold_couplets() -> list[list[tuple[str, str]]]:
    """
    Tag the couplets containing names from the gold standard lists according to the BIO notation, return a list
    containing the tagged couplets, each couplet being a list of tuples containing a token and its label,
    and pickle the list object."""
    print(f'\n{time.strftime("%H:%M:%S")}: Tagging couplets...')
    modified_gold_couplets = unpickle_obj(get_most_recent_file(dir_path='pickles', prefix='modified_gold_couplets'))
    modified_location_names = unpickle_obj(get_most_recent_file(dir_path='pickles', prefix='modified_location_names'))
    modified_person_names = unpickle_obj(get_most_recent_file(dir_path='pickles', prefix='modified_person_names'))
    names_for_testing = unpickle_obj(get_most_recent_file(dir_path='pickles', prefix='names_for_testing'))
    location_names_shortened = [name for name in modified_location_names if name not in names_for_testing]
    person_names_shortened = [name for name in modified_person_names if name not in names_for_testing]
    tagged_couplets = []
    for gold_couplet in modified_gold_couplets:
        tagged_couplet = []
        for word in gold_couplet.split(' '):
            if word in location_names_shortened:
                if '§' in word:
                    split_word = word.split('§')
                    tagged_couplet.append((split_word[0], 'B-LOC'))
                    for part in split_word[1:]:
                        tagged_couplet.append((part, 'I-LOC'))
                else:
                    tagged_couplet.append((word, 'B-LOC'))
            elif word in person_names_shortened:
                if '§' in word:
                    split_word = word.split('§')
                    tagged_couplet.append((split_word[0], 'B-PER'))
                    for part in split_word[1:]:
                        tagged_couplet.append((part, 'I-PER'))
                else:
                    tagged_couplet.append((word, 'B-PER'))
            else:
                tagged_couplet.append((word, 'O'))
        tagged_couplets.append(tagged_couplet)
    print(f'{time.strftime("%H:%M:%S")}: Tagged {len(tagged_couplets)} couplets.\n')
    pickle_obj(tagged_couplets, f'pickles/tagged_couplets_final_{time.strftime("%d%m%Y_%H%M")}.pickle')
    return tagged_couplets


def save_tagged_data() -> None:
    """Write the tagged data to a text file according to the BIO notation."""
    tagged_couplets = unpickle_obj(get_most_recent_file(dir_path='pickles', prefix='tagged_couplets_final'))
    file_path = f'data/tagged/tagged_data_final_{time.strftime("%d%m%Y_%H%M")}.txt'
    with open(file_path, 'w') as tagged_data_file:
        for couplet in tagged_couplets:
            for word in couplet:
                tagged_data_file.write(f'{word[0]}\t{word[1]}\n')
            tagged_data_file.write('\n')
    print(f'{time.strftime("%H:%M:%S")}: Saved tagged data as "{file_path}".\n')


if __name__ == '__main__':
    print('\nRunning annotate_text.py...\n')
    start = timer()
    # if you've already ran a function and thus pickled its results, comment out the respective line
    get_verses()
    get_couplets()
    get_gold_couplets()
    replace_spaces_in_names()
    # TODO: check how many entity tokens / occurrences were excluded because of this
    save_names_to_exclude()
    tag_gold_couplets()
    save_tagged_data()
    end = timer()
    print(f'\n{time.strftime("%d/%m/%Y %H:%M:%S")}: Done!\n\nElapsed time: {round((end - start) / 60, 2)} minutes.\n')

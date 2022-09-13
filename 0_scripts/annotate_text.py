import csv
import re
import pickle
from collections import Counter

# TODO: delete unnecessary comments
# TODO: clean / improve whole code / standardize docstrings
# BIO notation:
# http://nlpprogress.com/english/named_entity_recognition.html
# The training data files contain two columns separated by a tab. Each word has been put on a separate line and
# there is an empty line after each sentence. The first item on each line is a word, and the second named entity tag.
# The named entity tags have the format I-TYPE which means that the word is inside a phrase of type TYPE.
# The first word of each named entity have tag B-TYPE to show that it starts a new named entity.
# A word with tag O is not part of a named entity.
# http://nsurl.org/2019-2/tasks/task-7-named-entity-recognition-ner-for-farsi/

no = 1


# TODO: move pickle/unpickle functions to a util_funcs script
def pickle_obj(obj, path):
    """Pickles the given object and saves the pickle file at the given path."""
    with open(path, 'wb') as f:
        pickle.dump(obj, f)


def unpickle_obj(path):
    """Unpickles the object at the given path and returns it."""
    with open(path, 'rb') as pf:
        return pickle.load(pf)


# TODO: maybe do this with pandas?
def csv_as_list(path):
    """Reads the CSV file at the given path and returns a list containing each element from each row."""
    lst = []
    with open(path, newline='') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            for name in row:
                lst.append(name)
    return lst


def get_shahnameh_text():
    """Reads the file containing the Shahnameh text and returns the content as a string."""
    # TODO: Use Ganjoor API?
    # Shahnameh text from www.ganjoor.org
    with open('1_data/frdvsi.txt', 'r') as shahnameh_file:
        return shahnameh_file.read()


def extract_verses():
    """Returns a list containing all the verses from Shahnameh – without titles and tables of contents –
    and saves the cleaned text to a file."""
    # delete titles
    shahnameh_text_no_titles = re.sub(r'\n\n\n.+\n\n\n', '', get_shahnameh_text())
    # remove other non-verse lines
    verses = []
    for line in shahnameh_text_no_titles.split('\n\n'):
        if not re.search(r'بخش \d+', line) and ":" not in line and line:
            verses.append(line)
    with open('1_data/shahnameh_cleaned_text.txt', 'w') as clean_txt_file:
        for v in verses:
            clean_txt_file.write(v)
            clean_txt_file.write('\n')
    print(int(len(verses) / 2), 'couplets')
    return verses


def extract_rhymeless_couplets():
    """Saves couplets whose two verses don't have the same last letter
    (thus possibly don't match the rhyme scheme) to a file (for review)."""
    rhymeless_couplets = []
    verses = extract_verses()
    for i in range(0, len(verses)-2):
        if (i % 2) == 0:
            if not verses[i][-1] == verses[i+1][-1]:
                rhymeless_couplets.append(verses[i] + '\n' + verses[i+1] + '\n')
    with open('../1_data/rhymeless_couplets.txt', 'w') as rhymeless_couplets_file:
        for rhymeless_couplet in rhymeless_couplets:
            rhymeless_couplets_file.write(rhymeless_couplet)
            rhymeless_couplets_file.write('\n')


def get_couplets():
    """Assembles the couplets from the verses, returns them in a list, and pickles the list object."""
    verses = extract_verses()
    couplets = [' '.join([verse, verses[verses.index(verse)+1]]) for verse in verses if (verses.index(verse) % 2) == 0]
    pickle_obj(couplets, '../3_pickles/couplets.pickle')
    return couplets


def get_gold_couplets():
    """Returns a list of all the couplets that contain a name from one of the gold lists and pickles the list object."""
    global no
    gold_couplets = []
    place_names = csv_as_list('../1_data/places_gold_list.csv')
    characters_names = csv_as_list('../1_data/characters_gold_list.csv')
    print(place_names + characters_names)

    # for couplet in unpickle_obj('pickles/couplets.pickle'):
    #     if any(entity_name in couplet for entity_name in place_names + characters_names):
    #         print(couplet)
    #         gold_couplets.append(couplet)

    for couplet in unpickle_obj('../3_pickles/couplets.pickle'):
        for name in place_names + characters_names:
            name = ' ' + name + ' '
            if name in couplet:
                gold_couplets.append(couplet)
                print(f'{no}) detected name: {name}\nin couplet: {couplet}\n')
                no += 1
                break
    print(len(gold_couplets), 'gold couplets\n')
    print(Counter(gold_couplets))
    with open('../1_data/gold_couplets.txt', 'w') as gold_couplets_file:
        gold_couplets_file.write('\n'.join(gold_couplets))
    pickle_obj(gold_couplets, '../3_pickles/gold_couplets.pickle')
    return gold_couplets


# TODO: shorten + clean up + add documenting comment
# => 370 new names found
def replace_spaces_in_names():
    g_couplets = unpickle_obj('../3_pickles/gold_couplets.pickle')
    p_names = csv_as_list('../1_data/places_gold_list.csv')
    c_names = csv_as_list('../1_data/characters_gold_list.csv')
    space_names = {}
    modified_g_couplets = []
    modified_p_names = []
    modified_c_names = []
    for p_name in p_names:
        if ' ' in p_name.strip():
            replace_p_name = p_name.replace(' ', '§')
            space_names[p_name] = replace_p_name
            modified_p_names.append(replace_p_name)
        else:
            modified_p_names.append(p_name)
    for c_name in c_names:
        if ' ' in c_name.strip():
            replace_c_name = c_name.replace(' ', '§')
            space_names[c_name] = replace_c_name
            modified_c_names.append(replace_c_name)
        else:
            modified_c_names.append(c_name)
    for g_couplet in g_couplets:
        for s_name, no_s_name in space_names.items():
            if s_name in g_couplet:
                g_couplet = g_couplet.replace(s_name, no_s_name)
        modified_g_couplets.append(g_couplet)
    pickle_obj(modified_g_couplets, '../3_pickles/modified_g_couplets.pickle')
    pickle_obj(modified_p_names, '../3_pickles/modified_p_names.pickle')
    pickle_obj(modified_c_names, '../3_pickles/modified_c_names.pickle')
    return modified_g_couplets, modified_p_names, modified_c_names


# TODO: shorten + clean up + add documenting comments
def annotate_gold_couplets():
    gold_couplets = unpickle_obj('../3_pickles/modified_g_couplets.pickle')
    loc_names = unpickle_obj('../3_pickles/modified_p_names.pickle')
    per_names = unpickle_obj('../3_pickles/modified_c_names.pickle')
    n = 0
    tagged_couplets_list = []
    for g_couplet in gold_couplets:
        g_couplet = g_couplet.split(' ')
        tagged_couplet_dict = {}
        for word in g_couplet:
            if word in loc_names:
                if '§' in word:
                    split_word = word.split('§')
                    tagged_couplet_dict[n] = (split_word[0], 'B-LOC')
                    n += 1
                    for part in split_word[1:]:
                        tagged_couplet_dict[n] = (part, 'I-LOC')
                        n += 1
                else:
                    tagged_couplet_dict[n] = (word, 'B-LOC')
            elif word in per_names:
                if '§' in word:
                    split_word2 = word.split('§')
                    tagged_couplet_dict[n] = (split_word2[0], 'B-PER')
                    n += 1
                    for part2 in split_word2[1:]:
                        tagged_couplet_dict[n] = (part2, 'I-PER')
                        n += 1
                else:
                    tagged_couplet_dict[n] = (word, 'B-PER')
            else:
                tagged_couplet_dict[n] = (word, 'O')
            n += 1
        tagged_couplets_list.append(tagged_couplet_dict)
    pickle_obj(tagged_couplets_list, '../3_pickles/tagged_couplets_list_final.pickle')
    return tagged_couplets_list


def save_annotations(tagged_couplets_lst):
    with open('../2_annotation_results/auto_annot_training_data_final.txt', 'w') as annot_file:
        for coup in tagged_couplets_lst:
            for w in coup.values():
                line = ''.join([w[0], '\t', w[1], '\n'])
                print(line)
                annot_file.write(line)
            annot_file.write('\n')


# TODO: implementation of Nils' suggestion: exclude certain entity names from the training data
#  to check after the training whether the model was able to correctly detect and classify them
if __name__ == '__main__':
    print('running annotate_text.py...')
    # replace_spaces_in_names() # results are saved as pickle, only call if changed
    save_annotations(unpickle_obj('../3_pickles/tagged_couplets_list_final.pickle'))

import csv
import re

# sentence = line
# read text as list of verses
# extract all verses/couplets that contain a name from the gold standard lists
# tokenize text
# bring extracted text into IOB2 input format:
# The training data files contain two columns separated by a tab. Each word has been put on a separate line and
# there is an empty line after each sentence. The first item on each line is a word, and the second named entity tag.
# The named entity tags have the format I-TYPE which means that the word is inside a phrase of type TYPE.
# The first word of each named entity have tag B-TYPE to show that it starts a new named entity.
# A word with tag O is not part of a named entity.
# http://nsurl.org/2019-2/tasks/task-7-named-entity-recognition-ner-for-farsi/

with open('data/places_gold_list.csv', newline='') as csv_file:
    reader = csv.reader(csv_file, delimiter=',')
    place_names = list(reader)

# Shahnameh text from www.ganjoor.org
with open('data/frdvsi.txt', 'r') as shahnameh_file:
    shahnameh_text = shahnameh_file.read()

# delete titles
shahnameh_text_no_titles = re.sub(r'\n\n\n.+\n\n\n', '', shahnameh_text)

# save in file to check results
with open('data/test_text.txt', 'w') as test_file:
    test_file.write(shahnameh_text_no_titles)

# remove other non-verse lines
verses = []
for line in shahnameh_text_no_titles.split('\n\n'):
    if not re.search(r'بخش \d+', line) and ":" not in line and line:
        verses.append(line)

print(int(len(verses) / 2), 'couplets')

# save cleaned text
# with open('data/shahnameh_cleaned_text.txt', 'w') as txt_file:
#     for v in verses:
#         txt_file.write(v)
#         txt_file.write('\n')

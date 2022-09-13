import re
from sklearn.model_selection import train_test_split
from datasets import Dataset
from datasets import DatasetDict
from transformers import AutoTokenizer

# TODO: cleanup and document


def read_annot_data(path):
    with open(path, 'r', encoding='utf8') as annot_data_file:
        raw_text = annot_data_file.read().strip()
    raw_sents = re.split(r'\n{2}', raw_text)
    token_sents = []
    tag_sents = []
    for sent in raw_sents:
        tokens = []
        tags = []
        for line in sent.split('\n'):
            token, tag = line.split('\t')
            tokens.append(token)
            tags.append(tag)
        token_sents.append(tokens)
        tag_sents.append(tags)
    return token_sents, tag_sents


def create_dataset_dict(data_path):
    sents_list_tokens, sents_list_tags = read_annot_data(data_path)
    train_tokens, val_tokens, train_tags, val_tags = train_test_split(sents_list_tokens, sents_list_tags, test_size=.2)
    # create a set of unique tags
    unique_tags = set(tag for sent in sents_list_tags for tag in sent)
    # assign each tag a number (id): "tag: id" dictionary
    tag_to_id = {tag: t_id for t_id, tag in enumerate(unique_tags)}
    # reverse dictionary to create "id: tag" dictionary
    id_to_tag = {t_id: tag for tag, t_id in tag_to_id.items()}
    train_tag_ids = [[tag_to_id[t] for t in tag_list] for tag_list in train_tags]
    train_data_dict = {'tokens': train_tokens, 'ner_tags': train_tag_ids}
    train_dataset = Dataset.from_dict(train_data_dict)
    val_tag_ids = [[tag_to_id[t] for t in tag_list] for tag_list in val_tags]
    val_data_dict = {'tokens': val_tokens, 'ner_tags': val_tag_ids}
    val_dataset = Dataset.from_dict(val_data_dict)
    return DatasetDict({
        'train': train_dataset,
        'validation': val_dataset
    })


def align_tags_with_tokens(tag_ids, word_ids):
    new_tag_ids = []
    current_word_id = None
    for word_id in word_ids:
        if word_id != current_word_id:
            # Start of a new word!
            current_word_id = word_id
            tag_id = -100 if word_id is None else tag_ids[word_id]
            new_tag_ids.append(tag_id)
        elif word_id is None:
            # Special token
            new_tag_ids.append(-100)
        else:
            # Same word as previous token
            tag_id = tag_ids[word_id]
            # If the label is B-XXX we change it to I-XXX
            if tag_id == 1 or tag_id == 2:
                tag_id += 2
            new_tag_ids.append(tag_id)

    return new_tag_ids


def tokenize_and_align_tags(examples):
    tokenizer = AutoTokenizer.from_pretrained('HooshvareLab/bert-fa-zwnj-base')
    tokenized_inputs = tokenizer(
        examples['tokens'], truncation=True, is_split_into_words=True
    )
    all_tags = examples['ner_tags']
    new_tags = []
    for i, tags in enumerate(all_tags):
        word_ids = tokenized_inputs.word_ids(i)
        new_tags.append(align_tags_with_tokens(tags, word_ids))

    tokenized_inputs['tags'] = new_tags
    return tokenized_inputs


if __name__ == '__main__':
    print('Running fine-tune_model.py...')
    dataset_dict = create_dataset_dict('2_annotation_results/auto_annot_training_data_final.txt')
    tokenized_datasets = dataset_dict.map(
        tokenize_and_align_tags,
        batched=True,
        remove_columns=dataset_dict['train'].column_names,
    )
    print(tokenized_datasets)

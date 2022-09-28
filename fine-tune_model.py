import re
import time
from timeit import default_timer as timer
import evaluate
import numpy as np
from sklearn.model_selection import train_test_split
from datasets import Dataset
from datasets import DatasetDict
from transformers import \
    AutoTokenizer, \
    DataCollatorForTokenClassification, \
    AutoModelForTokenClassification, \
    TrainingArguments, \
    Trainer
from util_funcs import get_most_recent_file, pickle_obj, unpickle_obj

# TODO: add docstrings


def read_labeled_data() -> tuple[list[list], list[list]]:
    """
    Read the labeled training data and return a tuple containing two lists:
    a list containing a list of tokens for each couplet and,
    and a list containing a list of labels for each couplet.
    The lists are pickled before returning."""
    print(f'\n{time.strftime("%H:%M:%S")}: Reading labeled data...')
    with open(get_most_recent_file(dir_path='data/tagged', prefix='tagged_data_final'), 'r', encoding='utf8') \
            as labeled_data_file:
        labeled_data = labeled_data_file.read().strip()
    labeled_couplets = re.split(r'\n{2}', labeled_data)
    couplets_tokens = []
    couplets_labels = []
    for couplet in labeled_couplets[:100]:
        tokens = []
        labels = []
        for line in couplet.split('\n'):
            token, label = line.split('\t')
            tokens.append(token)
            labels.append(label)
        couplets_tokens.append(tokens)
        couplets_labels.append(labels)
    pickle_obj(couplets_tokens, f'pickles/couplets_tokens_{time.strftime("%d%m%Y_%H%M")}.pickle')
    pickle_obj(couplets_labels, f'pickles/couplets_labels_{time.strftime("%d%m%Y_%H%M")}.pickle')
    print(f'{time.strftime("%H:%M:%S")}: Read and saved tokens and labels from {len(labeled_couplets)} couplets.\n')
    return couplets_tokens, couplets_labels


def create_train_val_split() -> tuple[list[list], list[list], list[list], list[list]]:
    """Create a training/validation (0.8/0.2) split of the data, pickle and return the resulting lists."""
    print(f'\n{time.strftime("%H:%M:%S")}: Splitting the labeled data into training and validation datasets...')
    couplets_tokens = unpickle_obj(get_most_recent_file(dir_path='pickles', prefix='couplets_tokens'))
    couplets_labels = unpickle_obj(get_most_recent_file(dir_path='pickles', prefix='couplets_labels'))
    train_tokens, val_tokens, train_labels, val_labels = \
        train_test_split(couplets_tokens, couplets_labels, test_size=.2)
    pickle_obj(train_tokens, f'pickles/train_tokens_{time.strftime("%d%m%Y_%H%M")}.pickle')
    pickle_obj(train_labels, f'pickles/train_labels_{time.strftime("%d%m%Y_%H%M")}.pickle')
    pickle_obj(val_tokens, f'pickles/val_tokens_{time.strftime("%d%m%Y_%H%M")}.pickle')
    pickle_obj(val_labels, f'pickles/val_labels_{time.strftime("%d%m%Y_%H%M")}.pickle')
    print(f'{time.strftime("%H:%M:%S")}: Split and saved datasets.\n')
    return train_tokens, train_labels, val_tokens, val_labels


def get_unique_labels() -> list[str]:
    """Return a list containing the unique labels from the labeled data."""
    couplets_labels = unpickle_obj(get_most_recent_file(dir_path='pickles', prefix='couplets_labels'))
    return sorted(set(label for couplet in couplets_labels for label in couplet))


def get_id2label_dict():
    """Return a dictionary mapping the label IDs to label names (id: label)."""
    return {label_id: label for label_id, label in enumerate(get_unique_labels())}


def get_label2id_dict():
    """Return a dictionary mapping the label names to label IDs (label: id)."""
    return {label: label_id for label_id, label in enumerate(get_unique_labels())}


def get_id_for_label(label_str: str) -> int:
    """Return the ID (encoding) for the specified label."""
    return get_label2id_dict()[label_str]


def get_label_for_id(id_int: int) -> str:
    """Return the label for the specified label ID."""
    return get_id2label_dict()[id_int]


def create_dataset_dict() -> DatasetDict:
    """Convert the labeled data to a DatasetDict and return the resulting object after pickling it."""
    print(f'\n{time.strftime("%H:%M:%S")}: Converting data into a DatasetDict...')
    train_tokens = unpickle_obj(get_most_recent_file(dir_path='pickles', prefix='train_tokens'))
    train_labels = unpickle_obj(get_most_recent_file(dir_path='pickles', prefix='train_labels'))
    val_tokens = unpickle_obj(get_most_recent_file(dir_path='pickles', prefix='val_tokens'))
    val_labels = unpickle_obj(get_most_recent_file(dir_path='pickles', prefix='val_labels'))
    train_label_ids = [[get_id_for_label(label) for label in label_list] for label_list in train_labels]
    val_label_ids = [[get_id_for_label(label) for label in label_list] for label_list in val_labels]
    train_dataset = Dataset.from_dict({'tokens': train_tokens, 'ner_tags': train_label_ids})
    val_dataset = Dataset.from_dict({'tokens': val_tokens, 'ner_tags': val_label_ids})
    datasetdict = DatasetDict({'train': train_dataset, 'validation': val_dataset})
    pickle_obj(datasetdict, f'pickles/datasetdict_{time.strftime("%d%m%Y_%H%M")}.pickle')
    print(f'{time.strftime("%H:%M:%S")}: Created and saved the DatasetDict.\n')
    return datasetdict


def align_labels_with_tokens(label_ids, word_ids):
    new_label_ids = []
    current_word_id = None
    for word_id in word_ids:
        if word_id != current_word_id:
            # Start of a new word!
            current_word_id = word_id
            label_id = -100 if word_id is None else label_ids[word_id]
            new_label_ids.append(label_id)
        elif word_id is None:
            # Special token
            new_label_ids.append(-100)
        else:
            # Same word as previous token
            label_id = label_ids[word_id]
            # If the label is B-XXX we change it to I-XXX
            if label_id == 0 or label_id == 1:
                label_id += 2
            new_label_ids.append(label_id)
    return new_label_ids


def tokenize_and_align_labels(examples):
    print(f'\n{time.strftime("%H:%M:%S")}: Tokenizing and aligning data...')
    model_tokenizer = AutoTokenizer.from_pretrained('HooshvareLab/bert-fa-zwnj-base')
    tokenized_inputs = model_tokenizer(examples['tokens'], truncation=True, is_split_into_words=True)
    old_labels = examples['ner_tags']
    new_labels = []
    for i, tags in enumerate(old_labels):
        word_ids = tokenized_inputs.word_ids(i)
        new_labels.append(align_labels_with_tokens(tags, word_ids))
    tokenized_inputs['labels'] = new_labels
    pickle_obj(tokenized_inputs, f'pickles/tokenized_inputs_{time.strftime("%d%m%Y_%H%M")}.pickle')
    print(f'{time.strftime("%H:%M:%S")}: Tokenized and saved model inputs.\n')
    return tokenized_inputs


def compute_metrics(eval_preds):
    print(f'\n{time.strftime("%H:%M:%S")}: Computing metrics...\n')
    metric = evaluate.load("seqeval")
    logits, all_labels = eval_preds
    all_predictions = np.argmax(logits, axis=-1)
    # Remove ignored index (special tokens) and convert to labels
    true_labels = [[get_label_for_id(label_id) for label_id in labels if label_id != -100] for labels in all_labels]
    true_predictions = [[get_label_for_id(predicted_label_id) for (predicted_label_id, label_id) in
                         zip(predictions, labels) if label_id != -100] for predictions, labels in
                        zip(all_predictions, all_labels)]
    return metric.compute(predictions=true_predictions, references=true_labels)


if __name__ == '__main__':
    print('Running fine-tune_model.py...')
    start = timer()
    read_labeled_data()
    create_train_val_split()
    create_dataset_dict()
    dataset_dict = unpickle_obj(get_most_recent_file(dir_path='pickles', prefix='datasetdict'))
    tokenized_datasets = dataset_dict.map(
        tokenize_and_align_labels,
        batched=True,
        remove_columns=dataset_dict['train'].column_names
    )
    model_checkpoint = 'HooshvareLab/bert-fa-zwnj-base'
    tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
    data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer)
    model = AutoModelForTokenClassification.from_pretrained(
        model_checkpoint,
        id2label=get_id2label_dict(),
        label2id=get_label2id_dict()
    )
    args = TrainingArguments(
        "bert-fa-zwnj-base-shahnameh-ner",
        evaluation_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        num_train_epochs=3,
        weight_decay=0.01,
    )
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=tokenized_datasets['train'],
        eval_dataset=tokenized_datasets['validation'],
        data_collator=data_collator,
        compute_metrics=compute_metrics,
        tokenizer=tokenizer,
    )
    print('\n\n')
    trainer.train()
    pickle_obj(trainer, f'pickles/trainer_{time.strftime("%d%m%Y_%H%M")}.pickle')
    evaluation_results = trainer.evaluate()
    pickle_obj(evaluation_results, f'pickles/evaluation_results{time.strftime("%d%m%Y_%H%M")}.pickle')
    trainer.save_model('fine-tuned_model')
    end = timer()
    print(f'\n{time.strftime("%d/%m/%Y %H:%M:%S")}: Done!\n\nElapsed time: {round((end - start) / 60, 2)} minutes.\n')

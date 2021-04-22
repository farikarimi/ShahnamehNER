from transformers import AutoTokenizer
from transformers import AutoModelForTokenClassification  # for pytorch
from transformers import pipeline

pars_bert_ner = "HooshvareLab/bert-fa-zwnj-base-ner"
tokenizer = AutoTokenizer.from_pretrained(pars_bert_ner)
model = AutoModelForTokenClassification.from_pretrained(pars_bert_ner)
nlp = pipeline("ner", model=model, tokenizer=tokenizer)

# example = "در سال ۲۰۱۳ درگذشت و آندرتیکر و کین برای او مراسم یادبود گرفتند."
example = "پس آن صورت رستم گرزدار" \
          " ببردند نزدیک سام سوار" \
          " یکی جشن کردند در گلستان" \
          " ز زاولستان تا به کابلستان" \
          " همه دشت پر باده و نای بود" \
          " به هر کنج صد مجلس آرای بود" \
          " به زاولستان از کران تا کران" \
          " نشسته به هر جای رامشگران" \
          " نبد کهتر از مهتران بر فرود" \
          " نشسته چنان چون بود تار و پود" \
          " پس آن پیکر رستم شیرخوار" \
          " ببردند نزدیک سام سوار"

ner_results = nlp(example)

for subword in ner_results:
    print(subword)

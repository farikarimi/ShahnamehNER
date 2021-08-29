from transformers import AutoTokenizer
from transformers import AutoModelForTokenClassification  # for pytorch
from transformers import pipeline

pars_bert_ner = "HooshvareLab/bert-fa-zwnj-base-ner"
tokenizer = AutoTokenizer.from_pretrained(pars_bert_ner)
model = AutoModelForTokenClassification.from_pretrained(pars_bert_ner)
nlp = pipeline("ner", model=model, tokenizer=tokenizer)

# example = "در سال ۲۰۱۳ درگذشت و آندرتیکر و کین برای او مراسم یادبود گرفتند."
example = "یکی گفت کاین شاه روم است و هند ز قنوج تا پیش دریای سند" \
          "ز کشمیر تا پیش دریای چین برو شهریاران کنند آفرین" \
          "و دیگر دلاور سپهدار طوس که در جنگ بر شیر دارد فسوس" \
          "جهان بی‌سر و تاج خسرو مباد همیشه بماناد جاوید و شاد" \
          "چنین گفت کآیین تخت و کلاه کیومرث آورد و او بود شاه" \
          "سیامک بدش نام و فرخنده بود کیومرث را دل بدو زنده بود" \
          "جهان شد برآن دیوبچه سیاه ز بخت سیامک وزآن پایگاه" \
          "یکایک بیامد خجسته سروش بسان پری پلنگینه پوش" \
          "سخن چون به گوش سیامک رسید ز کردار بدخواه دیو پلید"

ner_results = nlp(example)

for subword in ner_results:
    print(subword)

# ARMAN corpus:
# Each file contains one token, along with its manually annotated named-entity tag, per line.
# Each sentence is separated with a newline. The NER tags are in IOB format.
# Location: LOC; Person: PER
# (The annotation format seems to be IOB2)

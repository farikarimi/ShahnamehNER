from transformers import AutoTokenizer
from transformers import AutoModelForTokenClassification  # for pytorch, use TFAutoModelForSequenceClassification for TF
from transformers import pipeline

# path to NER model
pars_bert_ner = "HooshvareLab/bert-fa-zwnj-base-ner"
# a tokenizer is downloaded for preprocessing the text for the prediction model
# (tokenization, encoding, padding, truncation)
# after splitting the text into tokens, the tokenizer converts them into numbers,
# to be able to build a tensor out of them and feed them to the model.
# To do this, the tokenizer has a vocab, which is downloaded when we instantiate it with from_pretrained
# since we need to use the same vocab as when the model was pretrained.
tokenizer = AutoTokenizer.from_pretrained(pars_bert_ner)
# AutoModelForTokenClassification downloads the model
model = AutoModelForTokenClassification.from_pretrained(pars_bert_ner)
model = AutoModelForTokenClassification.from_pretrained(pars_bert_ner)
# the pipeline groups everything together and post-processes the predictions to make them readable
ner_tagger = pipeline("ner", model=model, tokenizer=tokenizer)

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

# a list of dictionaries, each dictionary contains one sub-word
results = ner_tagger(example)

for subword in results:
    print(subword)

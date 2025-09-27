import re

import nltk


def shorten_text(text: str) -> str:
    text = re.sub(r'[^\w\s]', '', text)
    text = text.lower()
    stop_words = set(nltk.corpus.stopwords.words('russian'))
    word_tokens = nltk.word_tokenize(text)
    filtered_text = [word for word in word_tokens if word not in stop_words]
    lemmatizer = nltk.stem.WordNetLemmatizer()
    lemmatized_text = [lemmatizer.lemmatize(word) for word in filtered_text]
    new_text = ' '.join(lemmatized_text)
    return re.sub(' +', ' ', new_text)

def crop_text(text: str, percent_crop: float) -> str:
    text = text.split(' ')
    percent_crop = round(len(text)*percent_crop)
    return ' '.join(text[percent_crop:]) + '...'

def extract_parts_by_pipe(text: str, command: str) -> list[str] | None:
    if command not in text:
        return None
    return [part.strip().strip("[]") for part in text.replace(command, "").split("|")]

def split_text(text: str, max_length: int) -> list[str]:
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]
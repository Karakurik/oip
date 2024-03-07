import os
import ssl
import re
import collections
import nltk
import pymorphy3
from bs4 import BeautifulSoup

HTML_DIRECTORY = './html_directory'
TOKENS_FILE = './tokens.txt'
LEMMAS_FILE = './lemmas.txt'

BAD_TOKENS = {
    'NUMB',
    'NUMB,intg',
    'ROMN',
    'PNCT',
    'PREP',
    'CONJ',
    'PRCL',
    'INTJ',
    'LATN',
    'UNKN',
}

UTF_8 = 'utf-8'
RUSSIAN = 'russian'


def get_text(directory):
    texts = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        with open(file_path, 'r', encoding=UTF_8) as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            texts.append(' '.join(soup.stripped_strings))
    return ' '.join(texts)


def processing(directory, tokenizer, stop_words, morph):
    tokens = set()
    lemmas = collections.defaultdict(set)

    text = get_text(directory)
    row_tokens = tokenizer.tokenize(text)
    for token in row_tokens:
        token = token.lower()
        if len(token) < 2 or token in stop_words:
            continue

        parsed_token = morph.parse(token)
        is_number = bool(re.compile(r'^[0-9]+$').match(token))
        is_russian = bool(re.compile(r'^[а-яА-Я]{2,}$').match(token))
        if not is_russian or is_number:
            continue

        tokens.add(token)
        if parsed_token[0].score >= 0.5:
            lemmas[parsed_token[0].normal_form].add(token)

    return tokens, lemmas


def save(tokens, lemmas, tokens_filename, lemmas_filename):
    with open(tokens_filename, 'w', encoding=UTF_8) as file:
        file.write('\n'.join(tokens) + '\n')
    with open(lemmas_filename, 'w', encoding=UTF_8) as file:
        for lemma, tokens in lemmas.items():
            file.write(f'{lemma} {" ".join(tokens)}\n')


def main():
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    nltk.download('stopwords')

    stop_words = set(nltk.corpus.stopwords.words(RUSSIAN))
    tokenizer = nltk.tokenize.WordPunctTokenizer()
    morph = pymorphy3.MorphAnalyzer()

    tokens, lemmas = processing(HTML_DIRECTORY, tokenizer, stop_words, morph)
    save(tokens, lemmas, TOKENS_FILE, LEMMAS_FILE)


if __name__ == '__main__':
    main()

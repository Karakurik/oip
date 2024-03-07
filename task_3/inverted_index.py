import collections
import os
import re
import ssl

from bs4 import BeautifulSoup
import nltk
import pymorphy3

HTML_DIRECTORY = './html_directory'
TOKENS_FILE = './tokens.txt'
LEMMAS_FILE = './lemmas.txt'
INDEXES_FILE = './inverted_indexes.txt'
STOP_WORDS = set(nltk.corpus.stopwords.words('russian'))
BAD_TOKENS = {
    'NUMB',
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


def get_index(filename):
    return ''.join(char for char in filename if char.isdigit())


def get_text(directory):
    texts = collections.defaultdict(str)
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        index = int(get_index(filename))
        with open(file_path, 'r', encoding=UTF_8) as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            texts[index] = ' '.join(soup.stripped_strings)
    return texts


def process_text(text, tokenizer, morphy):
    tokens = set()
    lemmas = collections.defaultdict(set)
    indexes = collections.defaultdict(set)

    row_tokens = tokenizer.tokenize(text)
    for token in row_tokens:
        token = token.lower()
        if len(token) < 2 or token in STOP_WORDS:
            continue
        if not re.match(r'^[а-яА-Я]{2,}$', token) or re.match(r'^[0-9]+$', token):
            continue

        morph = morphy.parse(token)[0]
        if morph.tag.POS in BAD_TOKENS or morph.score < 0.5:
            continue

        tokens.add(token)
        lemmatized = morph.normal_form
        lemmas[lemmatized].add(token)

    return tokens, lemmas


def save(tokens, lemmas, indexes, tokens_filename, lemmas_filename, indexes_filename):
    with open(tokens_filename, 'w', encoding=UTF_8) as file:
        file.write('\n'.join(tokens) + '\n')
    with open(lemmas_filename, 'w', encoding=UTF_8) as file:
        for lemma, tokens in lemmas.items():
            file.write(f'{lemma} {" ".join(tokens)}\n')
    with open(indexes_filename, 'w', encoding=UTF_8) as file:
        for lemma, index_set in indexes.items():
            file.write(f'{lemma} {" ".join(map(str, sorted(index_set)))}\n')


def main():
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    nltk.download('stopwords')
    tokenizer = nltk.tokenize.WordPunctTokenizer()
    morphy = pymorphy3.MorphAnalyzer()

    texts = get_text(HTML_DIRECTORY)
    tokens = set()
    lemmas = collections.defaultdict(set)
    indexes = collections.defaultdict(set)

    for index, text in texts.items():
        t, l = process_text(text, tokenizer, morphy)
        tokens.update(t)
        for lemma, lemma_tokens in l.items():
            lemmas[lemma].update(lemma_tokens)
            indexes[lemma].add(index)

    save(tokens, lemmas, indexes, TOKENS_FILE, LEMMAS_FILE, INDEXES_FILE)


if __name__ == '__main__':
    main()

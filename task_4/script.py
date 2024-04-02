import re
import pymorphy3
from os import listdir, path
from bs4 import BeautifulSoup
from nltk.tokenize import wordpunct_tokenize
from collections import Counter
from math import log10

HTML_DIRECTORY = './html_directory'
TOKENS_FILE = './tokens.txt'
LEMMAS_FILE = './lemmas.txt'
TOKENS_TF_IDF_DIRECTORY = '/tokens_tf_idf'
LEMMAS_TF_IDF_DIRECTORY = '/lemmas_tf_idf'

morph = pymorphy3.MorphAnalyzer()


def read_tokens():
    tokens = set()
    with open(TOKENS_FILE, 'r') as file:
        lines = file.readlines()
        for line in lines:
            tokens.add(line.strip())
    return tokens


def read_lemmas():
    lemmas = set()
    with open(LEMMAS_FILE, 'r') as file:
        lines = file.readlines()
        for line in lines:
            words = re.split('\\s+', line)
            lemmas.add(words[0])
    return lemmas


def get_data(word_set):
    pages = []
    counters = []
    file_names = []
    for file_name in listdir(HTML_DIRECTORY):
        with open(HTML_DIRECTORY + '/' + file_name, 'r', encoding='utf-8') as file:
            file_names.append(re.search('\\d+', file_name)[0])
            text = BeautifulSoup(file, features='html.parser').get_text()
            list_of_words = wordpunct_tokenize(text)
            words = []
            for word in list_of_words:
                parsed_word = morph.parse(word)[0]
                word_form = parsed_word.normal_form if parsed_word.normalized.is_known else word.lower()
                if word_form in word_set:
                    words.append(word_form)
            pages.append(words)
            counters.append(Counter(words))
    return pages, counters, file_names


def get_tf(pages, counters, word_set):
    pages_tf = []
    for page, counter in zip(pages, counters):
        count = len(page)
        tf = {}
        for word in word_set:
            tf[word] = counter[word] / count
        pages_tf.append(tf)
    return pages_tf


def get_idf(pages, counters, word_set):
    counters_dict = dict.fromkeys(word_set, 0)
    for p_counter in counters:
        for word in word_set:
            if p_counter[word] != 0:
                counters_dict[word] += 1
    idf = {}
    for word in word_set:
        idf[word] = log10(len(pages) / counters_dict[word]) if counters_dict[word] != 0 else 0
    return idf


def get_tf_idf(tf, idf, word_set):
    idf_tf = []
    for tf_count in tf:
        idf_tf_dict = {}
        for word in word_set:
            idf_tf_dict[word] = tf_count[word] * idf[word]
        idf_tf.append(idf_tf_dict)
    return idf_tf


def calculate_tf_idf_for_words(word_set, directory):
    pages, counters, file_names = get_data(word_set)
    tf = get_tf(pages, counters, word_set)
    idf = get_idf(pages, counters, word_set)
    tf_idf = get_tf_idf(tf, idf, word_set)
    for page_tf_idf, file_name in zip(tf_idf, file_names):
        with open(path.dirname(__file__) + f'{directory}/{file_name}.txt', 'w', encoding='utf-8') as file:
            for word in word_set:
                file.write(f'{word} {idf[word]} {page_tf_idf[word]}\n')


if __name__ == '__main__':
    tokens = read_tokens()
    lemmas = read_lemmas()
    calculate_tf_idf_for_words(tokens, TOKENS_TF_IDF_DIRECTORY)
    calculate_tf_idf_for_words(lemmas, LEMMAS_TF_IDF_DIRECTORY)

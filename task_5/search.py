import re
import ssl
import numpy as np
from os import listdir, path
from pymorphy3 import MorphAnalyzer
import nltk
from nltk.tokenize import word_tokenize
from scipy.spatial import distance
from collections import defaultdict

INDEX_TXT_FILE = './index.txt'
LEMMAS_TF_IDF_DIRECTORY = './lemmas_tf_idf'


class Search:
    def __init__(self):
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context

        self.links = {}
        nltk.download('punkt')
        self.lemmas = []
        self.matrix = None
        self.read_links()
        self.read_lemmas()
        self.read_tf_idf()
        self.morph = MorphAnalyzer()

    def read_links(self):
        with open(INDEX_TXT_FILE, 'r', encoding='utf-8') as file:
            self.links = dict(line.split(' ') for line in file)

    def read_lemmas(self):
        file_names = listdir(LEMMAS_TF_IDF_DIRECTORY)
        with open(path.join(LEMMAS_TF_IDF_DIRECTORY, file_names[0]), 'r', encoding='utf-8') as file:
            self.lemmas = [line.split(' ')[0] for line in file]

    def read_tf_idf(self):
        file_names = listdir(LEMMAS_TF_IDF_DIRECTORY)
        self.matrix = np.zeros((len(file_names), len(self.lemmas)))
        for file_name in file_names:
            file_number = int(re.search('\\d+', file_name)[0])
            with open(path.join(LEMMAS_TF_IDF_DIRECTORY, file_name), 'r', encoding='utf-8') as file:
                self.matrix[file_number - 1] = [float(line.split(' ')[2]) for line in file]

    def vectorize(self, query: str) -> np.ndarray:
        vector = np.zeros(len(self.lemmas))
        tokens = word_tokenize(query)
        for token in tokens:
            parsed_token = self.morph.parse(token)[0]
            lemma = parsed_token.normal_form if parsed_token.normalized.is_known else token.lower()
            if lemma in self.lemmas:
                vector[self.lemmas.index(lemma)] = 1
        return vector

    def search(self, query: str) -> list:
        vector = self.vectorize(query)
        similarities = defaultdict(float)
        for i, row in enumerate(self.matrix, start=1):
            dist = 1 - distance.cosine(vector, row)
            if dist > 0:
                similarities[i] = dist
        sorted_similarities = sorted(similarities.items(), key=lambda item: item[1], reverse=True)
        return [(self.links[str(doc[0])], doc[1]) for doc in sorted_similarities if str(doc[0]) in self.links]

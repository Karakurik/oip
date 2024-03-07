import collections
import pymorphy3

INDEX_FILE = './index.txt'
INVERTED_INDEXES_FILE = './inverted_indexes.txt'
UTF_8 = 'utf-8'

AND = 'and'
OR = 'or'
NOT = 'not'


def prepare():
    all_indexes = set()
    lemma_indexes = collections.defaultdict(set)

    with open(INVERTED_INDEXES_FILE, 'r', encoding=UTF_8) as file:
        for line in file:
            key, *indexes = line.split()
            lemma_indexes[key] = set(indexes)
            all_indexes.update(indexes)

    urls = {}
    with open(INDEX_FILE, 'r', encoding=UTF_8) as file:
        for line in file:
            key, url = line.split(maxsplit=1)
            urls[key] = url.strip()

    return lemma_indexes, urls, all_indexes


def get_normalized(morphy, word):
    return morphy.parse(word)[0].normal_form


def process(datas, all_indexes):
    result = set()
    is_need_invert = False

    for data in datas:
        if data != NOT:
            if is_need_invert:
                result.difference_update(data)
            else:
                result.update(data)
            is_need_invert = False
        else:
            is_need_invert = not is_need_invert

    return result


def search(morphy, string, lemma_indexes, all_indexes):
    string = string.lower().replace('(', ' ( ').replace(')', ' ) ').split()
    stack = []
    result = []

    for word in string:
        if word == '(':
            stack.append(result)
            result = []
        elif word == ')':
            processed = process(result, all_indexes)
            result = stack.pop()
            result.append(processed)
        else:
            if word not in {AND, OR, NOT}:
                normalized = get_normalized(morphy, word)
                result.append(lemma_indexes.get(normalized, set()))
            else:
                result.append(word)

    return process(result, all_indexes)


def main():
    lemma_indexes, urls, all_indexes = prepare()
    morphy = pymorphy3.MorphAnalyzer()

    sample_queries = [
        "рио",
        "карта and тинькофф",
        "карта and тинькофф or браузер",
        "карта and (тинькофф or браузер)",
        "тинькофф",
        "браузер",
    ]
    for query in sample_queries:
        print('Sample query: ', query)
        if query.strip().lower() == 'exit':
            break
        indexes = search(morphy, query, lemma_indexes, all_indexes)
        for index in indexes:
            print(urls.get(index))

    while True:
        query = input('Your query: ')
        if query.strip().lower() == 'exit':
            break
        indexes = search(morphy, query, lemma_indexes, all_indexes)
        for index in indexes:
            print(urls.get(index))


if __name__ == '__main__':
    main()

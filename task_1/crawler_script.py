import os
import requests
from zipfile import ZipFile
from bs4 import BeautifulSoup

banki = 'https://www.banki.ru'
news = '/news/'
banki_news = banki + news
suffix = '.html'

UTF_8 = 'utf-8'
html_directory = './html_directory'
index_file = './index.txt'
zip_filename = './html.zip'

bad_tags = ['script', 'link', 'style']


def handle_response(response, tags_for_removal, directory, idx):
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in tags_for_removal:
            for item in soup.find_all(tag):
                item.extract()

        filename = f'{directory}/page_{idx}.html'
        with open(filename, 'w', encoding=UTF_8) as html_file:
            html_file.write(soup.prettify())
        return True
    return False


def main():
    websites = []
    response = requests.get(banki_news)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [banki + link.get('href') for link in soup.find_all('a', href=True) if
                 link.get('href').startswith(news)]
        websites.extend(links[:100])

    if not os.path.exists(html_directory):
        os.makedirs(html_directory)

    with open(index_file, 'w') as index:
        for idx, url in enumerate(websites, start=1):
            response = requests.get(url)
            if handle_response(response, bad_tags, html_directory, idx):
                index.write(f'{idx} {url}\n')

    with ZipFile(zip_filename, 'w') as zip_file:
        for root, _, files in os.walk(html_directory):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, os.path.relpath(file_path, html_directory))


if __name__ == '__main__':
    main()

import requests
from bs4 import BeautifulSoup
import csv


def write_to_csv(data):
    with open('news.csv', 'a') as file:
        writer = csv.writer(file, delimiter='/')
        writer.writerow((data['title'],
                         data['urls'],
                         data['img']))


def get_html(url):
    headers = {"User-Agent": "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}
    response = requests.get(url, headers=headers)
    return response.text


def get_data(url):
    html = get_html(url)
    soup = BeautifulSoup(html, 'lxml')
    news = soup.find_all('div', {'class': 'ArticleItem--data ArticleItem--data--withImage'})
    for new in news:
        title = new.find('a', {'class': 'ArticleItem--name'}).text.replace('\n', '')
        img = new.find('a', {'class': 'ArticleItem--image'}).get('href')
        urls = new.find('a', {'class': 'ArticleItem--name'}).get('href')
        data = {'title': title, 'urls': urls, 'img': img}
        write_to_csv(data)


def main():
    url = 'https://kaktus.media/?lable=8&date=2021-10-28&order=time'
    get_data(url)


main()

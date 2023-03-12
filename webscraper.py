import requests
from bs4 import BeautifulSoup
import json

# Konstanta obsahující adresu webu, ze které chceme odebírat data.
URL = "https://www.imdb.com/search/keyword/?keywords=anime%2Canime-animation&mode=detail&page=1&ref_=kw_ref_key&sort=moviemeter,asc"
page = requests.get(URL)
# Vytvoření objektu parseru stránky
soup = BeautifulSoup(page.content, 'html.parser')

rank_links = soup.select('div.lister-item-content>h3>span.lister-item-index')
anime_links = soup.select('div.lister-item-content>h3>a')
years_links = soup.select('div.lister-item-content>h3>span.lister-item-year')
runtime_links = soup.select('div.lister-item-content>p>span.runtime')
rating_links = soup.select('div.ratings-bar>div.inline-block>strong')
#Získání pořadí filmu v žebříčku
ranks = [int(tag.text[:-1]) for tag in rank_links]
#Získání názvu anime
titles = [tag.text for tag in anime_links]
#Získání období kdy anime vycházelo
years = [f'"{tag.text[1:-1]}"' for tag in years_links]
#Získání dléky jednoho dílu/filmu
runtime = [f'"{tag.text}"' for tag in runtime_links]
#Získání hodnocení
ratings = [tag.text for tag in rating_links]
#Odkazy na detailní stránky jednotlivých seriálů
urls = [f'https://www.imdb.com{tag["href"]}' for tag in anime_links]

# Kontrolní výpis získaných údajů
with open("anime.json",  "w", encoding='utf-8') as file:
    file.write('[')
    for i in range(0, 50):
        detail_page = requests.get(urls[i], headers={'User-agent': 'Mozilla/5.0'})
        dsoup = BeautifulSoup(detail_page.content, 'html.parser')
        content = dsoup.select('[data-testid=plot]>span[data-testid=plot-xs_to_m]')
        genre_links = dsoup.select('[data-testid=genres] a')
        genres = [genre.text for genre in genre_links]
        row = f'"rank": {ranks[i]}, "title": "{titles[i]}", "year": {years[i]}, "runtime": {runtime[i]}, "rating": {ratings[i]}, "url": "{urls[i]}", "genres": {json.dumps(genres)} '
        row = '{' + row + '}'
        row = row + ',\n' if i != 49 else row + "\n"
        print(row)
        file.write(row)
    file.write(']')

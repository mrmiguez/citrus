import os
import csv
import requests
from bs4 import BeautifulSoup


def iso639_gen():  # TODO test for existing CSV
    try:
        os.remove('assets/iso639.csv')
    except FileNotFoundError:
        pass

    r = requests.get("https://www.loc.gov/standards/iso639-2/php/code_list.php")
    soup = BeautifulSoup(r.text, 'lxml')
    table = soup.find("table", width='100%')
    headers = [header.text for header in table.find_all('th')]
    rows = []
    for row in table.find_all('tr'):
        rows.append([val.text for val in row.find_all('td')])

    with open('assets/iso639.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


def iso639(l):
    if os.path.isfile('assets/iso639.csv') is False:
        iso639_gen()
    with open('assets/iso639.csv', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if l == row['ISO 639-1 Code']:
                return {"name": row['English name of Language'].split(';')[0],
                        "iso_639_3": row['ISO 639-2 Code'].split(' ')[0]}

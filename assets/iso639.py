import os
import csv
import requests
from bs4 import BeautifulSoup
from os.path import abspath, dirname, join

iso_path = abspath(dirname(__file__))


def iso639_gen():
    try:
        os.remove(join(iso_path, 'iso639.csv'))
    except FileNotFoundError:
        pass

    r = requests.get("https://www.loc.gov/standards/iso639-2/php/code_list.php")
    soup = BeautifulSoup(r.text, 'lxml')
    table = soup.find("table", width='100%')
    headers = [header.text for header in table.find_all('th')]
    rows = []
    for row in table.find_all('tr'):
        rows.append([val.text for val in row.find_all('td')])

    with open(join(iso_path, 'iso639.csv'), 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


def iso639_2code(l):
    if os.path.isfile(join(iso_path, 'iso639.csv')) is False:
        iso639_gen()
    with open(join(iso_path, 'iso639.csv'), encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if l == row['ISO 639-1 Code']:
                return {"name": row['English name of Language'].split(';')[0],
                        "iso_639_3": row['ISO 639-2 Code'].split(' ')[0]}


def iso639_3code(l):
    if os.path.isfile(join(iso_path, 'iso639.csv')) is False:
        iso639_gen()
    with open(join(iso_path, 'iso639.csv'), encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if l == row['ISO 639-2 Code']:
                return {"name": row['English name of Language'].split(';')[0],
                        "iso_639_3": row['ISO 639-2 Code'].split(' ')[0]}

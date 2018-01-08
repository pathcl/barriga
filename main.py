import time
import requests
import threading
import json
import logging

from queue import Queue
from tqdm import tqdm
from bs4 import BeautifulSoup
import sqlite3 as sql
from lxml import html as htm

print_lock = threading.Lock()
flat_queue = Queue()

logging.basicConfig(filename='barriga.log',format='%(asctime)s %(levelname)s %(message)s',filemode='a', level=logging.INFO)

def process_queue():
    while True:
        flat = flat_queue.get()
        main(flat)
        flat_queue.task_done()


def totalpages():
    """
    Get total pages to scrape
    """
    counter = 0
    url = 'https://www.economicos.cl/rm/departamento?operacion=Arriendo&dormitoriosDesde=2&pagina=%d#results' % (counter)
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')

    for each_div in soup.findAll('div', {'class': 'cont_right_ecn_pag'}):
        counter += int(each_div.text.split()[3])

    return counter

def getallflats():
    """
    Iterates over every page we should
    """
    counter = totalpages()
    href = []
    
    print('Total pages to scrape: {}'.format(counter))
    print('Gathering every page...')

    for page in tqdm(range(0, counter)):
        url = 'https://www.economicos.cl/rm/departamento?operacion=Arriendo&dormitoriosDesde=2&pagina=%d#results' % (page)
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'lxml')

        for a in soup.find_all('a', href=True):
            if 'propiedades' in a['href']:
                href.append(url[:25]+a['href'])
   
    flats = set(href)

    return flats

def shorturl(url):
    post_url = 'https://www.googleapis.com/urlshortener/v1/url?key={}'.format('')
    payload = {'longUrl': url}
    headers = {'content-type': 'application/json'}
    r = requests.post(post_url, data=json.dumps(payload), headers=headers)
    return r.json()['id']

def main(flat):
    try:
        r = requests.get(flat).text
        if '/nassets/img/nodisponible.png' not in r:

            html = requests.get(flat).text
            soup = BeautifulSoup(html, 'lxml')
            tree = htm.fromstring(html)

            for each_div in soup.findAll('div', {'class': 'cont_price_detalle_f'}):
                price = each_div.text.split()[1]
                for comuna in tree.xpath('//div[@id="specs"]//li'):
                    if comuna.text_content().startswith('Comuna'):
                        commune = comuna.text_content().split(':')[1]
                        with print_lock:
                            with sql.connect('flats.db', check_same_thread=False) as conn:
                                conn.execute('INSERT INTO flats (timestamp, price, flat, commune) VALUES (?,?,?,?)', (time.strftime(
                                    '%Y-%m-%d %H:%M:%S'), price.replace('.', ''), flat, commune.replace(' ','')))

    except Exception as e:
        logging.info(e)
        raise

t1 = time.time()

allflats = getallflats()

for i in range(100):
    t = threading.Thread(target=process_queue)
    t.daemon = True
    t.start()

for flat in allflats:
    flat_queue.put(flat)

flat_queue.join()

logging.info("Execution time = {0:.5f}".format(time.time() - t1))

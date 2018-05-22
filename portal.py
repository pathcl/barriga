import time
import requests
import threading
from queue import Queue
from bs4 import BeautifulSoup
from tqdm import tqdm
from lxml import html
import sqlite3 as sql
import logging


logging.basicConfig(filename='barriga.log',format='%(asctime)s %(levelname)s %(message)s',filemode='a', level=logging.INFO)

counter = 0
t1 = time.time()

print_lock = threading.Lock()
flat_queue = Queue()


def process_queue():
    while True:
        flat = flat_queue.get()
        main(flat)
        flat_queue.task_done()

def getallflats():
    total = []
    print('Total pages to scrape: {}'.format('495'))
    print('Gathering every page...')

    for page in tqdm(range(0,1)):
        url = 'https://www.portalinmobiliario.com/arriendo/departamento/metropolitana?ca=3&ts=1&dd=2&mn=1&or=&sf=1&sp=0&at=0&pg=%d' % (page)
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'lxml')
        for a in soup.find_all('a', href=True):
            if a['href'].startswith('/arriendo/departamento/'):
                flat = 'https://www.portalinmobiliario.com'
                total.append(flat+a['href'])

    uniq = set(total)

    return uniq


def main(flat):
    try:
        r = requests.get(flat).text
        tree = html.fromstring(r)
        commune = tree.xpath('//*[@id="wrapper"]/div/div/div/div[2]/div/ol/li[5]/a/text()')
        price = tree.xpath('//*[@id="divImagenes"]/div[2]/div/p[1]/text()')
        totalrooms =  tree.xpath(
            '//*[@id="wrapper"]/section/div/div/div[1]/article/div/div[2]/div[2]/div[2]/div[2]/p/text()')
        size = tree.xpath(
            '//*[@id="wrapper"]/section/div/div/div[1]/article/div/div[2]/div[2]/div[2]/div[3]/p/text()')
        address = tree.xpath(
            '//*[@id="wrapper"]/section/div/div/div[1]/article/div/div[2]/div[2]/div[2]/div[1]/p/text()')
        if len(price) >= 1:
            q = ''.join(commune).replace(' ','')
            with print_lock:
                with sql.connect('flats.db', check_same_thread=False) as conn:
                    conn.execute('INSERT INTO flats (timestamp, price, flat, commune, rooms, bathroom, size, addr) VALUES (?,?,?,?,?,?,?,?)', (time.strftime(
                        '%Y-%m-%d %H:%M:%S'), price[0].replace(' ', '').replace('$', '').replace('.', ''), flat, q, totalrooms[0][0], totalrooms[1][0], size[0][:2], 
                        ''.join([item.text_content() for item in address]).strip()))

    except Exception as e:
        logging.info(e)
        raise

allflats = getallflats()

for i in range(100):
    t = threading.Thread(target=process_queue)
    t.daemon = True
    t.start()

for flat in allflats:
    flat_queue.put(flat)

flat_queue.join()

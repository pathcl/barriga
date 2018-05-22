# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from tqdm import tqdm
from collections import deque
from lxml import html
import time
import requests
import sys
import concurrent.futures

class Flat:
    
    def __init__(self, results):
        self.results = results
        #self.commune = commune

    def _getflats(self):
        counter = self.results
        href = deque()

        print('Total pages to scrape: {}'.format(counter))
        print('Gathering every page...')

        for page in tqdm(range(0, counter)):
            url = 'https://www.economicos.cl/rm/departamento?operacion=Arriendo&dormitoriosDesde=2&pagina=%d#results' % (
                page)
            html = requests.get(url).text
            soup = BeautifulSoup(html, 'lxml')

            for a in soup.find_all('a', href=True):
                if 'propiedades' in a['href']:
                    href.append(url[:25] + a['href'])

        return set(href)
    
    def _cleanup(self, item):
        stripe = (item.strip() for item in item)
        clean = ''.join(stripe).replace(' ', '')
        return clean

        
    def flats(self, device):
        '''should return a dictionary each description'''
        r = requests.get(device).text
        tree = html.fromstring(r)
        commune = tree.xpath(
            '//*[@id="specs"]/ul/li[7]/text()')
        price = tree.xpath(
            '//*[@id="detalle"]/div[4]/div[1]/div[2]/div[2]/text()')
        bedrooms = tree.xpath(
            '//*[@id="specs"]/ul/li[3]/text()')
        size = tree.xpath(
            '//*[@id="specs"]/ul/li[5]/text()')
        address = tree.xpath(
            '//*[@id="wrapper"]/section/div/div/div[1]/article/div/div[2]/div[2]/div[2]/div[1]/p/text()')

        return dict(url=device, commune=self._cleanup(commune), price=self._cleanup(price)[2:], 
        bedrooms=self._cleanup(bedrooms), size=''.join(size))
        

    def process(self):
        devices = self._getflats()

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            hostname = {executor.submit(
                self.flats, device): device for device in devices}

            for future in concurrent.futures.as_completed(hostname):
                device = hostname[future]
                try:
                    data = future.result()
                except Exception as exc:
                    print('%r generated an exception: %s' % (device, exc))
                else:
                    #print('[{}] {}'.format(device, data))
                    print('{}'.format(data))

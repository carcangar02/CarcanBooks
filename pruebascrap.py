import html
import json
import random
import time

from bs4 import BeautifulSoup
import cloudscraper
import requests
from PIL import Image
from io import BytesIO


def scrap_capitulo(enlace):
    # Esperar entre 1 y 3 segundos antes de hacer la petición
    delay = random.uniform(1.5, 3)
    time.sleep(delay)
    print('1')
    scraper = cloudscraper.create_scraper()
    response = scraper.get(enlace)

    # Comprobar que la petición fue exitosa
    if response.status_code == 200:
        print('2')

        # Parsear el HTML con BeautifulSoup
        main = BeautifulSoup(response.text, 'html.parser')
        # Intentar selector principal
        contenido = main.find('article')
        print('contenido', contenido)
        if not contenido:
            # Fallback para URLs de capítulo en Novelarrow
            contenido = main.select_one('div.mx-auto min-w-0 max-w-full overflow-hidden')
        if contenido:
            try:
                print('3')

                for div in contenido.find_all('div'):
                    div.decompose()
            except:
                print('4')

                print("Error al eliminar divs")
            print(str(contenido))
        # Si no se encontró contenido devuelve cadena vacía
        return ''
scrap_capitulo('https://novelarrow.com/chapter/fates-slave-shadow-slave-x-honkai-star-rail/chapter-578-ghostbusters-xxxi')





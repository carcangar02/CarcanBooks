import cloudscraper
from bs4 import BeautifulSoup
# from libros.models import Extension
import time
import random
import re
import json
import html
import math

extension_nombre = 'Novelfire'
# extension = Extension.objects.get(nombre=extension_nombre)
enlace ="https://novelfire.net/book/shadow-slave/chapter-1"



def scrap_capitulo(enlace):
    # Esperar entre 1 y 3 segundos antes de hacer la petición
    delay = random.uniform(1.5, 3)
    time.sleep(delay)

    scraper = cloudscraper.create_scraper()
    response = scraper.get(enlace)

    # Comprobar que la petición fue exitosa
    if response.status_code == 200:
        # Parsear el HTML con BeautifulSoup
        main = BeautifulSoup(response.text, 'html.parser')
        contenido = main.select_one('div#content.clearfix')
        try:
            for div in contenido.find_all('div'):
                div.decompose()
        except:
            pass
        return print(str(contenido))


scrap_capitulo(enlace)
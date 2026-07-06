import cloudscraper
from bs4 import BeautifulSoup
from libros.models import Extension
import time
import random
import re
import json
import html
import math

# Updated extension name
extension_nombre = 'Novelarrow'
extension = Extension.objects.get(nombre=extension_nombre)

def scrap_capitulo(enlace):
    print('Scraping capitulo:', enlace)
    # Esperar entre 1 y 3 segundos antes de hacer la petición
    delay = random.uniform(1.5, 3)
    time.sleep(delay)

    scraper = cloudscraper.create_scraper()
    response = scraper.get(enlace)

    # Comprobar que la petición fue exitosa
    if response.status_code == 200:
        # Parsear el HTML con BeautifulSoup
        main = BeautifulSoup(response.text, 'html.parser')
        # Intentar selector principal
        contenido = main.select_one('div#content.clearfix')
        if not contenido:
            # Fallback para URLs de capítulo en Novelarrow
            contenido = main.select_one('div.chapter-content')
        if contenido:
            try:
                for div in contenido.find_all('div'):
                    div.decompose()
            except:
                pass
            return str(contenido)
        # Si no se encontró contenido devuelve cadena vacía
        return ''





def scrap_libro_details(enlace):
    scraper = cloudscraper.create_scraper()
    response = scraper.get(enlace)



    # Comprobar que la petición fue exitosa
    if response.status_code == 200:
        # Parsear el HTML con BeautifulSoup
        main = BeautifulSoup(response.text, 'html.parser')
        title_tag = main.find("h1")

        titulo_web = title_tag.get_text(strip=True) if title_tag else None

        slug = titulo_web.lower().replace("'", "").replace(" - ", "-").replace(" ", "-").replace(":", "")
        imagen = f"https://images.novelarrow.com/novel_328_490/{slug}.jpg"












        # Recoger al informacion de los capitulo
        enlace_cap = f"https://novelarrow.com/api-web/novels/{slug}/chapters?sort=asc"

        capitulos_array = []

        scraper2 = cloudscraper.create_scraper()
        response2 = scraper2.get(enlace_cap)

        if response2.status_code == 200:
            json_response = json.loads(response2.text)
            
            
            resultado = html.unescape(json_response['items'])
            for row in resultado:
                nombre_capitulo = row.get('chapter_name')
                enlace_capitulo = f"https://novelarrow.com/chapter/{slug}/{row.get('chapter_id')}"

                capitulos_array.append({
                    'title': nombre_capitulo,
                    'href': enlace_capitulo
                })

    info_libro = {
        'titulo': titulo_web,
        'foto': imagen,
        'capitulos': capitulos_array
    }
    return info_libro  # OUT    info_libro{titulo, foto, capitulos[{title, href}] }

def scrap_busqueda(input): 
    string_busqueda = input.strip().replace(" ", "+").lower()
    enlace = f"https://novelarrow.com/api-web/novels?limit=5&page=1&status=all&sort=SEARCH_KEYWORD&genre=ALL&keyword={string_busqueda}"

    scraper = cloudscraper.create_scraper()
    response = scraper.get(enlace)

    # Comprobar que la petición fue exitosa
    if response.status_code == 200:
            json_response = json.loads(response.text)
            
            
            resultado = html.unescape(json_response['items'])
    


            libros_resultado = []
    for row in resultado:
        slug = row.get('novel_id') or row.get('slug')
        titulo = row.get('novel_name') or row.get('title')
        foto = f"https://images.novelarrow.com/novel_240_360/{slug}.jpg"
        enlace_libro = f"https://novelarrow.com/novel/{slug}"
        libros_resultado.append({
            'titulo': titulo,
            'enlace': enlace_libro,
            'foto': foto,
            'libreria': 2,

        })
    return libros_resultado

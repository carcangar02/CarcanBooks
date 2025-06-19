import cloudscraper
from bs4 import BeautifulSoup
from libros.models import Extension
import time
import random
import re
import json
import html
import math




extension_nombre = 'Novelfire'
extension = Extension.objects.get(nombre=extension_nombre)







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
        return str(contenido)



def scrap_libro_details(enlace):

    scraper = cloudscraper.create_scraper()
    response = scraper.get(enlace)


    # Comprobar que la petición fue exitosa
    if response.status_code == 200:
        # Parsear el HTML con BeautifulSoup
        main = BeautifulSoup(response.text, 'html.parser')
        imagen = main.select_one('figure.cover img')
        titulo_web = main.find('h1', class_='novel-title text2row').text
        num_caps = main.select_one('div.header-stats span strong').text
        num_bucles = math.ceil(int(num_caps) / 100)
        titulo_enlace = titulo_web.strip().replace("-", "").replace(" ", "-").lower().replace(":","").replace(",","").replace(".","").replace("!","").replace("'", "")
    capitulos_array = []
    
    for i in range(num_bucles):
        
        paginas = i +1

        enlace_capitulos = f"https://novelfire.net/book/{titulo_enlace}/chapters?page={paginas}"
        scraper_capitulos = cloudscraper.create_scraper()
        response_capitulos = scraper_capitulos.get(enlace_capitulos)

        if response_capitulos.status_code == 200:
            main = BeautifulSoup(response_capitulos.text, 'html.parser')
            
            capitulos_ul = main.find('ul', class_='chapter-list')
            capitulos_lista = capitulos_ul.find_all('li')
            
            
            for cap in capitulos_lista:
                cap_info = cap.find('a')
                capitulos_array.append({
                    'title': cap_info['title'],
                    'href': cap_info['href']
                })
                
                

    info_libro = {
        'titulo': titulo_web,
        'foto': imagen['data-src'],
        'capitulos': capitulos_array
    }
    return info_libro ## OUT    info_libro{titulo, foto, capitulos[{title, href}] }





def scrap_busqueda(input): 
    string_busqueda = input.strip().replace(" ", "%20").lower()
    enlace = f"https://novelfire.net/ajax/searchLive?inputContent={string_busqueda}"

    scraper = cloudscraper.create_scraper()
    response = scraper.get(enlace)

    # Comprobar que la petición fue exitosa
    if response.status_code == 200:
        # Parsear el HTML con BeautifulSoup
        json_response = json.loads(response.text)

        html_interno = html.unescape(json_response['html'])

    # Parseamos ese HTML con BeautifulSoup
        soup = BeautifulSoup(html_interno, 'html.parser')


        libros_resultado = []
        for row in soup.select('li.novel-item'):
            enlace = row.find('a')['href']
            imagen = row.find('img')['src']
            titulo = row.find('h4', class_='novel-title').text.strip()
            libros_resultado.append({
                'titulo': titulo,
                'enlace': enlace,
                'foto': imagen,
                'libreria': 2,
                'extension': extension.pk

            })
    return libros_resultado
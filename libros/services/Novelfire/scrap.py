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

    slug_libro = enlace.split("/")[-1]
    print(slug_libro)
    # Comprobar que la petición fue exitosa
    if response.status_code == 200:
        # Parsear el HTML con BeautifulSoup
        main = BeautifulSoup(response.text, 'html.parser')
        report_interno = main.find('a', id='novel-report')
        libro_id_interno = report_interno.get('report-post_id')
        imagen = main.select_one('figure.cover img')
        titulo_web = main.find('h1', class_='novel-title text2row').text



        enlace_capitulos_base = f'https://novelfire.net/listChapterDataAjax?post_id={libro_id_interno}&draw=1&columns%5B0%5D%5Bdata%5D=title&columns%5B0%5D%5Bname%5D=&columns%5B0%5D%5Bsearchable%5D=true&columns%5B0%5D%5Borderable%5D=false&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=created_at&columns%5B1%5D%5Bname%5D=&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=true&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=n_sort&columns%5B2%5D%5Bname%5D=&columns%5B2%5D%5Bsearchable%5D=false&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=2&order%5B0%5D%5Bdir%5D=asc&start=0&length=-1&search%5Bvalue%5D=&search%5Bregex%5D=false&_=1765977081754'
        scraper_capitulos = cloudscraper.create_scraper()
        response = scraper_capitulos.get(enlace_capitulos_base)

        # Comprobar que la petición fue exitosa
        if response.status_code == 200:
            # Parsear el HTML con BeautifulSoup
            json_response = json.loads(response.text)
            
        capitulos_array = []
        
        resultado = html.unescape(json_response['data'])

        for row in resultado:
                slug_capitulo_enlace = row["slug"]
                slug_corte = re.search(r'chapter-\d+', slug_capitulo_enlace)
                if slug_corte:
                    n_capitulo_enlace = slug_corte.group(0)
                    
                    capitulos_array.append({
                        'title': row["title"],
                        'href': f'https://novelfire.net/book/{slug_libro}/{n_capitulo_enlace}' #------------------------------------------- PROBLEMA , ME FALTA EL SLUG DEL LIBRO
                    })


    info_libro = {
        'titulo': titulo_web,
        'foto': imagen['src'],
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
        
        
        resultado = html.unescape(json_response['data'])



        libros_resultado = []
        for row in resultado:
            enlace = f'https://novelfire.net/book/{row["slug"]}'
            titulo = row['title']
            libros_resultado.append({
                'titulo': titulo,
                'enlace': enlace,
                'foto': f'https://novelfire.net/{row["image"]}',
                'libreria': 2,
                'extension': extension.pk

            })
    return libros_resultado
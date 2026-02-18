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
        imagen = main.select_one('figure.cover img')
        titulo_web = main.find('h1', class_='novel-title text2row').text


        # Recoger al informacion de los capitulo
        enlace= f"https://novelfire.net/book/{slug_libro}/chapters"
        
        capitulos_array = []

        scraper2 = cloudscraper.create_scraper()
        response2 = scraper2.get(enlace)


        if response2.status_code == 200:
            main2 = BeautifulSoup(response2.text, 'html.parser')

            items = main2.find_all('li', class_='page-item')

            if len(items) >= 2:

                li_intermedios = items[1:-1]

                ultimo_numero = li_intermedios[-1].get_text(strip=True)
                
        for i in range(1, int(ultimo_numero)+1):
            enlace = f"https://novelfire.net/book/{slug_libro}/chapters?page={i}"
            scraper3 = cloudscraper.create_scraper()
            response3 = scraper3.get(enlace)

             # Comprobar que la petición fue exitosa
            if response3.status_code == 200:
                main3 = BeautifulSoup(response3.text, 'html.parser')


                capitulos = main3.select('ul.chapter-list li a')

                for cap in capitulos:
                    nombre_capitulo = cap.find('strong', class_='chapter-title').get_text(strip=True)
                    enlace_capitulo = cap['href']
                    capitulos_array.append({
                        'title': nombre_capitulo,
                        'href': enlace_capitulo })



        






    info_libro = {
        'titulo': titulo_web,
        'foto': imagen['src'],
        'capitulos': capitulos_array
    }

    return info_libro ## OUT    info_libro{titulo, foto, capitulos[{title, href}] }





def scrap_busqueda(input): 
    string_busqueda = input.strip().replace(" ", "%20").lower()
    enlace = f"https://novelfire.net/ajax/searchLive?keyword={string_busqueda}&type=title"

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
import cloudscraper
from bs4 import BeautifulSoup
from libros.models import Extension
import time
import random

extension_nombre = 'Novelbin'
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
        contenido = main.find('div', class_='chr-c')
        for div in contenido.find_all('div'):
            div.decompose()
        
        return str(contenido)








def scrap_libro_details(enlace):

    scraper = cloudscraper.create_scraper()
    response = scraper.get(enlace)


    # Comprobar que la petición fue exitosa
    if response.status_code == 200:
        # Parsear el HTML con BeautifulSoup
        main = BeautifulSoup(response.text, 'html.parser')
        imagen = main.find('img', class_='lazy')
        titulo_web = main.find('h3', class_='title')


    titulo_enlace = titulo_web.text.strip().replace(" ", "-").lower().replace(":","").replace(",","").replace(".","").replace("!","")

    enlace_capitulos = f"https://novelbin.com/ajax/chapter-archive?novelId={titulo_enlace}"
    scraper_capitulos = cloudscraper.create_scraper()
    response_capitulos = scraper_capitulos.get(enlace_capitulos)

    if response_capitulos.status_code == 200:
        main = BeautifulSoup(response_capitulos.text, 'html.parser')
        capitulos_lista = main.find_all('a')
        capitulos_array = []
        for cap in capitulos_lista:
            capitulos_array.append({
                'title': cap.text.strip(),
                'href': cap['href']
            })

    info_libro = {
        'titulo': titulo_web.text,
        'foto': imagen['data-src'],
        'capitulos': capitulos_array
    }
    return info_libro ## OUT    info_libro{titulo, foto, capitulos[{title, href}] }











def scrap_busqueda(input):
    string_busqueda = input.strip().replace(" ", "+").lower()
    enlace = f"https://novelbin.me/search?keyword={string_busqueda}"

    scraper = cloudscraper.create_scraper()
    response = scraper.get(enlace)

    # Comprobar que la petición fue exitosa
    if response.status_code == 200:
        # Parsear el HTML con BeautifulSoup
        main = BeautifulSoup(response.text, 'html.parser')
        div_busqueda = main.find('div', class_='list list-novel col-xs-12')
        libros_resultado = []
        for row in div_busqueda.find_all('div', class_='row'):
            imagen = row.find('img', class_='cover')
            enlace = row.find('a')['href']
            titulo = row.find('h3', class_='novel-title').text.strip()
            libros_resultado.append({
                'titulo': titulo,
                'enlace': enlace,
                'foto': imagen['src'],
                'libreria': 2,
                'extension': extension.pk

            })
    return libros_resultado
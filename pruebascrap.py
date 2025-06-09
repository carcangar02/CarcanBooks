import cloudscraper
from bs4 import BeautifulSoup
enlace = 'https://novelbin.com/b/mother-of-learning/chapter-79'

def scrap_capitulo(enlace):
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
print(scrap_capitulo(enlace))

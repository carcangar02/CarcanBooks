import cloudscraper
from bs4 import BeautifulSoup
input = input('Input: ')
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
            })
    print(libros_resultado)
scrap_busqueda(input)

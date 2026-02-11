from ebooklib import epub
from io import BytesIO

import requests
from ebooklib import epub
from io import BytesIO

def crear_ebook(titulo, capitulos_html, portada_url=None):
    book = epub.EpubBook()
    book.set_title(titulo)
    book.add_author('Carlos Cantos Garcia')

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Referer": "https://novelfire.net/"
    }

    if portada_url:
        try:
            response = requests.get(portada_url, headers=headers, timeout=10)
            response.raise_for_status() # Lanza una excepción si hay un error (403, 404, etc.)

            book.set_cover("cover.jpg", response.content)
        except Exception as e:
            pass

    epub_capitulos = []

    for idx, contenido_html in enumerate(capitulos_html, start=1):
        if not contenido_html.strip():
            print(f'⚠️ Capítulo {idx} vacío.')

        capitulo = epub.EpubHtml(
            title=f'Capítulo {idx}',
            file_name=f'chap_{idx}.xhtml',
            content=contenido_html
        )
        book.add_item(capitulo)
        epub_capitulos.append(capitulo)

    book.toc = tuple(epub_capitulos)

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    book.spine = ['nav'] + epub_capitulos

    buffer = BytesIO()
    epub.write_epub(buffer, book)
    buffer.seek(0)
    contenido = buffer.getvalue()
    buffer.close()

    return contenido

 
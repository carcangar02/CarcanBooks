from ebooklib import epub
from io import BytesIO

def crear_ebook(titulo, capitulos_html):
    # Crear libro
    book = epub.EpubBook()
    book.set_title(titulo)
    book.add_author('Carlos Cantos Garcia')

    epub_capitulos = []

    for idx, contenido_html in enumerate(capitulos_html, start=1):
        if not contenido_html.strip():
            print(f'⚠️ Capítulo {idx} vacío.')
        else:
            print(f'✅ Capítulo {idx} OK ({len(contenido_html)} bytes)')
        capitulo = epub.EpubHtml(
            title=f'Capítulo {idx}',
            file_name=f'chap_{idx}.xhtml',
            content=contenido_html
        )
        book.add_item(capitulo)
        epub_capitulos.append(capitulo)

    # Tabla de contenidos
    book.toc = tuple(epub_capitulos)

    # Navegación obligatoria para EPUB
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Definir el orden de lectura
    book.spine = ['nav'] + epub_capitulos

    buffer = BytesIO()
    epub.write_epub(buffer, book)
    buffer.seek(0)

    contenido = buffer.getvalue()  # aquí sacamos el contenido
    buffer.close()  # y cerramos para evitar problemas con el destructor de ZipFile

    return contenido

 
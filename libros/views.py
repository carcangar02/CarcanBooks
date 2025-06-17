from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import Libreria, Libro, Capitulos, Extension
import importlib
import json
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed



def librerias_menu(request):
    librerias = Libreria.objects.values('pk', 'nombre')
    info_libros = []
    libros_qs = Libro.objects.prefetch_related('capitulos').all()



    for libro in libros_qs:
        try:

            info_libros.append({
                'id': libro.id,
                'titulo': libro.titulo,
                'foto': libro.foto,
                'libreria': libro.libreria_id
            })



        except Exception as e:
            print(f"Error procesando el libro {libro.titulo} (ID {libro.id}): {e}")


    context = {
        'librerias': list(librerias),
        'info_libros': json.dumps(info_libros),
    }
    return render(request, 'libros/librerias_menu.html', context)










def libro_details(request, libro_id=None, info_coded=None):
    if libro_id is None and info_coded is not None:
        
        decoded_bytes = base64.b64decode(info_coded)
        info_decoded = decoded_bytes.decode('utf-8')
        info_parts = info_decoded.split('&&&%%%')
        enlace = info_parts[0]
        extension = info_parts[1]

        libro_exist = Libro.objects.filter(enlace=enlace).exists()
        if libro_exist:
            libro_db = Libro.objects.get(enlace=enlace)
            capitulos = libro_db.capitulos.all().values('id', 'titulo', 'enlace', 'visto')
            libro_id = libro_db.pk
            titulo = libro_db.titulo
            foto = libro_db.foto
            enlace = libro_db.enlace
            libreria = libro_db.libreria
            extension = libro_db.extension.nombre
        else:
            extension_scrap = importlib.import_module(f'libros.services.{extension}.scrap')
            libro_scrapped = extension_scrap.scrap_libro_details(enlace) 
            capitulos = []
            libro_id = None
            titulo= libro_scrapped['titulo']
            foto = libro_scrapped['foto']
            libreria = None
            try:
                last_id = Capitulos.objects.latest('id').id
            except:
                last_id=0

            for cap in libro_scrapped['capitulos']:
                last_id += 1
                capitulos.append({
                    'id': last_id,
                    'titulo': cap['title'],
                    'enlace': cap['href'],
                    'visto': False
            })




    else:      


        if libro_id:       
            libro_db = Libro.objects.get(pk=libro_id)
            capitulos = libro_db.capitulos.all().values('id', 'titulo', 'enlace', 'visto')
            capitulos = capitulos.order_by('id')
            extension_scrap = importlib.import_module(f'libros.services.{libro_db.extension.nombre}.scrap')
            libro_scrapped = extension_scrap.scrap_libro_details(libro_db.enlace)
            titulo=libro_db.titulo
            enlace = libro_db.enlace
            foto = libro_db.foto
            libreria = libro_db.libreria
            extension = libro_db.extension.nombre

    
        num_caps_db = libro_db.num_capitulos
        num_caps_web=len(libro_scrapped['capitulos'])

        if num_caps_db != num_caps_web and num_caps_web > 0:
            diferencia = num_caps_web - num_caps_db
            for cap in libro_scrapped['capitulos'][-diferencia:]:
                if 'href' in cap and 'title' in cap:
                    nuevo_capitulo = Capitulos(
                        enlace=cap['href'],
                        libro=libro_db,
                        titulo=cap['title'],
                        visto=False
                    )
                    nuevo_capitulo.save()
        

                else:
                    print(f"Capítulo sin enlace o título en libro {libro_db.titulo} (ID {libro_db.id}): {cap}")
            new_num_cap = libro_db.capitulos.count()
            libro_db.num_capitulos = new_num_cap
            libro_db.save()
        






    librerias  = Libreria.objects.values('pk', 'nombre')

    info_libro = {
        'id': libro_id,
        'enlace': enlace,
        'titulo': titulo,
        'foto': foto,
        'libreria': libreria,
        'extension': extension
    }

    context = {
        'librerias': list(librerias),
        'libro': info_libro,
        'capitulos': json.dumps(list(capitulos)),
    }


    return render(request, "libros/libro_details.html" , context)









def lector(request, capitulo_id):
    try:
        capitulo = Capitulos.objects.get(pk=capitulo_id)
        libro = Libro.objects.get(id=capitulo.libro.pk)
        extension_scrap = importlib.import_module(f'libros.services.{libro.extension.nombre}.scrap')
        contenido_capitulo = extension_scrap.scrap_capitulo(capitulo.enlace)
        siguiente = capitulo_id +1
        anterior = capitulo_id -1
        siguiente_cap = Capitulos.objects.get(pk=siguiente)
        anterior_cap = Capitulos.objects.get(pk=anterior)
        if siguiente_cap.libro.pk != libro.pk:
            siguiente=None
        if anterior_cap.libro.pk != libro.pk:
            anterior=None

        context = {
            'anterior':anterior,
            'siguiente':siguiente,
            'capitulo': capitulo,
            'contenido': contenido_capitulo,
        }
        return render(request, "libros/lector.html", context)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    





def buscador(request):
    return render(request, "libros/buscador.html" )






def busqueda(request):
    input_busqueda = request.POST.get('input_busqueda')
    Extensiones = Extension.objects.values('nombre')
    array_resultados = []
    
    try:
        for extension in Extensiones:
            nombre_extension = extension['nombre']
            
            nombre_extension_modulo = importlib.import_module(f'libros.services.{nombre_extension}.scrap')
            resultado_busqueda = nombre_extension_modulo.scrap_busqueda(input_busqueda)
            array_resultados.append({
                'nombre_extension': nombre_extension,
                'resultados': resultado_busqueda
            })
            
        return JsonResponse(array_resultados, safe=False, status=200)
    except ImportError as e:
        print(f"Error al importar el módulo de extensión {nombre_extension}: {e}")
    except Exception as e:
        print(input_busqueda)
        print(f"Error al ejecutar la búsqueda para la extensión {nombre_extension}: {e}")







def cambio_status(request):
    try:
        status=request.POST.get('status')
        libro_id = request.POST.get('libro_id')

        if status == 'false':
            libro = Libro.objects.get(pk=libro_id)
            libro.delete()
            return JsonResponse({'message': 'Libro eliminado correctamente.'}, status=200)
        if status == 'true':
            libro_info = json.loads(request.POST.get('libro_info'))
            libreria_create = Libreria.objects.get(id=2)
            extension_create = Extension.objects.get(nombre=libro_info.get('extension'))
            print(f"{libro_info.get('titulo')},      {libro_info.get('enlace')}       {libro_info.get('extension')} ")
            Libro.objects.create(
                titulo=libro_info.get('titulo'),
                enlace=libro_info.get('enlace'),
                foto=libro_info.get('foto'),
                libreria=libreria_create,
                extension=extension_create
            )
            return JsonResponse({'message': 'Libro guardado correctamente.'}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)











def cambiar_libreria(request):
    try:
        libro_id = request.POST.get('libro_id')
        nueva_libreria_id = request.POST.get('nueva_libreria_id')
        print(libro_id, nueva_libreria_id)
        libro = Libro.objects.get(pk=libro_id)
        nueva_libreria = Libreria.objects.get(pk=nueva_libreria_id)

        libro.libreria = nueva_libreria
        libro.save()

        return JsonResponse({'message': 'Librería cambiada correctamente.'}, status=200)
    except Libro.DoesNotExist:
        return JsonResponse({'error': 'Libro no encontrado.'}, status=404)
    except Libreria.DoesNotExist:
        return JsonResponse({'error': 'Librería no encontrada.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)   
    





def descarga_to_ebook(request) :
    try:
        libro_id = request.POST.get('libro_id')
        libro = Libro.objects.get(pk=libro_id)
        capitulos = Capitulos.objects.filter(libro=libro).values('enlace', 'libro')
        extension_scrap = importlib.import_module(f'libros.services.{libro.extension.nombre}.scrap')
        toEbbok = importlib.import_module('libros.services.toEbook')
        html_caps = []


        for cap in capitulos:
            contenido = extension_scrap.scrap_capitulo(cap['enlace'])
            html_caps.append(contenido)

    



        bueffer_ebook = toEbbok.crear_ebook(libro.titulo, html_caps)


        response = HttpResponse(bueffer_ebook, content_type='application/epub+zip')
        response['Content-Disposition'] = f'attachment; filename="{libro.titulo}.epub"'

        return response


    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)}, status=500)
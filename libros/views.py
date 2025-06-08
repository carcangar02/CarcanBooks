from django.shortcuts import render
from django.http import JsonResponse
from .models import Libreria, Libro, Capitulos, Extension
import importlib
import json



def librerias_menu(request):
    librerias = Libreria.objects.values('pk', 'nombre')

    info_libros = []
    libros_qs = Libro.objects.prefetch_related('capitulos').all()





    for libro in libros_qs:
        try:
            num_caps_db = len(libro.capitulos.all())
            extension_scrap = importlib.import_module(f'libros.services.{libro.extension.nombre}.scrap')
            libro_scrapped = extension_scrap.scrap_libro_details(libro)
            info_libros.append({
                'id': libro.id,
                'titulo': libro.titulo,
                'foto': libro_scrapped['foto'],
                'libreria': libro.libreria_id
            })
            num_caps_web = len(libro_scrapped['capitulos'])
            if num_caps_db != num_caps_web and num_caps_web > 0:
                diferencia = num_caps_web - num_caps_db
                for cap in libro_scrapped['capitulos'][-diferencia:]:
                    if 'href' in cap and 'title' in cap:
                        nuevo_capitulo = Capitulos(
                            enlace=cap['href'],
                            libro=libro,
                            titulo=cap['title'],
                            visto=False
                        )
                        nuevo_capitulo.save()
                    else:
                        print(f"Capítulo sin enlace o título en libro {libro.titulo} (ID {libro.id}): {cap}")




        except Exception as e:
            print(f"Error procesando el libro {libro.titulo} (ID {libro.id}): {e}")


    context = {
        'librerias': list(librerias),
        'info_libros': json.dumps(info_libros),
    }
    return render(request, 'libros/librerias_menu.html', context)










def libro_details(request, libro_id):
    try:
        if libro_id:       
            libro = Libro.objects.get(pk=libro_id)
            capitulos = libro.capitulos.all().values('id', 'titulo', 'enlace', 'visto')
            extension_scrap = importlib.import_module(f'libros.services.{libro.extension.nombre}.scrap')
            libro_scrapped = extension_scrap.scrap_libro_details(libro)
        




        librerias  = Libreria.objects.values('pk', 'nombre')

        info_libro = {
            'id': libro_id,
            'enlace': libro.enlace,
            'titulo': libro_scrapped['titulo'],
            'foto': libro_scrapped['foto'],
            'capitulos':libro_scrapped['capitulos'],
            'libreria': libro.libreria.pk,
            'extension': libro.extension.nombre
        }

        context = {
            'librerias': list(librerias),
            'libro': info_libro,
            'capitulos': json.dumps(list(capitulos)),
        }


        return render(request, "libros/libro_details.html" , context)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)








def lector(request, capitulo_id):
    try:
        capitulo = Capitulos.objects.get(pk=capitulo_id)
        extension_scrap = importlib.import_module(f'libros.services.{capitulo.libro.extension.nombre}.scrap')
        contenido_capitulo = extension_scrap.scrap_capitulo(capitulo.enlace)
        context = {
            'capitulo': capitulo,
            'contenido': contenido_capitulo,
        }
        return render(request, "libros/lector.html", context)
    except Capitulos.DoesNotExist:
        return JsonResponse({'error': 'Capítulo no encontrado.'}, status=404)
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
            Libro.objects.create(
                titulo=libro_info.get('titulo'),
                enlace=libro_info.get('enlace'),
                libreria=2,
                extension=libro_info.get('extension')
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
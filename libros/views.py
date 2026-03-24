from django.shortcuts import redirect, render
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from .models import Libreria, Libro, Capitulos, Extension
import importlib
import json
import base64
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required






def login_view(request):
    cookie_info = request.COOKIES.get('carcanbooks_info')
    if cookie_info:
        try:
            username, password = cookie_info.split('&&&%%%')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user) 
                return redirect('/libros/librerias/')
        except Exception as e:
            print(f"Error al procesar la cookie de autenticación: {e}")
    else:
        return render(request, "libros/login_view.html")

#esta funcion sirve para hacer login recoge la informacino del formulario de la vista ,
#  y compara con la base de datos, si ya tienes una cookie te hace el login automaticamente y te redirecciona

def login_action(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        response = JsonResponse({
            'message': 'Inicio de sesión exitoso. Redirigiendo...',
            'redirect_url': '/libros/librerias/'
        })
        response.set_cookie('carcanbooks_info', f'{username}&&&%%%{password}', max_age=30*24*60*60)  # Cookie válida por 30 días
        return response
    else:
        # Error de autenticación
        return JsonResponse({'error': 'Credenciales inválidas.'}, status=401)


def signup_view(request):
    return render(request, "libros/signup_view.html")



def signup_action(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        response = JsonResponse({
            'message': 'Registro exitoso. Redirigiendo...',
            'redirect_url': '/libros/librerias/'
        })
        response.set_cookie('carcanbooks_info', f'{username}&&&%%%{password}', max_age=30*24*60*60)  # Cookie válida por 30 días
        return response
        
    return JsonResponse({"error": "Método no permitido."}, status=405)





@login_required
def librerias_menu(request):
    user_id = request.user.id

    librerias_qs = Libreria.objects.filter(usuario=user_id).prefetch_related('libros')

    librerias = []
    for libreria in librerias_qs:
        librerias.append({
            'pk': libreria.pk,
            'nombre': libreria.nombre,
            'libros_pk': [lib.pk for lib in libreria.libros.all()]  
        })


    info_libros = []
    lista_libros = Libreria.objects.filter(usuario=user_id).values('libros')

    libros_qs = Libro.objects.filter(pk__in=lista_libros).distinct()




    for libro in libros_qs:
        try:

            info_libros.append({
                'id': libro.id,
                'titulo': libro.titulo,
                'foto': libro.foto,
            })



        except Exception as e:
            print(f"Error procesando el libro {libro.titulo} (ID {libro.id}): {e}")


    context = {
        'librerias': json.dumps(librerias),
        'info_libros': json.dumps(info_libros),
    }
    return render(request, 'libros/librerias_menu.html', context)







@login_required

def crear_libreria(request):
    try:
        nombre_libreria = request.POST.get('nombreLista')
        usuario = request.user
        nueva_libreria = Libreria.objects.create(nombre=nombre_libreria, usuario=usuario)
        return JsonResponse({'message': 'Librería creada correctamente.', 'libreria_id': nueva_libreria.id}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    



    
@login_required

def borrar_libreria(request):
    try:
        libreria_id = request.POST.get('libreria_id')
        print(libreria_id)
        libreria = Libreria.objects.get(pk=libreria_id)
        libreria.delete()
        return JsonResponse({'message': 'Librería eliminada correctamente.'}, status=200)
    except Libreria.DoesNotExist:
        return JsonResponse({'error': 'Librería no encontrada jjjj.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)







@login_required

def libro_details(request, libro_id=None, info_coded=None):
    user_id = request.user.id

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
            extension = libro_db.extension.nombre
            
        objetos_a_crear = []
        for cap in libro_scrapped['capitulos']:
            objetos_a_crear.append(
                Capitulos(
                    libro=libro_db,
                    enlace=cap['href'],
                    titulo=cap['title'],
                    visto=False
                )
            )


        Capitulos.objects.bulk_create(
            objetos_a_crear, 
            ignore_conflicts=True 
        )


        libro_db.num_capitulos = libro_db.capitulos.count()
        libro_db.save()

        






    librerias_qs = Libreria.objects.filter(usuario=user_id).prefetch_related('libros')

    librerias = []
    for libreria in librerias_qs:
        librerias.append({
            'pk': libreria.pk,
            'nombre': libreria.nombre,
            'libros_pk': [lib.pk for lib in libreria.libros.all()]  
        })

    info_libro = {
        'id': libro_id,
        'enlace': enlace,
        'titulo': titulo,
        'foto': foto,
        'extension': extension
    }

    context = {
        'librerias': json.dumps(librerias),
        'libro': info_libro,
        'capitulos': json.dumps(list(capitulos)),
    }


    return render(request, "libros/libro_details.html" , context)








@login_required

def lector(request, capitulo_id):
    try:
        capitulo = Capitulos.objects.get(pk=capitulo_id)
        libro = Libro.objects.get(id=capitulo.libro.pk)
        extension_scrap = importlib.import_module(f'libros.services.{libro.extension.nombre}.scrap')
        contenido_capitulo = extension_scrap.scrap_capitulo(capitulo.enlace)
        siguiente = capitulo_id +1
        anterior = capitulo_id -1

        try:
            siguiente_cap = Capitulos.objects.get(pk=siguiente) 
            if siguiente_cap.libro.pk != libro.pk:
                siguiente=None
        except:
            siguiente=None
        
        try:
            anterior_cap = Capitulos.objects.get(pk=anterior)
            if anterior_cap.libro.pk != libro.pk:
                anterior=None
        except:
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
    




@login_required

def buscador(request):
    return render(request, "libros/buscador.html" )





@login_required

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









@login_required

def cambiar_libreria(request):
    try:
        libro_id = request.POST.get('libro_id') #3
        libreria_id_old = request.POST.get('libreria_id')  #18
        nueva_libreria_id = request.POST.get('nueva_libreria_id') #delete
        delete = request.POST.get('delete') == 'true'
        libro=Libro.objects.get(id=libro_id)

        if delete:
            libreria=Libreria.objects.get(id=libreria_id_old)
            libreria.libros.remove(libro)
            libreria.save()
        else:
            if libreria_id_old:
                libreria = Libreria.objects.get(id=libreria_id_old)
                libreria.libros.remove(libro)

            nueva_libreria = Libreria.objects.get(pk=nueva_libreria_id)

            nueva_libreria.libros.add(libro)
            nueva_libreria.save()

        return JsonResponse({'message': 'Librería cambiada correctamente.'}, status=200)
    except Libro.DoesNotExist:
        return JsonResponse({'error': 'Libro no encontrado.'}, status=404)
    except Libreria.DoesNotExist:
        return JsonResponse({'error': 'Librería no encontrada.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)   

def crear_libro(request):
    try:
        titulo = request.POST.get('titulo')
        enlace = request.POST.get('enlace')
        foto = request.POST.get('foto')
        extension_POST = request.POST.get('extension')
        extension = Extension.objects.get(nombre = extension_POST)

        Libro.objects.create(
            titulo=titulo,
            enlace=enlace,
            foto=foto,
            extension=extension,
        )
        nuevo_libro = Libro.objects.get(titulo=titulo)

        return JsonResponse({
                    'message': 'Libro creado correctamente.',
                    'id': nuevo_libro.id  # <--- Enviamos el ID
                }, status=201)
                
    except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)



def carga_dinamica_librerias(request):
    user_id = request.user.id

    librerias_qs = Libreria.objects.filter(usuario=user_id).prefetch_related('libros')

    librerias = []
    for libreria in librerias_qs:
        librerias.append({
            'pk': libreria.pk,
            'nombre': libreria.nombre,
            'libros_pk': [lib.pk for lib in libreria.libros.all()]  
        })

    context = {
            'librerias': librerias,
        }
    return JsonResponse(context, safe=False, status=200)


@login_required

def descarga_to_ebook(request) :
    try:
        libro_id = request.POST.get('libro_id')
        libro = Libro.objects.get(pk=libro_id)
        capitulos = Capitulos.objects.filter(libro=libro).values('enlace', 'libro').order_by('id')
        extension_scrap = importlib.import_module(f'libros.services.{libro.extension.nombre}.scrap')
        toEbbok = importlib.import_module('libros.services.toEbook')
        html_caps = []

        capitulos_list = list(capitulos)
        total_caps = len(capitulos_list)
        print(f"Iniciando descarga de {total_caps} capítulos para libro '{libro.titulo}' (ID {libro_id})")

        if total_caps == 0:
            print("No hay capítulos para descargar.")
        else:
          
            max_workers = min(5, total_caps)  
            max_retries = 3
            retry_backoff_base = 2  # segundos

            print(f"Usando hasta {max_workers} hilos para descargar capítulos en paralelo (reintentos={max_retries}).")

            resultados = [None] * total_caps
            completed = 0
            failed_count = 0

            def fetch_with_retries(enlace, idx_local):
            
                for attempt in range(1, max_retries + 1):
                    try:
                        contenido_local = extension_scrap.scrap_capitulo(enlace)
                        
                        if contenido_local:
                            return contenido_local
                        else:
                            print(f"[Cap {idx_local}] Contenido vacío en intento {attempt}.")
                    except Exception as e:
                        print(f"[Cap {idx_local}] Error en intento {attempt}: {e}")
                
                    sleep_for = retry_backoff_base ** attempt
                    time.sleep(sleep_for + 0.5)
                
                return ""

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_idx = {}
                for idx, cap in enumerate(capitulos_list, start=1):
                    enlace = cap.get('enlace')
                    future = executor.submit(fetch_with_retries, enlace, idx)
                    future_to_idx[future] = idx
                    
                    time.sleep(0.1)

                for future in as_completed(future_to_idx):
                    idx = future_to_idx[future]
                    try:
                        contenido = future.result()
                    except Exception as e:
                        print(f"Error inesperado en futuro del capítulo {idx}: {e}")
                        contenido = ""
                    if not contenido:
                        failed_count += 1
                    resultados[idx - 1] = contenido
                    completed += 1
                    percent = int((completed / total_caps) * 100)
                    print(f"Progreso descarga: {completed}/{total_caps} capítulos ({percent}%)")

           
            print(f"Descarga completada: {completed} capítulos descargados, {failed_count} fallidos.")      

            html_caps = resultados

    



        bueffer_ebook = toEbbok.crear_ebook(libro.titulo, html_caps, libro.foto)


        response = HttpResponse(bueffer_ebook, content_type='application/epub+zip')
        response['Content-Disposition'] = f'attachment; filename="{libro.titulo}.epub"'

        return response


    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)}, status=500)


def lastLibro(request):
    try:
        last_libro = Libro.objects.latest('id')
        next_id = last_libro.id +1

        return JsonResponse({'last_libro_id': next_id}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)








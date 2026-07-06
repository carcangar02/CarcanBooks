from django.shortcuts import redirect, render
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from .models import Libreria, Libro, Capitulos, Extension, Perfil
from django.core.paginator import Paginator
import importlib
import json
import base64
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt






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
    perfil, created = Perfil.objects.get_or_create(usuario=request.user)
    vistos_ids = set(perfil.capitulos_vistos.values_list('id', flat=True))

    if libro_id is None and info_coded is not None:
        decoded_bytes = base64.b64decode(info_coded)
        info_decoded = decoded_bytes.decode('utf-8')
        info_parts = info_decoded.split('&&&%%%')
        enlace = info_parts[0]
        extension = info_parts[1]

        libro_exist = Libro.objects.filter(enlace=enlace).exists()
        if libro_exist:
            libro_db = Libro.objects.get(enlace=enlace)
            libro_id = libro_db.pk
            titulo = libro_db.titulo
            foto = libro_db.foto
            enlace = libro_db.enlace
            extension = libro_db.extension.nombre
            capitulos_qs = libro_db.capitulos.all().order_by('id')
        else:
            extension_scrap = importlib.import_module(f'libros.services.{extension}.scrap')
            libro_scrapped = extension_scrap.scrap_libro_details(enlace) 
            capitulos_data = []
            titulo = libro_scrapped['titulo']
            foto = libro_scrapped['foto']
            
            for cap in libro_scrapped['capitulos']:
                capitulos_data.append({
                    'id': None,
                    'titulo': cap['title'],
                    'enlace': cap['href'],
                    'visto': False
                })
            
            # For scrapped books not in DB, we don't have IDs yet, so no pagination/search for now
            # or we create the book first? The current code seems to wait for 'crear_libro'
            context = {
                'librerias': json.dumps([]), # Will be loaded dynamically or handled later
                'libro': {'id': None, 'enlace': enlace, 'titulo': titulo, 'foto': foto, 'extension': extension},
                'capitulos': json.dumps(capitulos_data),
            }
            return render(request, "libros/libro_details.html" , context)

    else:      
        if libro_id:       
            libro_db = Libro.objects.get(pk=libro_id)
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
                        titulo=cap['title']
                    )
                )

            Capitulos.objects.bulk_create(objetos_a_crear, ignore_conflicts=True)
            libro_db.num_capitulos = libro_db.capitulos.count()
            libro_db.save()
            capitulos_qs = libro_db.capitulos.all().order_by('id')

    # Search and Pagination
    q = request.GET.get('q', '')
    if q:
        capitulos_qs = capitulos_qs.filter(titulo__icontains=q)
    
    paginator = Paginator(capitulos_qs, 100) # 100 chapters per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    capitulos_list = []
    for cap in page_obj:
        capitulos_list.append({
            'id': cap.id,
            'titulo': cap.titulo,
            'enlace': cap.enlace,
            'visto': cap.id in vistos_ids
        })

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
        'capitulos': json.dumps(capitulos_list),
        'page_obj': page_obj,
        'q': q,
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'capitulos': capitulos_list,
            'has_next': page_obj.has_next(),
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None
        })

    return render(request, "libros/libro_details.html" , context)


@login_required
def marcar_visto(request):
    if request.method == 'POST':
        capitulo_id = request.POST.get('capitulo_id')
        visto = request.POST.get('visto') == 'true'
        perfil, _ = Perfil.objects.get_or_create(usuario=request.user)
        try:
            capitulo = Capitulos.objects.get(pk=capitulo_id)
            if visto:
                perfil.capitulos_vistos.add(capitulo)
            else:
                perfil.capitulos_vistos.remove(capitulo)
            return JsonResponse({'status': 'ok'})
        except Capitulos.DoesNotExist:
            return JsonResponse({'error': 'Capítulo no encontrado'}, status=404)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required
def marcar_masivo(request):
    if request.method == 'POST':
        libro_id = request.POST.get('libro_id')
        desde = int(request.POST.get('desde', 0))
        hasta = int(request.POST.get('hasta', 0))
        visto = request.POST.get('visto') == 'true'
        perfil, _ = Perfil.objects.get_or_create(usuario=request.user)
        
        capitulos_libro = Capitulos.objects.filter(libro_id=libro_id).order_by('id')
        # We use slice to get the range based on index
        capitulos_a_marcar = capitulos_libro[desde:hasta+1]
        
        if visto:
            perfil.capitulos_vistos.add(*capitulos_a_marcar)
        else:
            perfil.capitulos_vistos.remove(*capitulos_a_marcar)
            
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required
def lector(request, capitulo_id):
    try:
        capitulo = Capitulos.objects.get(pk=capitulo_id)
        # Mark as read automatically
        perfil, _ = Perfil.objects.get_or_create(usuario=request.user)
        perfil.capitulos_vistos.add(capitulo)

        # Usar cache si existe, si no, scrapear y guardar
        if capitulo.contenido:
            contenido_capitulo = capitulo.contenido
        else:
            libro = capitulo.libro
            extension_scrap = importlib.import_module(f'libros.services.{libro.extension.nombre}.scrap')
            contenido_capitulo = extension_scrap.scrap_capitulo(capitulo.enlace)
            if contenido_capitulo:
                capitulo.contenido = contenido_capitulo
                capitulo.save()

        # Navegación robusta buscando el ID siguiente/anterior real del mismo libro
        siguiente_cap = Capitulos.objects.filter(libro=capitulo.libro, id__gt=capitulo.id).order_by('id').first()
        anterior_cap = Capitulos.objects.filter(libro=capitulo.libro, id__lt=capitulo.id).order_by('-id').first()

        context = {
            'anterior': anterior_cap.id if anterior_cap else None,
            'siguiente': siguiente_cap.id if siguiente_cap else None,
            'capitulo': capitulo,
            'contenido': contenido_capitulo,
        }
        return render(request, "libros/lector.html", context)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    




@login_required

def buscador(request):
    return render(request, "libros/buscador.html" )




@csrf_exempt
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
        return JsonResponse({'error': f'Error de importación: {e}'}, status=500)
    except Exception as e:
        print(input_busqueda)
        print(f"Error al ejecutar la búsqueda para la extensión {nombre_extension}: {e}")
        return JsonResponse({'error': f'Error interno: {e}'}, status=500)









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
        # Obtenemos id, enlace y contenido para manejar el cacheo
        capitulos = Capitulos.objects.filter(libro=libro).values('id', 'enlace', 'contenido').order_by('id')
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

            print(f"Usando hasta {max_workers} hilos para descargar capítulos en paralelo.")

            resultados = [None] * total_caps
            completed = 0
            failed_count = 0

            def fetch_with_retries(cap_id, enlace, contenido_db, idx_local):
                # Si ya tenemos el contenido en la DB, lo devolvemos directamente
                if contenido_db and contenido_db.strip():
                    return contenido_db
            
                for attempt in range(1, max_retries + 1):
                    try:
                        contenido_local = extension_scrap.scrap_capitulo(enlace)
                        
                        if contenido_local:
                            # Guardamos en la base de datos para futuras descargas o para el lector
                            Capitulos.objects.filter(pk=cap_id).update(contenido=contenido_local)
                            return contenido_local
                        else:
                            print(f"[Cap {idx_local}] Contenido vacío en intento {attempt}.")
                    except Exception as e:
                        print(f"[Cap {idx_local}] Error en intento {attempt}: {e}")
                
                    time.sleep(retry_backoff_base + 0.5)
                
                return ""

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_idx = {}
                for idx, cap in enumerate(capitulos_list, start=1):
                    cap_id = cap.get('id')
                    enlace = cap.get('enlace')
                    contenido_db = cap.get('contenido')
                    
                    future = executor.submit(fetch_with_retries, cap_id, enlace, contenido_db, idx)
                    future_to_idx[future] = idx
                    
                    # Pequeño delay para no saturar el inicio de hilos
                    time.sleep(0.05)

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
                    
                    if completed % 10 == 0 or completed == total_caps:
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


@login_required
def get_progreso_descarga(request, libro_id):
    try:
        libro = Libro.objects.get(pk=libro_id)
        total = libro.capitulos.count()
        completados = libro.capitulos.filter(contenido__isnull=False).exclude(contenido='').count()
        
        return JsonResponse({
            'total': total,
            'completados': completados,
            'porcentaje': int((completados / total * 100)) if total > 0 else 0
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)








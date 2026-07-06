from django.urls import path
from . import views

app_name = 'carcanbooks'  # para usar namespace en templates o reverses

urlpatterns = [
    path('librerias/', views.librerias_menu, name='librerias_menu'),
    path('libro/id/<int:libro_id>/', views.libro_details, name='libro_details'),
    path('libro/url/<str:info_coded>/', views.libro_details, name='libro_details'),
    path('lector/<int:capitulo_id>/', views.lector, name='lector'),
    path('cambiar_libreria/', views.cambiar_libreria, name='cambiar_libreria'),
    path('buscador/', views.buscador, name='buscador'),
    path('busqueda/', views.busqueda, name='busqueda'),
    path('descarga_to_ebook/', views.descarga_to_ebook, name='descarga_to_ebook'),
    path('login/', views.login_view, name='login_view'),
    path('login_action/', views.login_action, name='login_action'),
    path('signup/', views.signup_view, name='signup_view'),
    path('signup_action/', views.signup_action, name='signup_action'),
    path('crear_libreria/', views.crear_libreria, name='crear_libreria'),
    path('crear_libro/', views.crear_libro, name='crear_libro'),
    path('borrar_libreria/', views.borrar_libreria, name='borrar_libreria'),
    path('carga_dinamica_librerias/', views.carga_dinamica_librerias, name='carga_dinamica_librerias'),
    path('marcar_visto/', views.marcar_visto, name='marcar_visto'),
    path('marcar_masivo/', views.marcar_masivo, name='marcar_masivo'),
    path('lastLibro/', views.lastLibro, name='lastLibro'),
    path('progreso_descarga/<int:libro_id>/', views.get_progreso_descarga, name='get_progreso_descarga'),


]

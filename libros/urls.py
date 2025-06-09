from django.urls import path
from . import views

app_name = 'carcanbooks'  # para usar namespace en templates o reverses

urlpatterns = [
    path('', views.librerias_menu, name='librerias_menu'),
    path('libro/id/<int:libro_id>/', views.libro_details, name='libro_details'),
    path('libro/url/<str:info_coded>/', views.libro_details, name='libro_details'),
    path('lector/<int:capitulo_id>/', views.lector, name='lector'),
    path('cambiar_libreria/', views.cambiar_libreria, name='cambiar_libreria'),
    path('cambio_status/', views.cambio_status, name='cambio_status'),
    path('buscador/', views.buscador, name='buscador'),
    path('busqueda/', views.busqueda, name='busqueda'),
    path('descarga_to_ebook/', views.descarga_to_ebook, name='descarga_to_ebook'),

]

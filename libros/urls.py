from django.urls import path
from . import views

app_name = 'carcanbooks'  # para usar namespace en templates o reverses

urlpatterns = [
    path('', views.librerias_menu, name='librerias_menu'),
    path('libro/', views.libro_details, name='libro_details'),
    path('libro/<int:libro_id>/', views.libro_details, name='libro_details'),
    path('lector/<int:capitulo_id>/', views.lector, name='lector'),
    path('cambiar_libreria/', views.cambiar_libreria, name='cambiar_libreria'),
    path('cambio_status/', views.cambio_status, name='cambio_status'),

]

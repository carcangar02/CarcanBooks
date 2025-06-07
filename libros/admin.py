from django.contrib import admin

# Register your models here.
from .models import Libreria, Libro, Extension, Capitulos
admin.site.register(Libro)
admin.site.register(Libreria)
admin.site.register(Extension)
admin.site.register(Capitulos)

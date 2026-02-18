from django.contrib.auth.models import User
from django.db import models





class Libreria(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='librerias', default=None)
    nombre = models.CharField(max_length=100, unique=True)
    libros = models.ManyToManyField('Libro', related_name='librerias', blank=True)

    def __str__(self):
        return self.nombre


class Extension(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    enlace = models.URLField(max_length=200, unique=True) 
    
    
    def __str__(self):
        return self.nombre

class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    foto = models.URLField(max_length=500, blank=True, null=True)
    enlace = models.URLField(max_length=200, unique=True)
    num_capitulos = models.IntegerField(default=0)
    extension = models.ForeignKey(Extension, on_delete=models.CASCADE, related_name='libros', default=None )
    
    def __str__(self):
        return self.titulo

class Capitulos(models.Model):
    # 1. Quitamos unique=True y AUMENTAMOS el max_length (200 es muy poco para URLs hoy en día)
    enlace = models.URLField(max_length=500) 
    
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='capitulos')
    titulo = models.CharField(max_length=200)
    visto = models.BooleanField(default=False)


    class Meta:

        unique_together = ('libro', 'enlace') 
        indexes = [
            models.Index(fields=['enlace']),
        ]

    def __str__(self):
        return self.titulo


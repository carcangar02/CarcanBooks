from django.db import models

# Create your models here.
class Libreria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    

    def __str__(self):
        return self.nombre


class Extension(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    enlace = models.URLField(max_length=200, unique=True) 
    
    
    def __str__(self):
        return self.nombre

class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    enlace = models.URLField(max_length=200, unique=True)
    libreria = models.ForeignKey(Libreria, on_delete=models.CASCADE, related_name='libros')
    extension = models.ForeignKey(Extension, on_delete=models.CASCADE, related_name='libros', default=None )
    
    def __str__(self):
        return self.titulo

class Capitulos(models.Model):
    enlace = models.URLField(max_length=200, unique=True)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='capitulos')
    titulo = models.CharField(max_length=200)
    visto = models.BooleanField(default=False)
    def __str__(self):
        return self.titulo
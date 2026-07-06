from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Libreria(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='librerias', default=None)
    nombre = models.CharField(max_length=100, unique=True)
    libros = models.ManyToManyField('Libro', related_name='librerias', blank=True)

    def __str__(self):
        return self.nombre

class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    capitulos_vistos = models.ManyToManyField('Capitulos', blank=True, related_name='visto_por')

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

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
    contenido = models.TextField(blank=True, null=True)


    class Meta:

        unique_together = ('libro', 'enlace') 
        indexes = [
            models.Index(fields=['enlace']),
        ]

    def __str__(self):
        return self.titulo


@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.get_or_create(usuario=instance)

@receiver(post_save, sender=User)
def guardar_perfil(sender, instance, **kwargs):
    if hasattr(instance, 'perfil'):
        instance.perfil.save()
    else:
        Perfil.objects.get_or_create(usuario=instance)

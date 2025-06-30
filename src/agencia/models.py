from django.db import models

# Create your models here.
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class TopicoPagina(models.Model):
    nombre = models.CharField(
        _('Nombre'),
        help_text=_('Nombre descriptivo'),
        max_length=50,
        unique=True
    )
    descripcion= models.CharField(
        _('Descripción'),
        help_text=_('Descripción del tópico de página'),
        max_length=150,
        blank=True
    )
    def __str__(self) -> str:
        return f'{self.nombre}'

    def delete(self, *args, **kwargs):
        if self.paginas.exists():
            raise ValidationError("No se puede eliminar un tópico con páginas asociadas.")
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['nombre']
        verbose_name = _('Tópico de Página')
        verbose_name_plural = _('Tópicos de Páginas')


class Categoria(models.Model):
    nombre = models.CharField(
        _('Nombre'),
        help_text=_('Nombre descriptivo'),
        max_length=50,
        unique=True
    )
    descripcion= models.CharField(
        _('Descripción'),
        help_text=_('Descripción de la categoría de anuncios'),
        max_length=150,
        blank=True
    )
    def __str__(self):
        return f'{self.nombre}'

    def delete(self, *args, **kwargs):
        if self.anuncios.exists():
            raise ValidationError("No se puede eliminar una categoría con anuncios asociados.")
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = _('Categoría')
        verbose_name_plural = _('Categorías')
        ordering = ['nombre']


class TipoAnuncio(models.Model):
    nombre = models.CharField(
        _('Nombre'),
        help_text=_('Nombre descriptivo'),
        max_length=50,
        unique=True
    )
    descripcion= models.CharField(
        _('Descripción'),
        help_text=_('Descripción del tipo de anuncios'),
        max_length=150,
        blank=True
    )
    def __str__(self):
        return f'{self.nombre}'

    def delete(self, *args, **kwargs):
        if self.anuncios.exists():
            raise ValidationError("No se puede eliminar un tipo de anuncio con anuncios asociados.")
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = _('Tipo de Anuncio')
        verbose_name_plural = _('Tipos de Anuncios')
        ordering = ['nombre']

class Campania(models.Model):

    nombre = models.CharField(
        _('Nombre'),
        max_length=50,
        help_text=_('Nombre de la campaña'),
        unique=True
    )
    

    fecha_inicio = models.DateTimeField(
        _('Fecha de Inicio'),
        help_text=_('Fecha y hora de inicio de campaña')
    )
    fecha_fin = models.DateTimeField(
        _('Fecha de Fin'),
        help_text=_('Fecha y hora de fin de campaña'),
        blank=True,
        null=True
    )
    def __str__(self):
        return self.nombre

    def delete(self, *args, **kwargs):
        if self.anuncios.exists():
            raise ValidationError("No se puede eliminar una campaña con anuncios asociados.")
        super().delete(*args, **kwargs)
    
    class Meta:
        verbose_name = _('Campaña')
        verbose_name_plural = _('Campañas')
        ordering=['nombre']
    def clean(self):
        if self.fecha_fin and self.fecha_fin <= self.fecha_inicio:
            raise ValidationError(_('La fecha de fin debe ser posterior a la fecha de inicio'))


class Anuncio(models.Model):
    nombre = models.CharField(
        _('Nombre'),
        max_length=100,
        help_text=_('Nombre del anuncio')
    )
    tipo = models.ForeignKey(
        TipoAnuncio,
        verbose_name=_('Tipo'),
        help_text=_('Tipo de anuncio'),
        related_name='anuncios',
        on_delete=models.PROTECT
    )
    titulo = models.CharField(
        _('Título'),
        max_length=100,
        help_text=_('Título del anuncio')
    )
    contenido = models.TextField(
        _('Contenido'),
        help_text=_('Contenido del anuncio')
    )
    campania=models.ForeignKey(
        Campania,
        verbose_name=_('Campaña'),
        help_text=_('Campaña donde aparece el anuncio'),
        related_name='anuncios',
        on_delete=models.PROTECT
    )
    categoria = models.ForeignKey(
        Categoria,
        verbose_name=_('Categoría'),
        help_text=_('Categoría del anuncio'),
        related_name='anuncios',
        on_delete=models.PROTECT
    )
    precio = models.FloatField(
        _('Precio'),
        help_text=_('Precio del anuncio')
    )

    def __str__(self):
        return f'{self.nombre} - {self.titulo}'

    def delete(self, *args, **kwargs):
      if self.apariciones.exists() or self.contrataciones.exists():
          raise ValidationError("No se puede eliminar un anuncio con apariciones o contrataciones asociadas.")
      super().delete(*args, **kwargs)

    class Meta:
        verbose_name = _('Anuncio')
        verbose_name_plural = _('Anuncios')
        ordering = ['nombre']

class PaginaWeb(models.Model):
    url = models.URLField(
        _('URL'),
        help_text=_('URL de la página web')
    )
    nombre = models.CharField(
        _('Nombre'),
        max_length=100,
        help_text=_('Nombre de la página web')
    )
    topico = models.ForeignKey(
        TopicoPagina,
        verbose_name=_('Tópico'),
        help_text=_('Tópico de la página web'),
        related_name='paginas',
        on_delete=models.PROTECT
    )
    def __str__(self):
        return self.nombre

    def delete(self, *args, **kwargs):
      if self.apariciones.exists():
          raise ValidationError("No se puede eliminar una página web con apariciones asociadas.")
      super().delete(*args, **kwargs)

    class Meta:
        verbose_name = _('Página Web')
        verbose_name_plural = _('Páginas Web')
        ordering = ['nombre']

class AparicionAnuncioPagina(models.Model):
    anuncio = models.ForeignKey(
        Anuncio,
        verbose_name=_('Anuncio'),
        help_text=_('Anuncio que aparece en la página'),
        related_name='apariciones',
        on_delete=models.PROTECT
    )
    pagina_web=models.ForeignKey(
        PaginaWeb,
        verbose_name='Página Web',
        help_text='Página web',
        related_name='apariciones',
        on_delete=models.PROTECT
    )
    fecha_inicio_aparicion = models.DateTimeField(
        _('Fecha de Inicio'),
        help_text=_('Fecha y hora de inicio de aparición')
    )
    fecha_fin_aparicion = models.DateTimeField(
        _('Fecha de Fin'),
        help_text=_('Fecha y hora de fin de aparición'),
        blank=True,
        null=True
    )

    def __str__(self):
        return f'{self.anuncio.nombre} en {self.pagina_web.nombre}'

    class Meta:
        verbose_name = _('Aparición de Anuncio en Página')
        verbose_name_plural = _('Apariciones de Anuncios en Páginas')
        ordering = ['-fecha_inicio_aparicion']

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.fecha_fin_aparicion and self.fecha_fin_aparicion <= self.fecha_inicio_aparicion:
            raise ValidationError(_('La fecha de fin debe ser posterior a la fecha de inicio'))

class Cliente(models.Model):
    nombre = models.CharField(
        _('Nombre'),
        max_length=50,
        help_text=_('Nombre del cliente')
    )
    apellido = models.CharField(
        _('Apellido'),
        max_length=50,
        help_text=_('Apellido del cliente')
    )
    direccion_postal = models.CharField(
        _('Dirección Postal'),
        max_length=100,
        blank=True,
        help_text=_('Dirección postal del cliente')
    )
    numero_telefono = models.CharField(
        _('Número de Teléfono'),
        max_length=30,
        blank=True,
        help_text=_('Número de teléfono del cliente')
    )
    correo = models.EmailField(
        _('Correo Electrónico'),
        max_length=100,
        blank=True,
        help_text=_('Correo electrónico del cliente')
    )

    def __str__(self):
        return f'{self.nombre} {self.apellido}'

    def delete(self, *args, **kwargs):
        if self.contrataciones.exists():
            raise ValidationError("No se puede eliminar un cliente con contrataciones asociadas.")
        super().delete(*args, **kwargs)
    
    class Meta:
        verbose_name = _('Cliente')
        verbose_name_plural = _('Clientes')
        ordering = ['apellido', 'nombre']


class ContratacionAnuncio(models.Model):
    fecha_contratacion = models.DateTimeField(
        _('Fecha de Contratación'),
        help_text=_('Fecha y hora de contratación del anuncio')
    )
    anuncio = models.ForeignKey(
        Anuncio,
        verbose_name=_('Anuncio'),
        help_text=_('Anuncio contratado'),
        related_name='contrataciones',
        on_delete=models.PROTECT
    )
    cliente= models.ForeignKey(
        Cliente,
        verbose_name=_('Cliente'),
        help_text=_('Cliente que contrata el anuncio'),
        related_name='contrataciones',
        on_delete=models.PROTECT
    )
    precio = models.FloatField(
        _('Precio'),
        help_text=_('Precio de la contratación')
    )

    def __str__(self):
        return f'{self.cliente} - {self.anuncio.nombre} ({self.fecha_contratacion})'

    class Meta:
        verbose_name = _('Contratación de Anuncio')
        verbose_name_plural = _('Contrataciones de Anuncios')
        ordering = ['-fecha_contratacion']
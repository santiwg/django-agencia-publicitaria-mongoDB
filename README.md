# Tutorial: Despliegue de una Aplicación Django con Docker y MongoDB
Práctico de Mapeo Objeto-Documental para la materia, Bases de Datos de la carrera `Ingeniería en Sistemas` de la *`Universidad Tecnológica Nacional`* *`Facultad Regional Villa María`*.

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Django 5.1.11](https://img.shields.io/badge/Django%205.1.11-092E20?style=for-the-badge&logo=django&logoColor=white)
![Alpine Linux](https://img.shields.io/badge/Alpine_Linux-0D597F?style=for-the-badge&logo=alpine-linux&logoColor=white)
![Python 3.13](https://img.shields.io/badge/Python%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white)

**Referencia Rápida**

**Mantenido Por:** Barrionuevo, Imanol; Broilo, Mateo Jose; Correa, Valentin; Díaz, Gabriel; Gambino, Tomás; Gomez Ferrero, Andres; Letona, Mateo; Wursten, Santiago

## **Descargo de Responsabilidad:**
El código proporcionado se ofrece "tal cual", sin garantía de ningún tipo, expresa o implícita. En ningún caso los autores o titulares de derechos de autor serán responsables de cualquier reclamo, daño u otra responsabilidad.

## Introducción
Este tutorial te guiará paso a paso en la creación y despliegue de una aplicación Django utilizando Docker y Docker Compose. El objetivo es que puedas levantar un entorno de desarrollo profesional, portable y fácil de mantener, ideal tanto para pruebas como para producción.

---

## Requisitos Previos
- **Docker** y **Docker Compose** instalados en tu sistema. Puedes consultar la [documentación oficial de Docker](https://docs.docker.com/get-docker/) para la instalación.
- Conocimientos básicos de Python y Django (no excluyente, el tutorial es autoexplicativo).

### Recursos Útiles
- [Tutorial oficial de Django](https://docs.djangoproject.com/en/2.0/intro/tutorial01/)
- [Cómo crear un entorno virtual en Python](https://docs.djangoproject.com/en/2.0/intro/contributing/)

---
## 1. Estructura del Proyecto
Crea una carpeta para tu proyecto. En este ejemplo, la llamaremos `agencia`.

> **Puedes copiar todo este bloque y pegarlo directamente en tu terminal o archivo correspondiente.**
```sh
mkdir agencia
cd agencia/
```
---
## 2. Definición de Dependencias
Crea un archivo requirements.txt para listar las dependencias de Python necesarias para tu aplicación.

Puedes copiar todo este bloque y pegarlo directamente en tu archivo requirements.txt.
```txt
# requirements.txt
Django
djongo
```
---
## 3. Creación del Dockerfile
El `Dockerfile` define la imagen de Docker que contendrá tu aplicación. Aquí se detallan las etapas de construcción, instalación de dependencias y configuración del entorno.

> **Puedes copiar todo este bloque y pegarlo directamente en tu archivo Dockerfile.**
```dockerfile
# Etapa de construcción
FROM python:3.10-alpine AS base
LABEL maintainer="Santiago Wursten Gill <santiwgwuri@gmail.com>, Imanol Barrionuevo <barrionuevoimanol@gmail.com>"
LABEL version="1.0"
LABEL description="cloudset"
RUN apk --no-cache add bash pango ttf-freefont py3-pip curl

# Etapa de construcción
FROM base AS builder
# Instalación de dependencias de construcción
RUN apk --no-cache add py3-pip py3-pillow py3-brotli py3-scipy py3-cffi \
  linux-headers autoconf automake libtool gcc cmake python3-dev \
  fortify-headers binutils libffi-dev wget openssl-dev libc-dev \
  g++ make musl-dev pkgconf libpng-dev openblas-dev build-base \
  font-noto terminus-font libffi

# Copia solo los archivos necesarios para instalar dependencias de Python
COPY ./requirements.txt .

# Instalación de dependencias de Python
RUN pip install --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt \
  && rm requirements.txt

# Etapa de producción
FROM base
RUN mkdir /code
WORKDIR /code
# Copia solo los archivos necesarios desde la etapa de construcción
COPY ./requirements.txt .
RUN pip install -r requirements.txt \
  && rm requirements.txt
COPY --chown=user:group --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
#COPY --from=build-python /usr/local/bin/ /usr/local/bin/
ENV PATH /usr/local/lib/python3.13/site-packages:$PATH
# Configuración adicional
RUN ln -s /usr/share/zoneinfo/America/Cordoba /etc/localtime

# Comando predeterminado
CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "app.wsgi"]

```

---
## 4. Configuración de Variables de Entorno
Crea un archivo `.env.db` para almacenar las variables de entorno necesarias para la conexión a la base de datos.

> **Puedes copiar todo este bloque y pegarlo directamente en tu archivo .env.db.**
```conf
# .env.db
# .env.db
DATABASE_ENGINE=djongo
MONGO_HOST=mongo
MONGO_PORT=27017
MONGO_DB=agencia_db
```

---
## 5. Definición de Servicios con Docker Compose
El archivo `docker-compose.yml` orquesta los servicios necesarios: base de datos, backend de Django y utilidades para generación y administración del proyecto.

> **Puedes copiar todo este bloque y pegarlo directamente en tu archivo docker-compose.yml.**
```yml
services:
  mongo:
    image: mongo:7.0
    container_name: mongo
    env_file:
      - .env.db
    ports:
      - 27017:27017
    volumes:
      - mongo-data:/data/db
    networks:
      - net

  mongo-express:
    image: mongo-express
    container_name: mongo-express
    ports:
      - 8081:8081
    environment:
      - ME_CONFIG_MONGODB_SERVER=mongo
      - ME_CONFIG_MONGODB_PORT=27017
    depends_on:
      - mongo
    networks:
      - net

  backend:
    build: .
    command: runserver 0.0.0.0:8000
    entrypoint: python3 manage.py
    env_file:
      - .env.db
    expose:
      - "8000"
    ports:
      - "8000:8000"
    volumes:
      - ./src:/code
    depends_on:
      - mongo
    networks:
      - net

  generate:
    build: .
    user: root
    command: /bin/sh -c 'mkdir -p src && django-admin startproject app src'
    env_file:
      - .env.db
    depends_on:
      - mongo
    volumes:
      - .:/code
    networks:
      - net

  manage:
    build: .
    entrypoint: python3 manage.py
    env_file:
      - .env.db
    volumes:
      - ./src:/code
    depends_on:
      - mongo
    networks:
      - net

networks:
  net:

volumes:
  mongo-data:
```

---
## 6. Generación y Configuración de la Aplicación

### Generar la estructura base del proyecto y la app

Hay que tener el archivo `LICENSE` para que la generación de a imagen no produzca un error.
> **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
```sh
docker compose run --rm generate
docker compose run --rm manage startapp agencia
sudo chown $USER:$USER -R .
```

### Configuración de `settings.py`
Edita el archivo `settings.py` para agregar tu app y configurar la base de datos usando las variables de entorno.

> **Puedes copiar todo este bloque y pegarlo al final directamente en tu archivo ./src/app/settings.py.**
```python
import os

ALLOWED_HOSTS = [os.environ.get("ALLOWED_HOSTS", "*")]

INSTALLED_APPS += [
    'agencia',  # tu app
]

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DATABASE_ENGINE", "djongo"),
        "NAME": os.environ.get("MONGO_DB", "agencia_db"),
        "ENFORCE_SCHEMA": False,  # evita errores si los modelos no coinciden 100% con la base
        "CLIENT": {
            "host": os.environ.get("MONGO_HOST", "mongo"),
            "port": int(os.environ.get("MONGO_PORT", 27017)),
        },
    }
}

```

---
## 7. Primeros Pasos con Django

### Migrar la base de datos
> **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
```sh
docker compose run --rm manage migrate
```

### Crear un superusuario
> **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
```sh
docker compose run --rm manage createsuperuser
```

### Iniciar la aplicación
> **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
```sh
docker compose up -d backend
```
Accede a la administración de Django en [http://localhost:8000/admin/](http://localhost:8000/admin/)

### Ver logs de los contenedores
> **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
```sh
docker compose logs -f
```

---
## 8. Comandos Útiles
- **Aplicar migraciones:**
  > **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
  ```sh
  docker compose run manage makemigrations
  docker compose run manage migrate
  ```
- **Detener y eliminar contenedores:**
  > **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
  ```sh
  docker compose down
  ```
- **Detener y eliminar contenedores con imagenes y contenedores sin uso:**
  > **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
  ```sh
  docker compose down -v --remove-orphans --rmi all
  ```
- **Limpiar recursos de Docker:**
  > **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
  ```sh
  docker system prune -a
  ```
- **Cambiar permisos de archivos:**
  > **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
  ```sh
  sudo chown $USER:$USER -R .
  ```

---
## 9. Modelado de la Aplicación

### Ejemplo de `models.py`
Incluye modelos bien documentados y estructurados para una gestión profesional de tus datos.

> **Puedes copiar todo este bloque y pegarlo directamente en tu archivo ./src/agencia/models.py.**
```python
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
        related_name='anuncios'
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
        related_name='anuncios'
    )
    categoria = models.ForeignKey(
        Categoria,
        verbose_name=_('Categoría'),
        help_text=_('Categoría del anuncio'),
        related_name='anuncios'
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
        related_name='paginas'
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
        related_name='apariciones'
    )
    pagina_web=models.ForeignKey(
        PaginaWeb,
        verbose_name='Página Web',
        help_text='Página web',
        related_name='apariciones'
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
        related_name='contrataciones'
    )
    cliente= models.ForeignKey(
        Cliente,
        verbose_name=_('Cliente'),
        help_text=_('Cliente que contrata el anuncio'),
        related_name='contrataciones'
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
```

---
## 10. Administración de la Aplicación

### Ejemplo de `admin.py`
Registra tus modelos para gestionarlos desde el panel de administración de Django.

> **Puedes copiar todo este bloque y pegarlo directamente en tu archivo ./src/agencia/admin.py.**
```python
from django.contrib import admin
from agencia.models import *

class AnuncioInline(admin.TabularInline):
    model=Anuncio
    extra=0

class ContratacionAnuncioInline(admin.TabularInline):
    model = ContratacionAnuncio
    extra = 0

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'correo', 'numero_telefono')
    list_filter = ('nombre', 'apellido')
    search_fields = ['nombre', 'apellido', 'correo']
    ordering = ['apellido', 'nombre']
    inlines=[ContratacionAnuncioInline]



@admin.register(TopicoPagina)
class TopicoAdmin(admin.ModelAdmin):
    list_display = ('nombre','descripcion')
    search_fields = ['nombre']


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre','descripcion')
    search_fields = ['nombre']


@admin.register(TipoAnuncio)
class TipoAnuncioAdmin(admin.ModelAdmin):
    list_display = ('nombre','descripcion')
    search_fields = ['nombre']


@admin.register(Campania)
class CampaniaAdmin(admin.ModelAdmin):
    list_display = ('nombre','fecha_inicio','fecha_fin')
    search_fields = ['nombre']
    date_hierarchy='fecha_inicio'
    ordering=['-fecha_inicio']
    inlines=[AnuncioInline]


class AparicionAnuncioPaginaInline(admin.TabularInline):
    model = AparicionAnuncioPagina
    extra = 0

@admin.register(PaginaWeb)
class PaginaWebAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'url', 'topico')
    list_filter = ('topico',)
    search_fields = ['nombre', 'url']
    ordering=['nombre']
    inlines=[AparicionAnuncioPaginaInline]



@admin.register(Anuncio)
class AnuncioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'titulo', 'tipo', 'categoria', 'precio_formateado', 'campania')
    list_filter = ('tipo', 'categoria', 'campania','precio_formateado')
    def precio_formateado(self, obj):
        return f"${round(obj.precio, 2):.2f}"
    precio_formateado.short_description = "Precio"
    search_fields = ['nombre', 'titulo', 'contenido','campania__nombre']
    ordering = ['nombre']
    inlines = [AparicionAnuncioPaginaInline]





@admin.register(ContratacionAnuncio)
class ContratacionAnuncioAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'anuncio', 'fecha_contratacion', 'precio_formateado')
    list_filter = ('fecha_contratacion', 'anuncio__campania')
    def precio_formateado(self, obj):
        return f"${round(obj.precio, 2):.2f}"
    precio_formateado.short_description = "Precio"
    search_fields = ['cliente__nombre', 'cliente__apellido', 'anuncio__nombre']
    date_hierarchy = 'fecha_contratacion'
    ordering = ['-fecha_contratacion']
    save_as=True


@admin.register(AparicionAnuncioPagina)
class AparicionAnuncioPaginaAdmin(admin.ModelAdmin):
    list_display = ('anuncio', 'pagina_web', 'fecha_inicio_aparicion', 'fecha_fin_aparicion')
    list_filter = ('pagina_web', 'fecha_inicio_aparicion')
    search_fields = ['anuncio__nombre', 'pagina_web__nombre']
    date_hierarchy = 'fecha_inicio_aparicion'
    ordering = ['-fecha_inicio_aparicion']
    save_as=True
```

---


## 11. Migraciones y Carga de Datos Iniciales

### Realizar migraciones de la app nueva.
> **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
```sh
docker compose run --rm manage makemigrations
docker compose run --rm manage migrate
```

Accede a la administración de Django en [http://localhost:8000/admin/](http://localhost:8000/admin/) donde ya se van a ver los cambios realizados en la app, pero todavía sin datos pre cargados.

### Crear y cargar fixtures (datos iniciales)
Crea la carpeta `./src/agencia/fixtures` dentro de tu app y agrega el archivo `initial_data.json` con los datos de ejemplo. Luego, carga los datos:
> **Puedes copiar todo este bloque y pegarlo directamente en tu archivo initial_data.json.**
```json
[
    {
        "model": "agencia.categoria",
        "pk": 1,
        "fields": {
            "nombre": "Tecnología",
            "descripcion": "Anuncios tech"
        }
    },
    {
        "model": "agencia.categoria",
        "pk": 2,
        "fields": {
            "nombre": "Salud",
            "descripcion": "Salud y Bienestar"
        }
    },
    {
        "model": "agencia.categoria",
        "pk": 3,
        "fields": {
            "nombre": "Deportes",
            "descripcion": "Anuncios deportivos"
        }
    },
    {
        "model": "agencia.categoria",
        "pk": 4,
        "fields": {
            "nombre": "Moda",
            "descripcion": "Indumentaria y moda"
        }
    },
    {
        "model": "agencia.categoria",
        "pk": 5,
        "fields": {
            "nombre": "Hogar",
            "descripcion": "Productos para el hogar"
        }
    },
    {
        "model": "agencia.tipoanuncio",
        "pk": 1,
        "fields": {
            "nombre": "Banner",
            "descripcion": "Anuncio Banner"
        }
    },
    {
        "model": "agencia.tipoanuncio",
        "pk": 2,
        "fields": {
            "nombre": "Pop-up",
            "descripcion": "Anuncio emergente"
        }
    },
    {
        "model": "agencia.tipoanuncio",
        "pk": 3,
        "fields": {
            "nombre": "Video",
            "descripcion": "Anuncio en video"
        }
    },
    {
        "model": "agencia.tipoanuncio",
        "pk": 4,
        "fields": {
            "nombre": "Texto",
            "descripcion": "Anuncio de texto"
        }
    },
    {
        "model": "agencia.tipoanuncio",
        "pk": 5,
        "fields": {
            "nombre": "Audio",
            "descripcion": "Anuncio sonoro"
        }
    },
    {
        "model": "agencia.topicopagina",
        "pk": 1,
        "fields": {
            "nombre": "Noticias",
            "descripcion": "Página de noticias"
        }
    },
    {
        "model": "agencia.topicopagina",
        "pk": 2,
        "fields": {
            "nombre": "Deportes",
            "descripcion": "Página deportiva"
        }
    },
    {
        "model": "agencia.topicopagina",
        "pk": 3,
        "fields": {
            "nombre": "Tecnología",
            "descripcion": "Tech y gadgets"
        }
    },
    {
        "model": "agencia.topicopagina",
        "pk": 4,
        "fields": {
            "nombre": "Hogar",
            "descripcion": "Consejos para el hogar"
        }
    },
    {
        "model": "agencia.topicopagina",
        "pk": 5,
        "fields": {
            "nombre": "Salud",
            "descripcion": "Bienestar y salud"
        }
    },
    {
        "model": "agencia.paginaweb",
        "pk": 1,
        "fields": {
            "nombre": "TechNews",
            "url": "https://technews.com",
            "topico": 3
        }
    },
    {
        "model": "agencia.paginaweb",
        "pk": 2,
        "fields": {
            "nombre": "DeportesYA",
            "url": "https://deportesya.com",
            "topico": 2
        }
    },
    {
        "model": "agencia.paginaweb",
        "pk": 3,
        "fields": {
            "nombre": "HogarPlus",
            "url": "https://hogarplus.com",
            "topico": 4
        }
    },
    {
        "model": "agencia.paginaweb",
        "pk": 4,
        "fields": {
            "nombre": "SaludActiva",
            "url": "https://saludactiva.com",
            "topico": 5
        }
    },
    {
        "model": "agencia.paginaweb",
        "pk": 5,
        "fields": {
            "nombre": "NoticiasHoy",
            "url": "https://noticiashoy.com",
            "topico": 1
        }
    },
    {
        "model": "agencia.campania",
        "pk": 1,
        "fields": {
            "nombre": "Black Friday",
            "fecha_inicio": "2025-11-20T00:00:00Z",
            "fecha_fin": "2025-11-30T23:59:59Z"
        }
    },
    {
        "model": "agencia.campania",
        "pk": 2,
        "fields": {
            "nombre": "Cyber Monday",
            "fecha_inicio": "2025-12-01T00:00:00Z",
            "fecha_fin": "2025-12-05T23:59:59Z"
        }
    },
    {
        "model": "agencia.campania",
        "pk": 3,
        "fields": {
            "nombre": "Hot Sale",
            "fecha_inicio": "2025-10-10T00:00:00Z",
            "fecha_fin": "2025-10-20T23:59:59Z"
        }
    },
    {
        "model": "agencia.campania",
        "pk": 4,
        "fields": {
            "nombre": "Navidad",
            "fecha_inicio": "2025-12-20T00:00:00Z",
            "fecha_fin": "2025-12-26T23:59:59Z"
        }
    },
    {
        "model": "agencia.campania",
        "pk": 5,
        "fields": {
            "nombre": "Año Nuevo",
            "fecha_inicio": "2025-12-31T00:00:00Z",
            "fecha_fin": "2026-01-01T23:59:59Z"
        }
    },
    {
        "model": "agencia.cliente",
        "pk": 1,
        "fields": {
            "nombre": "Juan",
            "apellido": "Pérez",
            "correo": "juan@gmail.com",
            "numero_telefono": "12345678"
        }
    },
    {
        "model": "agencia.cliente",
        "pk": 2,
        "fields": {
            "nombre": "María",
            "apellido": "Gómez",
            "correo": "maria@gmail.com",
            "numero_telefono": "23456789"
        }
    },
    {
        "model": "agencia.cliente",
        "pk": 3,
        "fields": {
            "nombre": "Luis",
            "apellido": "Martínez",
            "correo": "luis@gmail.com",
            "numero_telefono": "34567890"
        }
    },
    {
        "model": "agencia.cliente",
        "pk": 4,
        "fields": {
            "nombre": "Ana",
            "apellido": "Suárez",
            "correo": "ana@gmail.com",
            "numero_telefono": "45678901"
        }
    },
    {
        "model": "agencia.cliente",
        "pk": 5,
        "fields": {
            "nombre": "Carlos",
            "apellido": "López",
            "correo": "carlos@gmail.com",
            "numero_telefono": "56789012"
        }
    },
    {
        "model": "agencia.anuncio",
        "pk": 1,
        "fields": {
            "nombre": "Anuncio 1",
            "titulo": "Título 1",
            "tipo": 1,
            "categoria": 1,
            "precio": "1100.00",
            "contenido": "Contenido del anuncio 1",
            "campania": 1
        }
    },
    {
        "model": "agencia.anuncio",
        "pk": 2,
        "fields": {
            "nombre": "Anuncio 2",
            "titulo": "Título 2",
            "tipo": 2,
            "categoria": 2,
            "precio": "1200.00",
            "contenido": "Contenido del anuncio 2",
            "campania": 2
        }
    },
    {
        "model": "agencia.anuncio",
        "pk": 3,
        "fields": {
            "nombre": "Anuncio 3",
            "titulo": "Título 3",
            "tipo": 3,
            "categoria": 3,
            "precio": "1300.00",
            "contenido": "Contenido del anuncio 3",
            "campania": 3
        }
    },
    {
        "model": "agencia.anuncio",
        "pk": 4,
        "fields": {
            "nombre": "Anuncio 4",
            "titulo": "Título 4",
            "tipo": 4,
            "categoria": 4,
            "precio": "1400.00",
            "contenido": "Contenido del anuncio 4",
            "campania": 4
        }
    },
    {
        "model": "agencia.anuncio",
        "pk": 5,
        "fields": {
            "nombre": "Anuncio 5",
            "titulo": "Título 5",
            "tipo": 5,
            "categoria": 5,
            "precio": "1500.00",
            "contenido": "Contenido del anuncio 5",
            "campania": 5
        }
    },
    {
        "model": "agencia.aparicionanunciopagina",
        "pk": 1,
        "fields": {
            "anuncio": 1,
            "pagina_web": 1,
            "fecha_inicio_aparicion": "2025-06-29T12:00:00Z",
            "fecha_fin_aparicion": "2025-07-09T12:00:00Z"
        }
    },
    {
        "model": "agencia.aparicionanunciopagina",
        "pk": 2,
        "fields": {
            "anuncio": 2,
            "pagina_web": 2,
            "fecha_inicio_aparicion": "2025-06-30T12:00:00Z",
            "fecha_fin_aparicion": "2025-07-10T12:00:00Z"
        }
    },
    {
        "model": "agencia.aparicionanunciopagina",
        "pk": 3,
        "fields": {
            "anuncio": 3,
            "pagina_web": 3,
            "fecha_inicio_aparicion": "2025-07-01T12:00:00Z",
            "fecha_fin_aparicion": "2025-07-11T12:00:00Z"
        }
    },
    {
        "model": "agencia.aparicionanunciopagina",
        "pk": 4,
        "fields": {
            "anuncio": 4,
            "pagina_web": 4,
            "fecha_inicio_aparicion": "2025-07-02T12:00:00Z",
            "fecha_fin_aparicion": "2025-07-12T12:00:00Z"
        }
    },
    {
        "model": "agencia.aparicionanunciopagina",
        "pk": 5,
        "fields": {
            "anuncio": 5,
            "pagina_web": 5,
            "fecha_inicio_aparicion": "2025-07-03T12:00:00Z",
            "fecha_fin_aparicion": "2025-07-13T12:00:00Z"
        }
    },
    {
        "model": "agencia.contratacionanuncio",
        "pk": 1,
        "fields": {
            "cliente": 1,
            "anuncio": 1,
            "fecha_contratacion": "2025-06-29T12:00:00Z",
            "precio": "1650.00"
        }
    },
    {
        "model": "agencia.contratacionanuncio",
        "pk": 2,
        "fields": {
            "cliente": 2,
            "anuncio": 2,
            "fecha_contratacion": "2025-06-30T12:00:00Z",
            "precio": "1800.00"
        }
    },
    {
        "model": "agencia.contratacionanuncio",
        "pk": 3,
        "fields": {
            "cliente": 3,
            "anuncio": 3,
            "fecha_contratacion": "2025-07-01T12:00:00Z",
            "precio": "1950.00"
        }
    },
    {
        "model": "agencia.contratacionanuncio",
        "pk": 4,
        "fields": {
            "cliente": 4,
            "anuncio": 4,
            "fecha_contratacion": "2025-07-02T12:00:00Z",
            "precio": "2100.00"
        }
    },
    {
        "model": "agencia.contratacionanuncio",
        "pk": 5,
        "fields": {
            "cliente": 5,
            "anuncio": 5,
            "fecha_contratacion": "2025-07-03T12:00:00Z",
            "precio": "2250.00"
        }
    }
]
```
> **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
```sh
docker compose run --rm manage loaddata initial_data
```

---

## Conclusión
Con estos pasos, tendrás un entorno Django profesional, portable y listo para desarrollo o producción. Recuerda consultar la documentación oficial de Django y Docker para profundizar en cada tema. ¡Éxitos en tu proyecto!

---

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
    list_display = ['nombre']
    search_fields = ['nombre']
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
    list_filter = ('tipo', 'categoria', 'campania','precio')
    def precio_formateado(self, obj):
        return f"${round(obj.precio, 2):.2f}"
    precio_formateado.short_description = "Precio"
    search_fields = ['nombre', 'titulo', 'contenido','campania__nombre']
    ordering = ['nombre']
    inlines = [AparicionAnuncioPaginaInline]





@admin.register(ContratacionAnuncio)
class ContratacionAnuncioAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'anuncio', 'fecha_contratacion', 'precio_formateado')
    list_filter = ['anuncio__campania']
    def precio_formateado(self, obj):
        return f"${round(obj.precio, 2):.2f}"
    precio_formateado.short_description = "Precio"
    search_fields = ['cliente__nombre', 'cliente__apellido', 'anuncio__nombre']
    ordering = ['-fecha_contratacion']
    save_as=True


@admin.register(AparicionAnuncioPagina)
class AparicionAnuncioPaginaAdmin(admin.ModelAdmin):
    list_display = ('anuncio', 'pagina_web', 'fecha_inicio_aparicion', 'fecha_fin_aparicion')
    list_filter = ['pagina_web']
    search_fields = ['anuncio__nombre', 'pagina_web__nombre']
    ordering = ['-fecha_inicio_aparicion']
    save_as=True

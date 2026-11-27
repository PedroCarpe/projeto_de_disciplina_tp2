from django.contrib import admin

from .models import Ocorrencia


@admin.register(Ocorrencia)
class OcorrenciaAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'criada_em')
    list_filter = ('tipo', 'criada_em')
    search_fields = ('descricao',)

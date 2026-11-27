from django.contrib import admin

from .models import Ocorrencia


@admin.register(Ocorrencia)
class OcorrenciaAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'usuario', 'criada_em')
    list_select_related = ('usuario',)
    list_filter = ('tipo', 'criada_em')
    search_fields = ('descricao', 'usuario__username', 'usuario__email')

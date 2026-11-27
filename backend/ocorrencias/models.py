from django.conf import settings
from django.contrib.gis.db import models


class Ocorrencia(models.Model):
    class Tipo(models.TextChoices):
        BURACO = 'buraco', 'Buraco na via'
        CALCADA = 'calcada', 'Calçada danificada'
        ILUMINACAO = 'iluminacao', 'Iluminação pública'
        LIXO = 'lixo', 'Lixo ou entulho'
        SINALIZACAO = 'sinalizacao', 'Sinalização ou semáforo'
        ARVORE = 'arvore', 'Árvore (poda ou queda)'
        ESGOTO = 'esgoto', 'Esgoto ou vazamento'
        ALAGAMENTO = 'alagamento', 'Alagamento'
        VANDALISMO = 'vandalismo', 'Pichação ou vandalismo'
        FURTO = 'furto', 'Roubo ou furto'
        OUTROS = 'outros', 'Outros'

    tipo = models.CharField(max_length=30, choices=Tipo.choices)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='ocorrencias',
    )
    descricao = models.TextField(blank=True)
    localizacao = models.PointField(srid=4326, null=True, blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criada_em']
        verbose_name = 'ocorrência'
        verbose_name_plural = 'ocorrências'

    def __str__(self) -> str:
        return f'{self.get_tipo_display()} — {self.criada_em:%Y-%m-%d %H:%M}'

from decimal import Decimal

from django import forms
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.gis.geos import Point

from .models import Ocorrencia


class OcorrenciaForm(forms.Form):
    tipo = forms.ChoiceField(choices=Ocorrencia.Tipo.choices)
    descricao = forms.CharField(required=False, widget=forms.Textarea)
    latitude = forms.DecimalField(
        max_digits=9,
        decimal_places=6,
        min_value=Decimal("-90"),
        max_value=Decimal("90"),
    )
    longitude = forms.DecimalField(
        max_digits=9,
        decimal_places=6,
        min_value=Decimal("-180"),
        max_value=Decimal("180"),
    )

    def save(self, usuario: AbstractBaseUser) -> Ocorrencia:
        """Cria a ocorrência com as coordenadas informadas no formulário válido."""
        if not self.is_valid():
            raise ValueError("O formulário precisa ser válido para salvar.")

        dados = self.cleaned_data
        localizacao = Point(
            float(dados["longitude"]),
            float(dados["latitude"]),
            srid=4326,
        )
        return Ocorrencia.objects.create(
            usuario=usuario,
            tipo=dados["tipo"],
            descricao=dados["descricao"],
            localizacao=localizacao,
        )

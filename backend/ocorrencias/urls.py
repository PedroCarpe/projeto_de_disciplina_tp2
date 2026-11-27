from django.urls import path

from . import views

urlpatterns = [
    path(
        "ocorrencias/registrar/",
        views.registrar_ocorrencia_view,
        name="registrar_ocorrencia",
    ),
]

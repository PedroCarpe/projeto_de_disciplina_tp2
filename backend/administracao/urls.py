from django.urls import path

from . import views

app_name = "administracao"

urlpatterns = [
    path("", views.painel_view, name="painel"),
]

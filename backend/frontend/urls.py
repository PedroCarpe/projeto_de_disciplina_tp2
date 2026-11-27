from django.contrib.auth.views import LogoutView
from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.home_view, name="inicio"),
    path("mapa/", views.mapa_view, name="mapa"),
    path("sair/", LogoutView.as_view(next_page="inicio"), name="logout"),
    path("login/", views.login_view, name="login"),
    path("cadastro/", views.cadastro_view, name="cadastro"),
    path("", include("ocorrencias.urls")),
]

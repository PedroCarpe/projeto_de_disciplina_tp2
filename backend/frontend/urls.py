from django.contrib.auth.views import LogoutView
from django.urls import path

from usuarios import views as usuarios_views

from . import views

urlpatterns = [
    path("", views.home_view, name="inicio"),
    path("notificacoes/", usuarios_views.notificacoes_view, name="notificacoes"),
    path("mapa/", views.mapa_view, name="mapa"),
    path("sair/", LogoutView.as_view(next_page="inicio"), name="logout"),
    path("login/", views.login_view, name="login"),
    path("cadastro/", views.cadastro_view, name="cadastro"),
    path("estatisticas/", views.estatisticas_view, name="estatisticas"),
]

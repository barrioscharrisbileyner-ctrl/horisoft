from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

app_name = "usuarios"

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(
        template_name="usuarios/login.html",
        authentication_form=LoginForm,
        redirect_authenticated_user=True), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("inicio/", views.inicio, name="inicio"),
    path("perfil/", views.mi_perfil, name="perfil"),
    path("", views.lista_usuarios, name="lista"),
    path("nuevo/", views.crear_usuario, name="crear"),
    path("<int:pk>/editar/", views.editar_usuario, name="editar"),
]

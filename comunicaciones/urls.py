from django.urls import path

from .views import archivar_comunicado_view, crear_comunicado_view, lista_comunicados

app_name = 'comunicaciones'

urlpatterns = [
    path('', lista_comunicados, name='comunicados'),
    path('nuevo/', crear_comunicado_view, name='crear'),
    path('<int:pk>/archivar/', archivar_comunicado_view, name='archivar'),
]

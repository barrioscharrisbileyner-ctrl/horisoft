from django.urls import path

from .views import crear_documento_view, descargar_documento, eliminar_documento_view, lista_documentos

app_name = 'documental'

urlpatterns = [
    path('', lista_documentos, name='documentos'),
    path('nuevo/', crear_documento_view, name='crear'),
    path('<int:pk>/descargar/', descargar_documento, name='descargar'),
    path('<int:pk>/eliminar/', eliminar_documento_view, name='eliminar'),
]

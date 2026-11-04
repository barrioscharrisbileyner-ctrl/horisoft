from django.urls import path

from .views import crear_parametro_view, eliminar_parametro_view, lista_parametros, actualizar_parametro_view

app_name = 'configuracion'

urlpatterns = [
    path('', lista_parametros, name='parametros'),
    path('nuevo/', crear_parametro_view, name='crear'),
    path('<str:clave>/', actualizar_parametro_view, name='editar'),
    path('<str:clave>/eliminar/', eliminar_parametro_view, name='eliminar'),
]

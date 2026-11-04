from django.urls import path

from .views import (
    crear_vigilante_view,
    lista_vigilantes,
    lista_visitantes,
    registrar_ingreso_view,
    registrar_salida_view,
    lista_camaras,
    camara_crear,
    camara_editar,
    camara_eliminar,
    lista_vehiculos,
    vehiculo_crear,
    vehiculo_editar,
    vehiculo_eliminar,
)

app_name = 'seguridad'

urlpatterns = [
    path('vigilantes/', lista_vigilantes, name='vigilantes'),
    path('vigilantes/nuevo/', crear_vigilante_view, name='vigilante_crear'),
    path('visitantes/', lista_visitantes, name='visitantes'),
    path('visitantes/ingreso/', registrar_ingreso_view, name='ingreso'),
    path('visitantes/<int:pk>/salida/', registrar_salida_view, name='salida'),
    path('camaras/', lista_camaras, name='camaras'),
    path('camaras/nueva/', camara_crear, name='camara_crear'),
    path('camaras/<int:pk>/editar/', camara_editar, name='camara_editar'),
    path('camaras/<int:pk>/eliminar/', camara_eliminar, name='camara_eliminar'),
    path('vehiculos/', lista_vehiculos, name='vehiculos'),
    path('vehiculos/nuevo/', vehiculo_crear, name='vehiculo_crear'),
    path('vehiculos/<int:pk>/editar/', vehiculo_editar, name='vehiculo_editar'),
    path('vehiculos/<int:pk>/eliminar/', vehiculo_eliminar, name='vehiculo_eliminar'),
]

from django.urls import path

from .views import actualizar_estado_proveedor_view, crear_proveedor_view, lista_proveedores

app_name = 'proveedores'

urlpatterns = [
    path('', lista_proveedores, name='proveedores'),
    path('nuevo/', crear_proveedor_view, name='crear'),
    path('<int:pk>/estado/', actualizar_estado_proveedor_view, name='estado'),
]

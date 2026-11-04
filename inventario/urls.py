from django.urls import path

from .views import actualizar_cantidad_view, actualizar_estado_view, crear_item_view, lista_inventario

app_name = 'inventario'

urlpatterns = [
    path('', lista_inventario, name='inventario'),
    path('nuevo/', crear_item_view, name='crear'),
    path('<int:pk>/cantidad/', actualizar_cantidad_view, name='cantidad'),
    path('<int:pk>/estado/', actualizar_estado_view, name='estado'),
]

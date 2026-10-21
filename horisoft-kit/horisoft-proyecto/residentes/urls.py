from django.urls import path
from . import views

app_name = 'residentes'

urlpatterns = [
    path('', views.inicio, name='inicio'),

    # Personas (Residentes)
    path('personas/', views.lista_personas, name='personas'),
    path('personas/nueva/', views.crear_persona, name='persona_crear'),
    path('personas/<int:pk>/editar/', views.editar_persona, name='persona_editar'),
    path('personas/<int:pk>/eliminar/', views.eliminar_persona, name='persona_eliminar'),

    # Unidades Residenciales
    path('unidades/', views.lista_unidades, name='unidades'),
    path('unidades/nueva/', views.crear_unidad, name='unidad_crear'),
    path('unidades/<int:pk>/editar/', views.editar_unidad, name='unidad_editar'),
    path('unidades/<int:pk>/eliminar/', views.eliminar_unidad, name='unidad_eliminar'),

    # Residencias (asociación Persona <-> Unidad)
    path('residencias/', views.lista_residencias, name='residencias'),
    path('residencias/nueva/', views.crear_residencia, name='residencia_crear'),
    path('residencias/<int:pk>/editar/', views.editar_residencia, name='residencia_editar'),
    path('residencias/<int:pk>/eliminar/', views.eliminar_residencia, name='residencia_eliminar'),
]

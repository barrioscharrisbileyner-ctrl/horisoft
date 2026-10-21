from django.urls import path

from . import views

app_name = 'reservas'

urlpatterns = [
    # Reservas
    path('', views.lista_reservas, name='lista'),
    path('nueva/', views.crear_reserva, name='crear'),
    path('<int:pk>/editar/', views.editar_reserva, name='editar'),
    path('<int:pk>/estado/', views.cambiar_estado, name='estado'),
    path('<int:pk>/eliminar/', views.eliminar_reserva, name='eliminar'),

    # Zonas comunes
    path('zonas/', views.lista_zonas, name='zonas'),
    path('zonas/nueva/', views.crear_zona, name='zona_crear'),
    path('zonas/<int:pk>/editar/', views.editar_zona, name='zona_editar'),
    path('zonas/<int:pk>/eliminar/', views.eliminar_zona, name='zona_eliminar'),
]

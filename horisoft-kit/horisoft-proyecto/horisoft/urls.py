from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('residentes/', include('residentes.urls')),  # <-- delega a la app
    path('usuarios/', include('usuarios.urls')),      # autenticación y roles
    path('reservas/', include('reservas.urls')),      # zonas comunes y reservas
    path('', RedirectView.as_view(pattern_name='usuarios:inicio', permanent=False)),
]

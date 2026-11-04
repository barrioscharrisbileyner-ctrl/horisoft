from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api_v1.urls')),
    path('residentes/', include('residentes.urls')),  # <-- delega a la app
    path('usuarios/', include('usuarios.urls')),      # autenticación y roles
    path('reservas/', include('reservas.urls')),      # zonas comunes y reservas
    path('pqrs/', include('pqrs.urls')),              # PQRs
    path('financiera/', include('financiera.urls')),  # gestión financiera
    path('comunicaciones/', include('comunicaciones.urls')),  # comunicaciones internas
    path('documental/', include('documental.urls')),  # gestión documental
    path('seguridad/', include('seguridad.urls')),    # seguridad
    path('inventario/', include('inventario.urls')),  # inventario
    path('proveedores/', include('proveedores.urls')),  # proveedores
    path('configuracion/', include('configuracion.urls')),  # configuración general
    path('', RedirectView.as_view(pattern_name='usuarios:inicio', permanent=False)),
]

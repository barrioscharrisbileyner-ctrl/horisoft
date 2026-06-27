from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('residentes/', include('residentes.urls')),  # <-- delega a la app
    path('', RedirectView.as_view(url='residentes/', permanent=False)),
]

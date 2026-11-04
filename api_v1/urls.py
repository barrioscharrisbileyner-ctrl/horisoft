from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONOpenAPIRenderer
from rest_framework.schemas import get_schema_view

from .views import (
    AuthLoginView, AuthRefreshView, ComunicadoListView, HealthView,
    PqrListCreateView, ReservaCancelarView, ReservaDetailView,
    ReservaListCreateView, ResidentMeView, UserMeView, ZonaComunListView,
)

schema_view = get_schema_view(
    title='Horisoft API v1',
    description='Esquema OpenAPI de los endpoints de Horisoft.',
    version='1.0.0',
    public=True,
    permission_classes=[AllowAny],
    renderer_classes=[JSONOpenAPIRenderer],
)

urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),
    path('auth/login/', AuthLoginView.as_view(), name='auth-login'),
    path('auth/refresh/', AuthRefreshView.as_view(), name='auth-refresh'),
    path('auth/me/', UserMeView.as_view(), name='auth-me'),
    path('residentes/me/', ResidentMeView.as_view(), name='resident-me'),
    path('zonas-comunes/', ZonaComunListView.as_view(), name='zonas-comunes-list'),
    path('reservas/', ReservaListCreateView.as_view(), name='reservas-list-create'),
    path('reservas/<int:pk>/', ReservaDetailView.as_view(), name='reservas-detail'),
    path('reservas/<int:pk>/cancelar/', ReservaCancelarView.as_view(), name='reservas-cancel'),
    path('pqrs/', PqrListCreateView.as_view(), name='pqrs-list-create'),
    path('comunicados/', ComunicadoListView.as_view(), name='comunicados-list'),
    path('schema/', schema_view, name='api-schema'),
]

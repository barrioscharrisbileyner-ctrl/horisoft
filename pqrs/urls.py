from django.urls import path

from . import views

app_name = 'pqrs'

urlpatterns = [
    path('', views.lista_pqrs, name='lista'),
    path('nueva/', views.crear_pqr, name='crear'),
    path('<int:pk>/', views.detalle_pqr, name='detalle'),
    path('<int:pk>/responder/', views.responder_pqr_view, name='responder'),
]

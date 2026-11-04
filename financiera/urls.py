from django.urls import path

from . import views

app_name = 'financiera'

urlpatterns = [
    path('cuentas/', views.lista_cuentas, name='cuentas'),
    path('cuentas/nueva/', views.crear_cuenta_view, name='cuenta_crear'),
    path('cuentas/<int:pk>/vencer/', views.marcar_vencida_view, name='cuenta_vencer'),
    path('pagos/', views.lista_pagos, name='pagos'),
    path('pagos/nuevo/', views.registrar_pago_view, name='pago_crear'),
    path('multas/', views.lista_multas, name='multas'),
    path('multas/nueva/', views.multa_crear, name='multa_crear'),
    path('multas/<int:pk>/editar/', views.multa_editar, name='multa_editar'),
    path('multas/<int:pk>/eliminar/', views.multa_eliminar, name='multa_eliminar'),
    path('convenios/', views.lista_convenios, name='convenios'),
    path('convenios/nuevo/', views.convenio_crear, name='convenio_crear'),
    path('convenios/<int:pk>/editar/', views.convenio_editar, name='convenio_editar'),
    path('convenios/<int:pk>/eliminar/', views.convenio_eliminar, name='convenio_eliminar'),
]

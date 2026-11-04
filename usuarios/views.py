from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from comunicaciones.models import Comunicado
from financiera.models import CuentaCobro
from inventario.models import ItemInventario
from pqrs.models import Pqr
from reservas.models import Reserva
from residentes.access import propiedades_accesibles
from .decorators import rol_requerido
from .forms import EditarUsuarioForm, RegistroUsuarioForm
from .models import ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE, ROLES, PerfilUsuario
from .permisos import LECTURA_RESIDENTES, obtener_rol


def _perfiles_visibles(usuario):
    perfiles = PerfilUsuario.objects.select_related("user", "persona")
    if usuario.is_superuser:
        return perfiles
    propiedades = propiedades_accesibles(usuario)
    return perfiles.filter(
        Q(persona__propiedades__in=propiedades)
        | Q(user__accesos_propiedad__propiedad_horizontal__in=propiedades),
    ).distinct()


@rol_requerido(ROL_ADMINISTRADOR)
def lista_usuarios(request):
    perfiles = _perfiles_visibles(request.user)

    q = request.GET.get("q", "").strip()
    rol = request.GET.get("rol", "").strip()
    if q:
        perfiles = perfiles.filter(
            Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q)
            | Q(user__email__icontains=q))
    if rol:
        perfiles = perfiles.filter(rol=rol)

    pagina = Paginator(perfiles, 10).get_page(request.GET.get("page"))
    return render(request, "usuarios/lista.html", {
        "seccion": "usuarios", "pagina": pagina, "q": q, "rol_filtro": rol, "roles": ROLES})


@rol_requerido(ROL_ADMINISTRADOR)
def crear_usuario(request):
    form = RegistroUsuarioForm(request.POST or None, editor=request.user)
    if request.method == "POST" and form.is_valid():
        usuario = form.save()
        messages.success(request, f"Usuario {usuario.email} creado correctamente.")
        return redirect("usuarios:lista")
    return render(request, "usuarios/formulario.html", {
        "form": form, "titulo": "Nuevo usuario"})


@rol_requerido(ROL_ADMINISTRADOR)
def editar_usuario(request, pk):
    perfil = get_object_or_404(_perfiles_visibles(request.user), pk=pk)
    form = EditarUsuarioForm(request.POST or None, instance=perfil, editor=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Usuario actualizado correctamente.")
        return redirect("usuarios:lista")
    return render(request, "usuarios/formulario.html", {
        "form": form, "titulo": f"Editar a {perfil.user.get_full_name() or perfil.user.email}"})


@login_required
def mi_perfil(request):
    return render(request, "usuarios/perfil.html")


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def panel_administrativo(request):
    propiedades = propiedades_accesibles(request.user)
    inventario_bajo_minimo = ItemInventario.objects.filter(
        propiedad_horizontal__in=propiedades,
        cantidad__lte=F('cantidad_minima'),
    ).order_by('cantidad', 'nombre')
    contexto = {
        'cuentas_pendientes': CuentaCobro.objects.filter(
            residencia__unidad__propiedad_horizontal__in=propiedades,
            estado__in=[CuentaCobro.ESTADO_PENDIENTE, CuentaCobro.ESTADO_VENCIDA],
            valor_pagado__lt=F('valor'),
        ).count(),
        'pqrs_abiertas': Pqr.objects.filter(
            residencia__unidad__propiedad_horizontal__in=propiedades,
            estado__in=[Pqr.ESTADO_ABIERTA, Pqr.ESTADO_EN_PROCESO],
        ).count(),
        'reservas_hoy': Reserva.objects.filter(
            zona__propiedad_horizontal__in=propiedades,
            fecha=timezone.localdate(),
        ).exclude(estado=Reserva.ESTADO_CANCELADA).count(),
        'comunicados_recientes': Comunicado.objects.filter(
            propiedad_horizontal__in=propiedades,
            estado=Comunicado.ESTADO_PUBLICADO,
        ).order_by('-fecha_publicacion')[:5],
        'inventario_bajo_minimo': inventario_bajo_minimo,
    }
    return render(request, 'usuarios/panel.html', contexto)


@login_required
def inicio(request):
    """Punto de entrada tras el login: cada rol llega a su sección principal."""
    rol = obtener_rol(request.user)
    if rol in (ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO):
        return redirect("usuarios:panel")
    if rol in LECTURA_RESIDENTES:
        return redirect("residentes:inicio")
    if rol == ROL_RESIDENTE:
        return redirect("reservas:lista")
    return redirect("usuarios:perfil")

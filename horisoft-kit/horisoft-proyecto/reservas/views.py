"""
Vistas de Zonas Comunes y Reservas.

Mismo patrón del módulo Residentes (lista paginada de 10, crear/editar que
comparten plantilla, eliminar solo por POST), más control de acceso por rol:

  - Administrador / Administrativo: gestionan zonas y todas las reservas.
  - Residente: ve zonas y SUS reservas; reserva a nombre de sus residencias y
    puede cancelar las suyas.
  - Vigilante: solo consulta (zonas y reservas).
"""
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from usuarios.decorators import rol_requerido
from usuarios.models import ROL_ADMINISTRADOR, ROL_RESIDENTE
from usuarios.permisos import ESCRIBIR_RESERVAS, GESTION, USO_RESERVAS, obtener_rol

from .forms import ReservaForm, ZonaComunForm
from .models import Reserva, ZonaComun


def _reservas_visibles(usuario):
    """Todas las reservas, salvo para un Residente: solo las de sus residencias."""
    reservas = Reserva.objects.select_related('zona', 'residencia__persona', 'residencia__unidad')
    if obtener_rol(usuario) == ROL_RESIDENTE:
        perfil = getattr(usuario, 'perfil', None)
        persona = perfil.persona if perfil else None
        return reservas.filter(residencia__persona=persona) if persona else reservas.none()
    return reservas


# ----------------------------------------------------------------------
# ZONAS COMUNES
# ----------------------------------------------------------------------
@rol_requerido(*USO_RESERVAS)
def lista_zonas(request):
    pagina = Paginator(ZonaComun.objects.all(), 10).get_page(request.GET.get('page'))
    return render(request, 'reservas/zonas_lista.html', {
        'seccion': 'zonas', 'zonas': pagina,
        'puede_reservar': obtener_rol(request.user) in ESCRIBIR_RESERVAS,
    })


@rol_requerido(*GESTION)
def crear_zona(request):
    form = ZonaComunForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Zona común creada correctamente.')
        return redirect('reservas:zonas')
    return render(request, 'reservas/zona_form.html', {
        'seccion': 'zonas', 'form': form, 'titulo': 'Nueva zona común'})


@rol_requerido(*GESTION)
def editar_zona(request, pk):
    zona = get_object_or_404(ZonaComun, pk=pk)
    form = ZonaComunForm(request.POST or None, instance=zona)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Zona común actualizada correctamente.')
        return redirect('reservas:zonas')
    return render(request, 'reservas/zona_form.html', {
        'seccion': 'zonas', 'form': form, 'titulo': f'Editar zona: {zona.nombre}'})


@rol_requerido(*GESTION)
def eliminar_zona(request, pk):
    zona = get_object_or_404(ZonaComun, pk=pk)
    if request.method == 'POST':
        try:
            zona.delete()
            messages.success(request, f'Zona "{zona.nombre}" eliminada.')
        except ProtectedError:
            messages.error(
                request,
                f'No se puede eliminar "{zona.nombre}": tiene reservas. Márcala como Inactiva.')
    return redirect('reservas:zonas')


# ----------------------------------------------------------------------
# RESERVAS
# ----------------------------------------------------------------------
@rol_requerido(*USO_RESERVAS)
def lista_reservas(request):
    reservas = _reservas_visibles(request.user)

    estado = request.GET.get('estado', '').strip()
    zona = request.GET.get('zona', '').strip()
    if estado:
        reservas = reservas.filter(estado=estado)
    if zona.isdigit():
        reservas = reservas.filter(zona_id=int(zona))

    pagina = Paginator(reservas, 10).get_page(request.GET.get('page'))
    rol = obtener_rol(request.user)
    return render(request, 'reservas/reservas_lista.html', {
        'seccion': 'reservas', 'reservas': pagina,
        'estado_filtro': estado, 'zona_filtro': zona,
        'estados': Reserva.ESTADO_CHOICES, 'zonas': ZonaComun.objects.all(),
        'puede_reservar': rol in ESCRIBIR_RESERVAS,
        'puede_gestionar': rol in GESTION,
        'puede_eliminar': rol == ROL_ADMINISTRADOR,
    })


@rol_requerido(*ESCRIBIR_RESERVAS)
def crear_reserva(request):
    inicial = {'zona': request.GET.get('zona')} if request.method == 'GET' else None
    form = ReservaForm(request.POST or None, usuario=request.user, initial=inicial)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Reserva creada correctamente (queda Pendiente de confirmación).')
        return redirect('reservas:lista')

    # Un Residente sin residencia activa no puede reservar: se le explica por qué.
    sin_residencia = not form.fields['residencia'].queryset.exists()
    return render(request, 'reservas/reserva_form.html', {
        'seccion': 'reservas', 'form': form, 'titulo': 'Nueva reserva',
        'sin_residencia': sin_residencia})


@rol_requerido(*GESTION)
def editar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    form = ReservaForm(request.POST or None, instance=reserva, usuario=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Reserva actualizada correctamente.')
        return redirect('reservas:lista')
    return render(request, 'reservas/reserva_form.html', {
        'seccion': 'reservas', 'form': form, 'titulo': 'Editar reserva', 'sin_residencia': False})


@rol_requerido(*ESCRIBIR_RESERVAS)
@require_POST
def cambiar_estado(request, pk):
    # Para un Residente, _reservas_visibles solo incluye las suyas: una ajena da 404.
    reserva = get_object_or_404(_reservas_visibles(request.user), pk=pk)
    nuevo = request.POST.get('estado', '')

    if nuevo not in dict(Reserva.ESTADO_CHOICES):
        messages.error(request, 'Estado no válido.')
        return redirect('reservas:lista')
    # Un Residente solo puede cancelar; confirmar es del personal administrativo.
    if obtener_rol(request.user) == ROL_RESIDENTE and nuevo != Reserva.ESTADO_CANCELADA:
        raise PermissionDenied
    # Reactivar una reserva cancelada no debe crear un cruce de horario.
    if reserva.esta_cancelada and nuevo != Reserva.ESTADO_CANCELADA and Reserva.hay_cruce(
            reserva.zona, reserva.fecha, reserva.hora_inicio, reserva.hora_fin, excluir_pk=reserva.pk):
        messages.error(request, 'No se puede reactivar: ya existe otra reserva activa en ese horario.')
        return redirect('reservas:lista')

    reserva.estado = nuevo
    reserva.save(update_fields=['estado'])
    messages.success(request, f'La reserva quedó {nuevo.lower()}.')
    return redirect('reservas:lista')


@rol_requerido(ROL_ADMINISTRADOR)
def eliminar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    if request.method == 'POST':
        reserva.delete()
        messages.success(request, 'Reserva eliminada.')
    return redirect('reservas:lista')

from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.decorators import rol_requerido
from usuarios.models import ROL_ADMINISTRADOR, ROL_RESIDENTE, ROL_VIGILANTE
from usuarios.permisos import obtener_rol

from residentes.access import filtrar_por_propiedad
from .forms import PqrForm, PqrRespuestaForm
from .models import Pqr
from .services import responder_pqr, validar_pqr_data


@rol_requerido(ROL_ADMINISTRADOR, ROL_RESIDENTE, ROL_VIGILANTE)
def lista_pqrs(request):
    pqrs = filtrar_por_propiedad(
        Pqr.objects.select_related('residencia__persona', 'residencia__unidad'),
        request.user,
        'residencia__unidad__propiedad_horizontal',
    )
    if obtener_rol(request.user) == ROL_RESIDENTE:
        perfil = getattr(request.user, 'perfil', None)
        persona = perfil.persona if perfil else None
        pqrs = pqrs.filter(residencia__persona=persona) if persona else pqrs.none()
    pagina = Paginator(pqrs, 20).get_page(request.GET.get('page'))
    return render(request, 'pqrs/lista.html', {'pqrs': pagina, 'pagina': pagina})


@rol_requerido(ROL_ADMINISTRADOR, ROL_RESIDENTE)
def crear_pqr(request):
    form = PqrForm(request.POST or None, usuario=request.user)
    if request.method == 'POST' and form.is_valid():
        datos = form.cleaned_data
        try:
            validar_pqr_data(datos)
            pqr = form.save()
        except ValidationError as exc:
            form.add_error(None, str(exc))
        else:
            messages.success(request, 'PQR registrada correctamente.')
            return redirect('pqrs:lista')
    return render(request, 'pqrs/formulario.html', {'form': form, 'titulo': 'Nueva PQR'})


@rol_requerido(ROL_ADMINISTRADOR)
def responder_pqr_view(request, pk):
    pqr = get_object_or_404(
        filtrar_por_propiedad(
            Pqr.objects.all(), request.user,
            'residencia__unidad__propiedad_horizontal',
        ),
        pk=pk,
    )
    form = PqrRespuestaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            responder_pqr(pqr, form.cleaned_data['respuesta'], request.user)
        except (ValidationError, PermissionError) as exc:
            form.add_error(None, str(exc))
        else:
            messages.success(request, 'Respuesta registrada. La PQR quedó cerrada.')
            return redirect('pqrs:lista')
    return render(request, 'pqrs/responder.html', {'form': form, 'pqr': pqr})


@rol_requerido(ROL_ADMINISTRADOR, ROL_RESIDENTE, ROL_VIGILANTE)
def detalle_pqr(request, pk):
    pqr = get_object_or_404(
        filtrar_por_propiedad(
            Pqr.objects.all(), request.user,
            'residencia__unidad__propiedad_horizontal',
        ),
        pk=pk,
    )
    if obtener_rol(request.user) == ROL_RESIDENTE:
        perfil = getattr(request.user, 'perfil', None)
        persona = getattr(perfil, 'persona', None)
        if not persona or pqr.residencia.persona_id != persona.pk:
            raise PermissionDenied
    return render(request, 'pqrs/detalle.html', {
        'pqr': pqr,
        'es_admin': obtener_rol(request.user) == ROL_ADMINISTRADOR,
    })

from django.contrib import messages
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.decorators import rol_requerido
from usuarios.models import ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE
from usuarios.permisos import obtener_rol

from residentes.access import filtrar_por_propiedad
from .forms import ConvenioPagoForm, CuentaCobroForm, MultaForm, PagoForm
from .models import ConvenioPago, CuentaCobro, Multa, Pago
from .services import crear_cuenta, marcar_vencida, registrar_pago


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE)
def lista_cuentas(request):
    cuentas = filtrar_por_propiedad(
        CuentaCobro.objects.select_related('residencia__persona', 'residencia__unidad'),
        request.user,
        'residencia__unidad__propiedad_horizontal',
    )
    if obtener_rol(request.user) == ROL_RESIDENTE:
        persona = getattr(getattr(request.user, 'perfil', None), 'persona', None)
        cuentas = cuentas.filter(residencia__persona=persona) if persona else cuentas.none()
    pagina = Paginator(cuentas, 20).get_page(request.GET.get('page'))
    return render(request, 'financiera/cuentas_lista.html', {'cuentas': pagina, 'pagina': pagina})


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def crear_cuenta_view(request):
    form = CuentaCobroForm(request.POST or None, usuario=request.user)
    if request.method == 'POST' and form.is_valid():
        cuenta = crear_cuenta(form.cleaned_data, residencia=form.cleaned_data['residencia'])
        messages.success(request, f'Cuenta {cuenta.concepto} creada correctamente.')
        return redirect('financiera:cuentas')
    return render(request, 'financiera/cuenta_form.html', {'form': form, 'titulo': 'Nueva cuenta de cobro'})


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def marcar_vencida_view(request, pk):
    cuenta = get_object_or_404(
        filtrar_por_propiedad(
            CuentaCobro.objects.all(), request.user,
            'residencia__unidad__propiedad_horizontal',
        ),
        pk=pk,
    )
    if request.method == 'POST':
        try:
            marcar_vencida(cuenta)
            messages.success(request, 'Cuenta marcada como vencida.')
        except ValidationError as exc:
            messages.error(request, str(exc))
    return redirect('financiera:cuentas')


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE)
def lista_pagos(request):
    pagos = filtrar_por_propiedad(
        Pago.objects.select_related('cuenta__residencia__persona', 'cuenta__residencia__unidad'),
        request.user,
        'cuenta__residencia__unidad__propiedad_horizontal',
    )
    if obtener_rol(request.user) == ROL_RESIDENTE:
        persona = getattr(getattr(request.user, 'perfil', None), 'persona', None)
        pagos = pagos.filter(cuenta__residencia__persona=persona) if persona else pagos.none()
    pagina = Paginator(pagos, 20).get_page(request.GET.get('page'))
    return render(request, 'financiera/pagos_lista.html', {'pagos': pagina, 'pagina': pagina})


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def registrar_pago_view(request):
    form = PagoForm(request.POST or None, usuario=request.user)
    if request.method == 'POST' and form.is_valid():
        cuenta = form.cleaned_data['cuenta']
        try:
            pago = registrar_pago(cuenta, form.cleaned_data['valor_pagado'], form.cleaned_data['metodo_pago'])
            messages.success(request, f'Pago registrado por {pago.valor_pagado}.')
            return redirect('financiera:pagos')
        except ValidationError as exc:
            form.add_error(None, str(exc))
    return render(request, 'financiera/pago_form.html', {'form': form, 'titulo': 'Registrar pago'})


def _formulario_modelo(request, form_class, template, lista_url, titulo, instance=None):
    form = form_class(request.POST or None, instance=instance, usuario=request.user)
    if request.method == 'POST' and form.is_valid():
        objeto = form.save()
        messages.success(request, f'{titulo} guardado correctamente.')
        return redirect(lista_url)
    return render(request, template, {
        'form': form,
        'titulo': titulo,
        'cancel_url': lista_url,
    })


def _confirmar_eliminacion(request, objeto, etiqueta, lista_url):
    if request.method == 'POST':
        objeto.delete()
        messages.success(request, f'{etiqueta} eliminado correctamente.')
        return redirect(lista_url)
    return render(request, 'residentes/confirmar_eliminacion.html', {
        'objeto': objeto,
        'titulo': f'Eliminar {etiqueta.lower()}',
        'cancel_url': lista_url,
    })


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE)
def lista_multas(request):
    multas = filtrar_por_propiedad(
        Multa.objects.select_related('residencia__persona', 'residencia__unidad'),
        request.user,
        'residencia__unidad__propiedad_horizontal',
    )
    if obtener_rol(request.user) == ROL_RESIDENTE:
        persona = getattr(getattr(request.user, 'perfil', None), 'persona', None)
        multas = multas.filter(residencia__persona=persona) if persona else multas.none()
    pagina = Paginator(multas, 20).get_page(request.GET.get('page'))
    return render(request, 'financiera/multas_lista.html', {
        'multas': pagina,
        'pagina': pagina,
        'puede_gestionar': obtener_rol(request.user) in (ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO),
    })


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def multa_crear(request):
    return _formulario_modelo(request, MultaForm, 'residentes/crud_form.html', 'financiera:multas',
                              'Registrar multa')


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def multa_editar(request, pk):
    multa = get_object_or_404(
        filtrar_por_propiedad(
            Multa.objects.all(), request.user,
            'residencia__unidad__propiedad_horizontal',
        ),
        pk=pk,
    )
    return _formulario_modelo(request, MultaForm, 'residentes/crud_form.html', 'financiera:multas',
                              'Editar multa', multa)


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def multa_eliminar(request, pk):
    multa = get_object_or_404(
        filtrar_por_propiedad(
            Multa.objects.all(), request.user,
            'residencia__unidad__propiedad_horizontal',
        ),
        pk=pk,
    )
    return _confirmar_eliminacion(request, multa, 'Multa', 'financiera:multas')


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE)
def lista_convenios(request):
    convenios = filtrar_por_propiedad(
        ConvenioPago.objects.select_related('cuenta__residencia__persona', 'cuenta__residencia__unidad'),
        request.user,
        'cuenta__residencia__unidad__propiedad_horizontal',
    )
    if obtener_rol(request.user) == ROL_RESIDENTE:
        persona = getattr(getattr(request.user, 'perfil', None), 'persona', None)
        convenios = convenios.filter(cuenta__residencia__persona=persona) if persona else convenios.none()
    pagina = Paginator(convenios, 20).get_page(request.GET.get('page'))
    return render(request, 'financiera/convenios_lista.html', {
        'convenios': pagina,
        'pagina': pagina,
        'puede_gestionar': obtener_rol(request.user) in (ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO),
    })


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def convenio_crear(request):
    return _formulario_modelo(request, ConvenioPagoForm, 'residentes/crud_form.html',
                              'financiera:convenios', 'Crear convenio de pago')


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def convenio_editar(request, pk):
    convenio = get_object_or_404(
        filtrar_por_propiedad(
            ConvenioPago.objects.all(), request.user,
            'cuenta__residencia__unidad__propiedad_horizontal',
        ),
        pk=pk,
    )
    return _formulario_modelo(request, ConvenioPagoForm, 'residentes/crud_form.html',
                              'financiera:convenios', 'Editar convenio de pago', convenio)


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def convenio_eliminar(request, pk):
    convenio = get_object_or_404(
        filtrar_por_propiedad(
            ConvenioPago.objects.all(), request.user,
            'cuenta__residencia__unidad__propiedad_horizontal',
        ),
        pk=pk,
    )
    return _confirmar_eliminacion(request, convenio, 'Convenio de pago', 'financiera:convenios')

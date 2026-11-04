from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.decorators import rol_requerido
from usuarios.models import ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE, ROL_VIGILANTE
from usuarios.permisos import obtener_rol

from residentes.access import filtrar_por_propiedad
from .forms import CamaraForm, VehiculoForm, VigilanteForm, VisitanteForm
from .models import Camara, Vehiculo, Vigilante, Visitante
from .services import actualizar_estado_vigilante, crear_vigilante, registrar_ingreso, registrar_salida


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_VIGILANTE, ROL_RESIDENTE)
def lista_vigilantes(request):
    rol = obtener_rol(request.user)
    vigilantes = filtrar_por_propiedad(Vigilante.objects.all(), request.user)
    pagina = Paginator(vigilantes, 20).get_page(request.GET.get('page'))
    return render(request, 'seguridad/lista_vigilantes.html', {
        'vigilantes': pagina,
        'pagina': pagina,
        'rol': rol,
        'es_admin': rol in (ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO),
    })


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def crear_vigilante_view(request):
    form = VigilanteForm(request.POST or None, usuario=request.user)
    if request.method == 'POST' and form.is_valid():
        try:
            vigilante = crear_vigilante(
                nombre=form.cleaned_data['nombre'],
                documento=form.cleaned_data['documento'],
                propiedad_horizontal=form.cleaned_data['propiedad_horizontal'],
                telefono=form.cleaned_data['telefono'],
                turno=form.cleaned_data['turno'],
                estado=form.cleaned_data['estado'],
            )
            messages.success(request, f'Vigilante "{vigilante.nombre}" creado correctamente.')
            return redirect('seguridad:vigilantes')
        except ValueError as exc:
            form.add_error(None, str(exc))
    return render(request, 'seguridad/vigilante_form.html', {'form': form})


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_VIGILANTE, ROL_RESIDENTE)
def lista_visitantes(request):
    rol = obtener_rol(request.user)
    visitantes = filtrar_por_propiedad(
        Visitante.objects.select_related('residencia__persona', 'residencia__unidad', 'vigilante'),
        request.user,
        'residencia__unidad__propiedad_horizontal',
    )
    pagina = Paginator(visitantes, 20).get_page(request.GET.get('page'))
    return render(
        request,
        'seguridad/lista_visitantes.html',
        {
            'visitantes': pagina,
            'pagina': pagina,
            'rol': rol,
            'es_admin': rol in (ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO),
            'es_vigilante': rol == ROL_VIGILANTE,
        },
    )


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_VIGILANTE)
def registrar_ingreso_view(request):
    form = VisitanteForm(request.POST or None, usuario=request.user)
    if request.method == 'POST' and form.is_valid():
        try:
            visita = registrar_ingreso(
                nombre=form.cleaned_data['nombre'],
                documento=form.cleaned_data['documento'],
                residencia=form.cleaned_data['residencia'],
                vigilante=form.cleaned_data['vigilante'],
                motivo=form.cleaned_data['motivo'],
                placa_vehiculo=form.cleaned_data['placa_vehiculo'],
            )
            messages.success(request, f'Ingreso registrado para {visita.nombre}.')
            return redirect('seguridad:visitantes')
        except ValueError as exc:
            form.add_error(None, str(exc))
    return render(request, 'seguridad/ingreso_form.html', {'form': form})


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_VIGILANTE)
def registrar_salida_view(request, pk):
    visita = get_object_or_404(
        filtrar_por_propiedad(
            Visitante.objects.all(), request.user,
            'residencia__unidad__propiedad_horizontal',
        ),
        pk=pk,
    )
    if request.method == 'POST':
        try:
            registrar_salida(visita)
            messages.success(request, 'Salida registrada correctamente.')
        except ValueError as exc:
            messages.error(request, str(exc))
    return redirect('seguridad:visitantes')


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


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_VIGILANTE, ROL_RESIDENTE)
def lista_camaras(request):
    camaras = filtrar_por_propiedad(Camara.objects.select_related('zona'), request.user, 'zona__propiedad_horizontal')
    pagina = Paginator(camaras, 20).get_page(request.GET.get('page'))
    return render(request, 'seguridad/camaras_lista.html', {
        'camaras': pagina,
        'pagina': pagina,
        'puede_gestionar': obtener_rol(request.user) in (ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO),
    })


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def camara_crear(request):
    return _formulario_modelo(
        request, CamaraForm, 'residentes/crud_form.html', 'seguridad:camaras', 'Registrar cámara',
    )


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def camara_editar(request, pk):
    camara = get_object_or_404(
        filtrar_por_propiedad(Camara.objects.all(), request.user, 'zona__propiedad_horizontal'),
        pk=pk,
    )
    return _formulario_modelo(
        request, CamaraForm, 'residentes/crud_form.html', 'seguridad:camaras', 'Editar cámara', camara,
    )


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def camara_eliminar(request, pk):
    camara = get_object_or_404(
        filtrar_por_propiedad(Camara.objects.all(), request.user, 'zona__propiedad_horizontal'),
        pk=pk,
    )
    return _confirmar_eliminacion(request, camara, 'Cámara', 'seguridad:camaras')


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_VIGILANTE, ROL_RESIDENTE)
def lista_vehiculos(request):
    vehiculos = filtrar_por_propiedad(
        Vehiculo.objects.select_related('residencia__persona', 'residencia__unidad'),
        request.user,
        'residencia__unidad__propiedad_horizontal',
    )
    rol = obtener_rol(request.user)
    if rol == ROL_RESIDENTE:
        persona = getattr(getattr(request.user, 'perfil', None), 'persona', None)
        vehiculos = vehiculos.filter(residencia__persona=persona) if persona else vehiculos.none()
    pagina = Paginator(vehiculos, 20).get_page(request.GET.get('page'))
    return render(request, 'seguridad/vehiculos_lista.html', {
        'vehiculos': pagina,
        'pagina': pagina,
        'puede_gestionar': rol in (ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO),
        'es_residente': rol == ROL_RESIDENTE,
    })


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE)
def vehiculo_crear(request):
    return _formulario_modelo(
        request, VehiculoForm, 'residentes/crud_form.html', 'seguridad:vehiculos', 'Registrar vehículo',
    )


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def vehiculo_editar(request, pk):
    vehiculo = get_object_or_404(
        filtrar_por_propiedad(
            Vehiculo.objects.all(), request.user,
            'residencia__unidad__propiedad_horizontal',
        ),
        pk=pk,
    )
    return _formulario_modelo(
        request, VehiculoForm, 'residentes/crud_form.html', 'seguridad:vehiculos', 'Editar vehículo', vehiculo,
    )


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def vehiculo_eliminar(request, pk):
    vehiculo = get_object_or_404(
        filtrar_por_propiedad(
            Vehiculo.objects.all(), request.user,
            'residencia__unidad__propiedad_horizontal',
        ),
        pk=pk,
    )
    return _confirmar_eliminacion(request, vehiculo, 'Vehículo', 'seguridad:vehiculos')

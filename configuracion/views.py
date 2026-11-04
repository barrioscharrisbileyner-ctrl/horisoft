from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.decorators import rol_requerido
from usuarios.models import ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE, ROL_VIGILANTE
from usuarios.permisos import obtener_rol

from residentes.access import filtrar_por_propiedad
from .forms import ParametroConfiguracionForm, ParametroConfiguracionValorForm
from .models import ParametroConfiguracion
from .services import actualizar_valor_parametro, crear_parametro


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE, ROL_VIGILANTE)
def lista_parametros(request):
    rol = obtener_rol(request.user)
    parametros = filtrar_por_propiedad(ParametroConfiguracion.objects.all(), request.user)
    pagina = Paginator(parametros, 20).get_page(request.GET.get('page'))
    return render(request, 'configuracion/lista.html', {'parametros': pagina, 'pagina': pagina, 'rol': rol, 'es_admin': rol in (ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)})


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def crear_parametro_view(request):
    form = ParametroConfiguracionForm(request.POST or None, usuario=request.user)
    if request.method == 'POST' and form.is_valid():
        try:
            parametro = crear_parametro(
                clave=form.cleaned_data['clave'],
                valor=form.cleaned_data['valor'],
                propiedad_horizontal=form.cleaned_data['propiedad_horizontal'],
                descripcion=form.cleaned_data.get('descripcion', ''),
            )
            messages.success(request, f'Parámetro "{parametro.clave}" creado correctamente.')
            return redirect('configuracion:parametros')
        except ValueError as exc:
            form.add_error(None, str(exc))
    return render(request, 'configuracion/form.html', {'form': form})


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def actualizar_parametro_view(request, clave):
    parametro = get_object_or_404(
        filtrar_por_propiedad(ParametroConfiguracion.objects.all(), request.user),
        clave=clave,
    )
    form = ParametroConfiguracionValorForm(
        request.POST or None, instance=parametro, usuario=request.user,
    )
    if request.method == 'POST' and form.is_valid():
        try:
            actualizar_valor_parametro(
                parametro,
                form.cleaned_data['valor'],
                form.cleaned_data.get('descripcion', ''),
            )
            messages.success(request, 'Parámetro actualizado correctamente.')
            return redirect('configuracion:parametros')
        except ValueError as exc:
            form.add_error(None, str(exc))
    return render(request, 'configuracion/form.html', {'form': form})


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def eliminar_parametro_view(request, clave):
    parametro = get_object_or_404(
        filtrar_por_propiedad(ParametroConfiguracion.objects.all(), request.user),
        clave=clave,
    )
    if request.method == 'POST':
        parametro.delete()
        messages.success(request, 'Parámetro eliminado correctamente.')
    return redirect('configuracion:parametros')

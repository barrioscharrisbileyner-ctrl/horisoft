from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.decorators import rol_requerido
from usuarios.models import ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE, ROL_VIGILANTE
from usuarios.permisos import obtener_rol

from residentes.access import filtrar_por_propiedad
from .forms import ComunicadoForm
from .models import Comunicado
from .services import archivar_comunicado, crear_comunicado, listar_comunicados_para_usuario


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE, ROL_VIGILANTE)
def lista_comunicados(request):
    rol = obtener_rol(request.user)
    comunicados = listar_comunicados_para_usuario(request.user)
    pagina = Paginator(comunicados, 20).get_page(request.GET.get('page'))
    return render(
        request,
        'comunicaciones/lista.html',
        {
            'comunicados': pagina,
            'pagina': pagina,
            'rol': rol,
            'es_admin': rol in (ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO),
        },
    )


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def crear_comunicado_view(request):
    form = ComunicadoForm(request.POST or None, usuario=request.user)
    if request.method == 'POST' and form.is_valid():
        try:
            comunicado = crear_comunicado(
                titulo=form.cleaned_data['titulo'],
                contenido=form.cleaned_data['contenido'],
                dirigido_a=form.cleaned_data['dirigido_a'],
                autor=request.user,
                propiedad_horizontal=form.cleaned_data['propiedad_horizontal'],
            )
            messages.success(request, f'Comunicado "{comunicado.titulo}" creado correctamente.')
            return redirect('comunicaciones:comunicados')
        except ValueError as exc:
            form.add_error(None, str(exc))
    return render(request, 'comunicaciones/form.html', {'form': form})


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def archivar_comunicado_view(request, pk):
    comunicado = get_object_or_404(
        filtrar_por_propiedad(Comunicado.objects.all(), request.user), pk=pk,
    )
    if request.method == 'POST':
        try:
            archivar_comunicado(comunicado)
            messages.success(request, 'Comunicado archivado correctamente.')
        except ValueError as exc:
            messages.error(request, str(exc))
    return redirect('comunicaciones:comunicados')

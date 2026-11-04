from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.decorators import rol_requerido
from usuarios.models import ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_PROVEEDOR, ROL_RESIDENTE
from usuarios.permisos import obtener_rol

from residentes.access import filtrar_por_propiedad
from .forms import ProveedorEstadoForm, ProveedorForm
from .models import Proveedor
from .services import actualizar_estado_proveedor, crear_proveedor


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_PROVEEDOR, ROL_RESIDENTE)
def lista_proveedores(request):
    rol = obtener_rol(request.user)
    proveedores = filtrar_por_propiedad(Proveedor.objects.all(), request.user)
    pagina = Paginator(proveedores, 20).get_page(request.GET.get('page'))
    return render(request, 'proveedores/lista.html', {'proveedores': pagina, 'pagina': pagina, 'rol': rol, 'es_admin': rol in (ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)})


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def crear_proveedor_view(request):
    form = ProveedorForm(request.POST or None, usuario=request.user)
    if request.method == 'POST' and form.is_valid():
        try:
            proveedor = crear_proveedor(
                nombre=form.cleaned_data['nombre'],
                nit=form.cleaned_data['nit'],
                servicio=form.cleaned_data['servicio'],
                propiedad_horizontal=form.cleaned_data['propiedad_horizontal'],
                telefono=form.cleaned_data['telefono'],
                estado=form.cleaned_data['estado'],
            )
            messages.success(request, f'Proveedor "{proveedor.nombre}" creado correctamente.')
            return redirect('proveedores:proveedores')
        except ValueError as exc:
            form.add_error(None, str(exc))
    return render(request, 'proveedores/form.html', {'form': form})


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def actualizar_estado_proveedor_view(request, pk):
    proveedor = get_object_or_404(
        filtrar_por_propiedad(Proveedor.objects.all(), request.user), pk=pk,
    )
    form = ProveedorEstadoForm(request.POST or None, instance=proveedor)
    if request.method == 'POST':
        if form.is_valid():
            try:
                actualizar_estado_proveedor(proveedor, form.cleaned_data['estado'])
                messages.success(request, 'Estado actualizado correctamente.')
                return redirect('proveedores:proveedores')
            except ValueError as exc:
                form.add_error(None, str(exc))
    return render(request, 'proveedores/form.html', {'form': form})

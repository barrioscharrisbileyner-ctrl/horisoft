from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.decorators import rol_requerido
from usuarios.models import ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_VIGILANTE, ROL_RESIDENTE
from usuarios.permisos import obtener_rol

from residentes.access import filtrar_por_propiedad
from .forms import ItemInventarioForm
from .models import ItemInventario
from .services import actualizar_cantidad, actualizar_estado, crear_item


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_VIGILANTE, ROL_RESIDENTE)
def lista_inventario(request):
    rol = obtener_rol(request.user)
    items = filtrar_por_propiedad(ItemInventario.objects.all(), request.user)
    pagina = Paginator(items, 20).get_page(request.GET.get('page'))
    return render(request, 'inventario/lista.html', {'items': pagina, 'pagina': pagina, 'rol': rol, 'es_admin': rol in (ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)})


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def crear_item_view(request):
    form = ItemInventarioForm(request.POST or None, usuario=request.user)
    if request.method == 'POST' and form.is_valid():
        try:
            item = crear_item(
                nombre=form.cleaned_data['nombre'],
                categoria=form.cleaned_data['categoria'],
                cantidad=form.cleaned_data['cantidad'],
                cantidad_minima=form.cleaned_data['cantidad_minima'],
                propiedad_horizontal=form.cleaned_data['propiedad_horizontal'],
                ubicacion=form.cleaned_data['ubicacion'],
                estado=form.cleaned_data['estado'],
            )
            messages.success(request, f'Ítem "{item.nombre}" creado correctamente.')
            return redirect('inventario:inventario')
        except ValueError as exc:
            form.add_error(None, str(exc))
    return render(request, 'inventario/form.html', {'form': form})


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def actualizar_cantidad_view(request, pk):
    item = get_object_or_404(
        filtrar_por_propiedad(ItemInventario.objects.all(), request.user), pk=pk,
    )
    if request.method == 'POST':
        cantidad = request.POST.get('cantidad')
        try:
            actualizar_cantidad(item, cantidad)
            messages.success(request, 'Cantidad actualizada.')
        except ValueError as exc:
            messages.error(request, str(exc))
    return redirect('inventario:inventario')


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def actualizar_estado_view(request, pk):
    item = get_object_or_404(
        filtrar_por_propiedad(ItemInventario.objects.all(), request.user), pk=pk,
    )
    if request.method == 'POST':
        estado = request.POST.get('estado')
        try:
            actualizar_estado(item, estado)
            messages.success(request, 'Estado actualizado.')
        except ValueError as exc:
            messages.error(request, str(exc))
    return redirect('inventario:inventario')

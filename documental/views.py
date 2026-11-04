from django.contrib import messages
from django.core.paginator import Paginator
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.decorators import rol_requerido
from usuarios.models import ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE, ROL_VIGILANTE
from usuarios.permisos import obtener_rol

from residentes.access import filtrar_por_propiedad
from .forms import DocumentoForm
from .models import Documento
from .services import crear_documento


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE, ROL_VIGILANTE)
def lista_documentos(request):
    rol = obtener_rol(request.user)
    documentos = filtrar_por_propiedad(Documento.objects.all(), request.user)
    pagina = Paginator(documentos, 20).get_page(request.GET.get('page'))
    return render(request, 'documental/lista.html', {'documentos': pagina, 'pagina': pagina, 'rol': rol, 'es_admin': rol in (ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)})


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def crear_documento_view(request):
    form = DocumentoForm(request.POST or None, request.FILES or None, usuario=request.user)
    if request.method == 'POST' and form.is_valid():
        try:
            documento = crear_documento(
                titulo=form.cleaned_data['titulo'],
                tipo=form.cleaned_data['tipo'],
                responsable=request.user,
                propiedad_horizontal=form.cleaned_data['propiedad_horizontal'],
                url_archivo=form.cleaned_data['url_archivo'],
                descripcion=form.cleaned_data.get('descripcion', ''),
                archivo=form.cleaned_data.get('archivo'),
            )
            messages.success(request, f'Documento "{documento.titulo}" creado correctamente.')
            return redirect('documental:documentos')
        except ValueError as exc:
            form.add_error(None, str(exc))
    return render(request, 'documental/form.html', {'form': form})


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO)
def eliminar_documento_view(request, pk):
    documento = get_object_or_404(
        filtrar_por_propiedad(Documento.objects.all(), request.user), pk=pk,
    )
    if request.method == 'POST':
        if documento.archivo:
            documento.archivo.delete(save=False)
        documento.delete()
        messages.success(request, 'Documento eliminado correctamente.')
    return redirect('documental:documentos')


@rol_requerido(ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE, ROL_VIGILANTE)
def descargar_documento(request, pk):
    documento = get_object_or_404(
        filtrar_por_propiedad(Documento.objects.all(), request.user), pk=pk,
    )
    if not documento.archivo:
        raise Http404('Este documento no tiene un archivo cargado.')
    try:
        archivo = documento.archivo.open('rb')
    except FileNotFoundError as exc:
        raise Http404('El archivo del documento no está disponible.') from exc
    response = FileResponse(archivo, as_attachment=True, filename=f'documento-{documento.pk}.pdf')
    response['X-Content-Type-Options'] = 'nosniff'
    return response

"""
Vistas del módulo Residentes y Unidades.

Mismo patrón de la guía TallerExpress:
- una vista 'lista_*' (GET, con paginación de 10 por página)
- una vista 'crear_*' / 'editar_*' que comparten plantilla de formulario
  y distinguen GET (mostrar) de POST (guardar)
- una vista 'eliminar_*' que solo borra si la petición es POST
  (la confirmación visual la hace el JS de la plantilla con confirm()).
"""
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import ProtectedError
from django.shortcuts import render, redirect, get_object_or_404

from usuarios.decorators import rol_requerido
from usuarios.permisos import GESTION, LECTURA_RESIDENTES

from .access import filtrar_por_propiedad, propiedades_accesibles
from .models import Persona, UnidadResidencial, Residencia, PropiedadHorizontal
from .forms import PersonaForm, UnidadResidencialForm, ResidenciaForm


@rol_requerido(*LECTURA_RESIDENTES)
def inicio(request):
    """Pequeño índice del módulo con accesos a las 3 secciones."""
    contexto = {
        'total_personas': Persona.objects.filter(
            propiedades__in=propiedades_accesibles(request.user),
        ).distinct().count(),
        'total_unidades': filtrar_por_propiedad(
            UnidadResidencial.objects.all(), request.user,
        ).count(),
        'total_residencias': filtrar_por_propiedad(
            Residencia.objects.filter(activo=True), request.user, 'unidad__propiedad_horizontal',
        ).count(),
    }
    return render(request, 'residentes/inicio.html', contexto)


# ----------------------------------------------------------------------
# PERSONAS (Residentes)
# ----------------------------------------------------------------------
@rol_requerido(*LECTURA_RESIDENTES)
def lista_personas(request):
    qs = Persona.objects.filter(propiedades__in=propiedades_accesibles(request.user)).distinct()
    paginator = Paginator(qs, 10)
    personas = paginator.get_page(request.GET.get('page'))
    return render(request, 'residentes/personas_lista.html', {'personas': personas})


@rol_requerido(*GESTION)
def crear_persona(request):
    if request.method == 'POST':
        form = PersonaForm(request.POST, usuario=request.user)
        if form.is_valid():
            form.save()
            return redirect('residentes:personas')
    else:
        form = PersonaForm(usuario=request.user)
    return render(request, 'residentes/persona_form.html', {'form': form, 'titulo': 'Nuevo residente'})


@rol_requerido(*GESTION)
def editar_persona(request, pk):
    persona = get_object_or_404(
        Persona.objects.filter(propiedades__in=propiedades_accesibles(request.user)).distinct(),
        pk=pk,
    )
    if request.method == 'POST':
        form = PersonaForm(request.POST, instance=persona, usuario=request.user)
        if form.is_valid():
            form.save()
            return redirect('residentes:personas')
    else:
        form = PersonaForm(instance=persona, usuario=request.user)
    return render(request, 'residentes/persona_form.html', {'form': form, 'titulo': f'Editar residente: {persona.nombre}'})


@rol_requerido(*GESTION)
def eliminar_persona(request, pk):
    personas = Persona.objects.filter(
        propiedades__in=propiedades_accesibles(request.user),
    ).distinct()
    if not request.user.is_superuser:
        personas = personas.exclude(
            propiedades__in=PropiedadHorizontal.objects.exclude(
                pk__in=propiedades_accesibles(request.user),
            ),
        ).distinct()
    persona = get_object_or_404(
        personas,
        pk=pk,
    )
    if request.method == 'POST':
        try:
            persona.delete()
        except ProtectedError:
            messages.error(request, f'No se puede eliminar a {persona.nombre}: tiene reservas asociadas.')
    return redirect('residentes:personas')


# ----------------------------------------------------------------------
# UNIDADES RESIDENCIALES
# ----------------------------------------------------------------------
@rol_requerido(*LECTURA_RESIDENTES)
def lista_unidades(request):
    qs = filtrar_por_propiedad(
        UnidadResidencial.objects.select_related('propiedad_horizontal'),
        request.user,
    )
    paginator = Paginator(qs, 10)
    unidades = paginator.get_page(request.GET.get('page'))
    return render(request, 'residentes/unidades_lista.html', {'unidades': unidades})


@rol_requerido(*GESTION)
def crear_unidad(request):
    if request.method == 'POST':
        form = UnidadResidencialForm(request.POST, usuario=request.user)
        if form.is_valid():
            form.save()
            return redirect('residentes:unidades')
    else:
        form = UnidadResidencialForm(usuario=request.user)
    return render(request, 'residentes/unidad_form.html', {'form': form, 'titulo': 'Nueva unidad'})


@rol_requerido(*GESTION)
def editar_unidad(request, pk):
    unidad = get_object_or_404(
        filtrar_por_propiedad(UnidadResidencial.objects.all(), request.user),
        pk=pk,
    )
    if request.method == 'POST':
        form = UnidadResidencialForm(request.POST, instance=unidad, usuario=request.user)
        if form.is_valid():
            form.save()
            return redirect('residentes:unidades')
    else:
        form = UnidadResidencialForm(instance=unidad, usuario=request.user)
    return render(request, 'residentes/unidad_form.html', {'form': form, 'titulo': f'Editar unidad: {unidad.numero_unidad}'})


@rol_requerido(*GESTION)
def eliminar_unidad(request, pk):
    unidad = get_object_or_404(
        filtrar_por_propiedad(UnidadResidencial.objects.all(), request.user),
        pk=pk,
    )
    if request.method == 'POST':
        try:
            unidad.delete()
        except ProtectedError:
            messages.error(request, f'No se puede eliminar la unidad {unidad.numero_unidad}: tiene reservas asociadas.')
    return redirect('residentes:unidades')


# ----------------------------------------------------------------------
# RESIDENCIAS (asociar Persona <-> Unidad)
# ----------------------------------------------------------------------
@rol_requerido(*LECTURA_RESIDENTES)
def lista_residencias(request):
    qs = filtrar_por_propiedad(
        Residencia.objects.select_related('persona', 'unidad'),
        request.user,
        'unidad__propiedad_horizontal',
    )
    paginator = Paginator(qs, 10)
    residencias = paginator.get_page(request.GET.get('page'))
    return render(request, 'residentes/residencias_lista.html', {'residencias': residencias})


@rol_requerido(*GESTION)
def crear_residencia(request):
    if request.method == 'POST':
        form = ResidenciaForm(request.POST, usuario=request.user)
        if form.is_valid():
            form.save()
            return redirect('residentes:residencias')
    else:
        form = ResidenciaForm(usuario=request.user)
    return render(request, 'residentes/residencia_form.html', {'form': form, 'titulo': 'Asociar residente a unidad'})


@rol_requerido(*GESTION)
def editar_residencia(request, pk):
    residencia = get_object_or_404(
        filtrar_por_propiedad(Residencia.objects.all(), request.user, 'unidad__propiedad_horizontal'),
        pk=pk,
    )
    if request.method == 'POST':
        form = ResidenciaForm(request.POST, instance=residencia, usuario=request.user)
        if form.is_valid():
            form.save()
            return redirect('residentes:residencias')
    else:
        form = ResidenciaForm(instance=residencia, usuario=request.user)
    return render(request, 'residentes/residencia_form.html', {'form': form, 'titulo': 'Editar residencia'})


@rol_requerido(*GESTION)
def eliminar_residencia(request, pk):
    residencia = get_object_or_404(
        filtrar_por_propiedad(Residencia.objects.all(), request.user, 'unidad__propiedad_horizontal'),
        pk=pk,
    )
    if request.method == 'POST':
        try:
            residencia.delete()
        except ProtectedError:
            messages.error(request, 'No se puede eliminar la residencia: tiene reservas asociadas. Márcala como inactiva.')
    return redirect('residentes:residencias')

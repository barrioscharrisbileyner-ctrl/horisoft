"""
Vistas del módulo Residentes y Unidades.

Mismo patrón de la guía TallerExpress:
- una vista 'lista_*' (GET, con paginación de 10 por página)
- una vista 'crear_*' / 'editar_*' que comparten plantilla de formulario
  y distinguen GET (mostrar) de POST (guardar)
- una vista 'eliminar_*' que solo borra si la petición es POST
  (la confirmación visual la hace el JS de la plantilla con confirm()).
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator

from .models import Persona, UnidadResidencial, Residencia, PropiedadHorizontal
from .forms import PersonaForm, UnidadResidencialForm, ResidenciaForm


def obtener_ph_default():
    """Esta instancia de Horisoft administra una sola copropiedad. Si todavía
    no existe el registro, lo crea la primera vez que se necesita."""
    ph, _ = PropiedadHorizontal.objects.get_or_create(
        id_ph=1,
        defaults={'nombre': 'Conjunto Residencial Horisoft', 'nit': ''},
    )
    return ph


def inicio(request):
    """Pequeño índice del módulo con accesos a las 3 secciones."""
    contexto = {
        'total_personas': Persona.objects.count(),
        'total_unidades': UnidadResidencial.objects.count(),
        'total_residencias': Residencia.objects.filter(activo=True).count(),
    }
    return render(request, 'residentes/inicio.html', contexto)


# ----------------------------------------------------------------------
# PERSONAS (Residentes)
# ----------------------------------------------------------------------
def lista_personas(request):
    qs = Persona.objects.all()
    paginator = Paginator(qs, 10)
    personas = paginator.get_page(request.GET.get('page'))
    return render(request, 'residentes/personas_lista.html', {'personas': personas})


def crear_persona(request):
    if request.method == 'POST':
        form = PersonaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('residentes:personas')
    else:
        form = PersonaForm()
    return render(request, 'residentes/persona_form.html', {'form': form, 'titulo': 'Nuevo residente'})


def editar_persona(request, pk):
    persona = get_object_or_404(Persona, pk=pk)
    if request.method == 'POST':
        form = PersonaForm(request.POST, instance=persona)
        if form.is_valid():
            form.save()
            return redirect('residentes:personas')
    else:
        form = PersonaForm(instance=persona)
    return render(request, 'residentes/persona_form.html', {'form': form, 'titulo': f'Editar residente: {persona.nombre}'})


def eliminar_persona(request, pk):
    persona = get_object_or_404(Persona, pk=pk)
    if request.method == 'POST':
        persona.delete()
    return redirect('residentes:personas')


# ----------------------------------------------------------------------
# UNIDADES RESIDENCIALES
# ----------------------------------------------------------------------
def lista_unidades(request):
    qs = UnidadResidencial.objects.select_related('propiedad_horizontal')
    paginator = Paginator(qs, 10)
    unidades = paginator.get_page(request.GET.get('page'))
    return render(request, 'residentes/unidades_lista.html', {'unidades': unidades})


def crear_unidad(request):
    if request.method == 'POST':
        form = UnidadResidencialForm(request.POST)
        if form.is_valid():
            unidad = form.save(commit=False)
            unidad.propiedad_horizontal = obtener_ph_default()
            unidad.save()
            return redirect('residentes:unidades')
    else:
        form = UnidadResidencialForm()
    return render(request, 'residentes/unidad_form.html', {'form': form, 'titulo': 'Nueva unidad'})


def editar_unidad(request, pk):
    unidad = get_object_or_404(UnidadResidencial, pk=pk)
    if request.method == 'POST':
        form = UnidadResidencialForm(request.POST, instance=unidad)
        if form.is_valid():
            form.save()
            return redirect('residentes:unidades')
    else:
        form = UnidadResidencialForm(instance=unidad)
    return render(request, 'residentes/unidad_form.html', {'form': form, 'titulo': f'Editar unidad: {unidad.numero_unidad}'})


def eliminar_unidad(request, pk):
    unidad = get_object_or_404(UnidadResidencial, pk=pk)
    if request.method == 'POST':
        unidad.delete()
    return redirect('residentes:unidades')


# ----------------------------------------------------------------------
# RESIDENCIAS (asociar Persona <-> Unidad)
# ----------------------------------------------------------------------
def lista_residencias(request):
    qs = Residencia.objects.select_related('persona', 'unidad')
    paginator = Paginator(qs, 10)
    residencias = paginator.get_page(request.GET.get('page'))
    return render(request, 'residentes/residencias_lista.html', {'residencias': residencias})


def crear_residencia(request):
    if request.method == 'POST':
        form = ResidenciaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('residentes:residencias')
    else:
        form = ResidenciaForm()
    return render(request, 'residentes/residencia_form.html', {'form': form, 'titulo': 'Asociar residente a unidad'})


def editar_residencia(request, pk):
    residencia = get_object_or_404(Residencia, pk=pk)
    if request.method == 'POST':
        form = ResidenciaForm(request.POST, instance=residencia)
        if form.is_valid():
            form.save()
            return redirect('residentes:residencias')
    else:
        form = ResidenciaForm(instance=residencia)
    return render(request, 'residentes/residencia_form.html', {'form': form, 'titulo': 'Editar residencia'})


def eliminar_residencia(request, pk):
    residencia = get_object_or_404(Residencia, pk=pk)
    if request.method == 'POST':
        residencia.delete()
    return redirect('residentes:residencias')

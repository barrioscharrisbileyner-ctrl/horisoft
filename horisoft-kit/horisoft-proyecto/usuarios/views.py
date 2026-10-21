from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .decorators import rol_requerido
from .forms import EditarUsuarioForm, RegistroUsuarioForm
from .models import ROL_ADMINISTRADOR, ROL_RESIDENTE, ROLES, PerfilUsuario
from .permisos import LECTURA_RESIDENTES, obtener_rol


@rol_requerido(ROL_ADMINISTRADOR)
def lista_usuarios(request):
    perfiles = PerfilUsuario.objects.select_related("user", "persona")

    q = request.GET.get("q", "").strip()
    rol = request.GET.get("rol", "").strip()
    if q:
        perfiles = perfiles.filter(
            Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q)
            | Q(user__email__icontains=q))
    if rol:
        perfiles = perfiles.filter(rol=rol)

    pagina = Paginator(perfiles, 10).get_page(request.GET.get("page"))
    return render(request, "usuarios/lista.html", {
        "seccion": "usuarios", "pagina": pagina, "q": q, "rol_filtro": rol, "roles": ROLES})


@rol_requerido(ROL_ADMINISTRADOR)
def crear_usuario(request):
    form = RegistroUsuarioForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario = form.save()
        messages.success(request, f"Usuario {usuario.email} creado correctamente.")
        return redirect("usuarios:lista")
    return render(request, "usuarios/formulario.html", {
        "form": form, "titulo": "Nuevo usuario"})


@rol_requerido(ROL_ADMINISTRADOR)
def editar_usuario(request, pk):
    perfil = get_object_or_404(PerfilUsuario.objects.select_related("user"), pk=pk)
    form = EditarUsuarioForm(request.POST or None, instance=perfil, editor=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Usuario actualizado correctamente.")
        return redirect("usuarios:lista")
    return render(request, "usuarios/formulario.html", {
        "form": form, "titulo": f"Editar a {perfil.user.get_full_name() or perfil.user.email}"})


@login_required
def mi_perfil(request):
    return render(request, "usuarios/perfil.html")


@login_required
def inicio(request):
    """Punto de entrada tras el login: cada rol llega a su sección principal."""
    rol = obtener_rol(request.user)
    if rol in LECTURA_RESIDENTES:
        return redirect("residentes:inicio")
    if rol == ROL_RESIDENTE:
        return redirect("reservas:lista")
    return redirect("usuarios:perfil")

from django import forms
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

from residentes.access import propiedades_accesibles
from residentes.models import AccesoPropiedad, PropiedadHorizontal
from .models import PERSONA_MODEL, ROL_ADMINISTRADOR, ROL_RESIDENTE, ROLES, PerfilUsuario

User = get_user_model()

MSG_RESIDENTE_SIN_PERSONA = "Un residente debe estar vinculado a una persona registrada."


def _personas_libres(incluir=None, usuario=None):
    """Personas que aún no tienen usuario (más la indicada, al editar)."""
    Persona = apps.get_model(PERSONA_MODEL)
    propiedades = propiedades_accesibles(usuario) if usuario is not None else \
        PropiedadHorizontal.objects.all()
    libres = Persona.objects.filter(
        perfil_usuario__isnull=True,
        propiedades__in=propiedades,
    ).distinct()
    if incluir is not None:
        libres = Persona.objects.filter(
            pk=incluir.pk,
            propiedades__in=propiedades,
        ) | libres
    return libres.distinct()


class LoginForm(AuthenticationForm):
    """Login con correo electrónico (el correo se guarda como username)."""

    error_messages = {
        "invalid_login": "Correo o contraseña incorrectos.",
        "inactive": "Esta cuenta está inactiva. Comunícate con el administrador.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Correo electrónico"
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "autofocus": True, "autocomplete": "username"})
        self.fields["password"].label = "Contraseña"
        self.fields["password"].widget.attrs.update({"class": "form-control"})

    def clean_username(self):
        return self.cleaned_data["username"].strip().lower()


class RegistroUsuarioForm(forms.Form):
    """Alta de un usuario (solo la usa el Administrador)."""

    nombre = forms.CharField(max_length=150)
    apellido = forms.CharField(max_length=150, required=False)
    correo = forms.EmailField(label="Correo electrónico")
    rol = forms.ChoiceField(choices=ROLES)
    persona = forms.ModelChoiceField(
        queryset=None, required=False,
        help_text="Obligatoria para los residentes. Solo aparecen personas sin usuario.")
    propiedades = forms.ModelMultipleChoiceField(
        queryset=PropiedadHorizontal.objects.none(),
        required=False,
        label="Copropiedades autorizadas",
    )
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput)

    def __init__(self, *args, editor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.editor = editor
        propiedades = propiedades_accesibles(editor) if editor is not None else \
            PropiedadHorizontal.objects.all()
        self.fields["persona"].queryset = _personas_libres(usuario=editor)
        self.fields["propiedades"].queryset = propiedades
        for campo in self.fields.values():
            clase = "form-select" if isinstance(campo, (forms.ChoiceField, forms.ModelChoiceField)) else "form-control"
            campo.widget.attrs.setdefault("class", clase)

    def clean_correo(self):
        correo = self.cleaned_data["correo"].strip().lower()
        if User.objects.filter(username__iexact=correo).exists() or \
                User.objects.filter(email__iexact=correo).exists():
            raise ValidationError("Ya existe un usuario registrado con ese correo.")
        return correo

    def clean(self):
        datos = super().clean()
        p1, p2 = datos.get("password1"), datos.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Las contraseñas no coinciden.")
        elif p1:
            try:
                validate_password(p1)
            except ValidationError as error:
                self.add_error("password1", error)
        if datos.get("rol") == ROL_RESIDENTE and not datos.get("persona"):
            self.add_error("persona", MSG_RESIDENTE_SIN_PERSONA)
        if datos.get("rol") != ROL_RESIDENTE and not datos.get("propiedades"):
            disponibles = list(self.fields["propiedades"].queryset[:2])
            if len(disponibles) == 1:
                datos["propiedades"] = disponibles
            else:
                self.add_error("propiedades", "Selecciona al menos una copropiedad autorizada.")
        return datos

    @transaction.atomic
    def save(self):
        d = self.cleaned_data
        user = User.objects.create_user(
            username=d["correo"], email=d["correo"], password=d["password1"],
            first_name=d["nombre"], last_name=d.get("apellido", ""))
        PerfilUsuario.objects.create(user=user, rol=d["rol"], persona=d.get("persona"))
        if d["rol"] != ROL_RESIDENTE:
            AccesoPropiedad.objects.bulk_create([
                AccesoPropiedad(usuario=user, propiedad_horizontal=propiedad)
                for propiedad in d["propiedades"]
            ])
        return user


class EditarUsuarioForm(forms.ModelForm):
    """Cambia rol, persona vinculada y estado (activo/inactivo) de un usuario."""

    is_active = forms.BooleanField(label="Cuenta activa", required=False)
    propiedades = forms.ModelMultipleChoiceField(
        queryset=PropiedadHorizontal.objects.none(),
        required=False,
        label="Copropiedades autorizadas",
    )

    class Meta:
        model = PerfilUsuario
        fields = ["rol", "persona"]

    def __init__(self, *args, editor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.editor = editor  # quien edita (para impedir que se auto-bloquee)
        self.fields["is_active"].initial = self.instance.user.is_active
        propiedades_editor = propiedades_accesibles(editor) if editor is not None else \
            PropiedadHorizontal.objects.all()
        self.fields["propiedades"].queryset = propiedades_editor
        self.fields["propiedades"].initial = propiedades_editor.filter(
            pk__in=propiedades_accesibles(self.instance.user),
        )
        self.fields["persona"].queryset = _personas_libres(
            incluir=self.instance.persona, usuario=editor,
        )
        self.fields["persona"].required = False
        for nombre, campo in self.fields.items():
            if nombre == "is_active":
                campo.widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(campo, (forms.ChoiceField, forms.ModelChoiceField)):
                campo.widget.attrs.setdefault("class", "form-select")

    def clean(self):
        datos = super().clean()
        if datos.get("rol") == ROL_RESIDENTE and not datos.get("persona"):
            self.add_error("persona", MSG_RESIDENTE_SIN_PERSONA)
        if datos.get("rol") != ROL_RESIDENTE and not datos.get("propiedades"):
            disponibles = list(self.fields["propiedades"].queryset[:2])
            if len(disponibles) == 1:
                datos["propiedades"] = disponibles
            else:
                self.add_error("propiedades", "Selecciona al menos una copropiedad autorizada.")
        # Un administrador no puede quitarse a sí mismo el acceso.
        if self.editor is not None and self.instance.user_id == self.editor.pk:
            if not datos.get("is_active"):
                self.add_error("is_active", "No puedes desactivar tu propia cuenta.")
            if datos.get("rol") != ROL_ADMINISTRADOR:
                self.add_error("rol", "No puedes quitarte el rol de Administrador a ti mismo.")
        return datos

    @transaction.atomic
    def save(self, commit=True):
        perfil = super().save(commit=commit)
        perfil.user.is_active = self.cleaned_data["is_active"]
        perfil.user.save(update_fields=["is_active"])
        if self.editor is not None:
            propiedades_editor = propiedades_accesibles(self.editor)
            if self.cleaned_data["rol"] == ROL_RESIDENTE:
                AccesoPropiedad.objects.filter(usuario=perfil.user).delete()
            else:
                AccesoPropiedad.objects.filter(
                    usuario=perfil.user,
                    propiedad_horizontal__in=propiedades_editor,
                ).delete()
                AccesoPropiedad.objects.bulk_create([
                    AccesoPropiedad(usuario=perfil.user, propiedad_horizontal=propiedad)
                    for propiedad in self.cleaned_data["propiedades"]
                ])
        return perfil

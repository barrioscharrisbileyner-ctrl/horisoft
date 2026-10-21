from getpass import getpass

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from usuarios.models import ROL_ADMINISTRADOR, PerfilUsuario


class Command(BaseCommand):
    help = "Crea el primer usuario Administrador (con perfil y rol) para poder entrar al sistema."

    def add_arguments(self, parser):
        parser.add_argument("--correo", required=True)
        parser.add_argument("--nombre", default="Administrador")
        parser.add_argument("--password", help="Si se omite, se pide por consola.")

    def handle(self, *args, **opciones):
        User = get_user_model()
        correo = opciones["correo"].strip().lower()
        if User.objects.filter(username__iexact=correo).exists():
            raise CommandError(f"Ya existe un usuario con el correo {correo}.")

        password = opciones["password"] or getpass("Contraseña: ")
        try:
            validate_password(password)
        except ValidationError as error:
            raise CommandError("; ".join(error.messages))

        user = User.objects.create_user(
            username=correo, email=correo, password=password,
            first_name=opciones["nombre"], is_staff=True)
        PerfilUsuario.objects.create(user=user, rol=ROL_ADMINISTRADOR)
        self.stdout.write(self.style.SUCCESS(f"Administrador {correo} creado."))

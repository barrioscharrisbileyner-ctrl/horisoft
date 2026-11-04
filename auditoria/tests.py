from django.test import TestCase
from django.urls import reverse

from usuarios.models import ROL_ADMINISTRADOR
from usuarios.testing import crear_usuario_con_rol

from .models import AuditEvent


class AuditMiddlewareTests(TestCase):
    def setUp(self):
        self.admin = crear_usuario_con_rol('admin-auditoria@horisoft.com', ROL_ADMINISTRADOR)

    def test_write_request_is_audited_without_storing_request_payload(self):
        self.client.force_login(self.admin)
        path = reverse('comunicaciones:crear')
        response = self.client.post(
            path,
            {
                'titulo': 'Aviso auditado',
                'contenido': 'Contenido de prueba',
                'dirigido_a': 'Todos',
                'dato_privado': 'no debe persistirse',
            },
        )

        self.assertEqual(response.status_code, 302)
        event = AuditEvent.objects.get(path=path)
        self.assertEqual(event.actor, self.admin)
        self.assertEqual(event.method, 'POST')
        self.assertEqual(event.status_code, 302)
        self.assertNotIn('no debe persistirse', str(event))

    def test_read_request_is_not_audited(self):
        self.client.force_login(self.admin)
        self.client.get(reverse('comunicaciones:comunicados'))
        self.assertEqual(AuditEvent.objects.count(), 0)

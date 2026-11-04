from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from comunicaciones.models import Comunicado
from pqrs.models import Pqr
from reservas.models import Reserva, ZonaComun
from residentes.access import filtrar_por_propiedad
from usuarios.models import (
    ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE, ROL_VIGILANTE,
)
from usuarios.permisos import obtener_rol

from .permissions import RoleRequired
from .serializers import (
    ComunicadoSerializer, PQRSerializer, ReservaSerializer, UserSerializer,
    ZonaComunSerializer,
)

User = get_user_model()


class HealthView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = []

    def get(self, request):
        return Response({"status": "ok", "service": "horisoft-api"}, status=status.HTTP_200_OK)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        perfil = getattr(user, 'perfil', None)
        token['role'] = perfil.rol if perfil else ('Administrador' if user.is_superuser else None)
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data


class AuthLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth_login'


class AuthRefreshView(TokenRefreshView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth_refresh'


class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)


def reservas_visibles(usuario):
    reservas = filtrar_por_propiedad(
        Reserva.objects.select_related('zona', 'residencia__persona', 'residencia__unidad'),
        usuario,
        'zona__propiedad_horizontal',
    )
    if obtener_rol(usuario) == ROL_RESIDENTE:
        perfil = getattr(usuario, 'perfil', None)
        persona = perfil.persona if perfil else None
        return reservas.filter(residencia__persona=persona) if persona else reservas.none()
    return reservas


class ReservaListCreateView(ListCreateAPIView):
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated, RoleRequired]
    allowed_roles = (ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE, ROL_VIGILANTE)

    def get_queryset(self):
        return reservas_visibles(self.request.user)

    def perform_create(self, serializer):
        rol = obtener_rol(self.request.user)
        data = serializer.validated_data
        if rol == ROL_RESIDENTE:
            perfil = getattr(self.request.user, 'perfil', None)
            persona = perfil.persona if perfil else None
            residencia = data.get('residencia')
            if not persona or not residencia or residencia.persona_id != persona.pk:
                raise PermissionDenied('Solo puedes crear reservas para tus propias residencias.')
        serializer.save()


class ReservaDetailView(RetrieveAPIView):
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated, RoleRequired]
    allowed_roles = (ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE, ROL_VIGILANTE)
    queryset = Reserva.objects.none()
    lookup_field = 'id_reserva'
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        return reservas_visibles(self.request.user)


class ReservaCancelarView(APIView):
    permission_classes = [IsAuthenticated, RoleRequired]
    allowed_roles = (ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE)

    def post(self, request, pk):
        reserva = get_object_or_404(reservas_visibles(request.user), pk=pk)
        if reserva.estado == Reserva.ESTADO_CANCELADA:
            raise ValidationError({'estado': 'La reserva ya está cancelada.'})
        reserva.estado = Reserva.ESTADO_CANCELADA
        reserva.save(update_fields=['estado'])
        return Response(ReservaSerializer(reserva).data, status=status.HTTP_200_OK)


class ZonaComunListView(ListAPIView):
    serializer_class = ZonaComunSerializer
    permission_classes = [IsAuthenticated, RoleRequired]
    allowed_roles = (ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE, ROL_VIGILANTE)

    def get_queryset(self):
        return filtrar_por_propiedad(
            ZonaComun.objects.all(),
            self.request.user,
        )


class ComunicadoListView(ListAPIView):
    serializer_class = ComunicadoSerializer
    permission_classes = [IsAuthenticated, RoleRequired]
    allowed_roles = (ROL_ADMINISTRADOR, ROL_ADMINISTRATIVO, ROL_RESIDENTE, ROL_VIGILANTE)

    def get_queryset(self):
        comunicados = filtrar_por_propiedad(
            Comunicado.objects.filter(estado=Comunicado.ESTADO_PUBLICADO),
            self.request.user,
        )
        rol = obtener_rol(self.request.user)
        if rol == ROL_RESIDENTE:
            return comunicados.filter(dirigido_a__in=[
                Comunicado.DIRIGIDO_A_TODOS,
                Comunicado.DIRIGIDO_A_RESIDENTES,
            ])
        if rol == ROL_VIGILANTE:
            return comunicados.filter(dirigido_a__in=[
                Comunicado.DIRIGIDO_A_TODOS,
                Comunicado.DIRIGIDO_A_VIGILANTES,
            ])
        return comunicados


class ResidentMeView(APIView):
    permission_classes = [IsAuthenticated, RoleRequired]
    allowed_roles = (ROL_RESIDENTE,)

    def get(self, request):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)


class PqrListCreateView(ListCreateAPIView):
    serializer_class = PQRSerializer
    permission_classes = [IsAuthenticated, RoleRequired]
    allowed_roles = (ROL_ADMINISTRADOR, ROL_RESIDENTE, ROL_VIGILANTE)

    def get_queryset(self):
        pqrs = filtrar_por_propiedad(
            Pqr.objects.select_related('residencia__persona', 'residencia__unidad'),
            self.request.user,
            'residencia__unidad__propiedad_horizontal',
        )
        rol = obtener_rol(self.request.user)
        if rol == ROL_RESIDENTE:
            perfil = getattr(self.request.user, 'perfil', None)
            persona = perfil.persona if perfil else None
            if not persona:
                return pqrs.none()
            return pqrs.filter(residencia__persona=persona)
        return pqrs

    def perform_create(self, serializer):
        rol = obtener_rol(self.request.user)
        if rol == ROL_RESIDENTE:
            perfil = getattr(self.request.user, 'perfil', None)
            persona = perfil.persona if perfil else None
            residencia = serializer.validated_data.get('residencia')
            if not persona or not residencia or residencia.persona_id != persona.pk:
                raise PermissionDenied('Solo puedes crear PQRs para tus propias residencias.')
        serializer.save()

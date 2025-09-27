from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes

from .models import CustomUser, Role
from .serializers import (
    CustomTokenObtainPairSerializer,
    CustomUserSerializer,
    RoleSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    UserToggleActiveSerializer
)
from todoapi.utils.rate_limiting import rate_limit
from todoapi.utils.permissions import IsAdminOnly


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vista personalizada para obtener tokens JWT
    Incluye información adicional del usuario en la respuesta
    """
    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(
        summary="Obtener token JWT",
        description="Autentica un usuario y devuelve tokens de acceso y refresh con información del usuario",
        request=CustomTokenObtainPairSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'access': {'type': 'string'},
                    'refresh': {'type': 'string'},
                    'user': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'username': {'type': 'string'},
                            'email': {'type': 'string'},
                            'first_name': {'type': 'string'},
                            'last_name': {'type': 'string'},
                            'dni': {'type': 'string'},
                            'rol': {'type': 'object'},
                        }
                    }
                }
            }
        }
    )
    @rate_limit(requests_per_hour=20, requests_per_minute=3)
    def post(self, request, *args, **kwargs):
        """
        Login with strict rate limiting.
        Limited to 20 attempts per hour and 3 per minute per IP.
        """
        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    """
    Vista para cerrar sesión (logout)
    Invalida el refresh token
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Cerrar sesión",
        description="Cierra la sesión del usuario invalidando el refresh token",
        request={
            'type': 'object',
            'properties': {
                'refresh': {'type': 'string', 'description': 'Refresh token a invalidar'}
            }
        },
        responses={
            200: {'description': 'Sesión cerrada exitosamente'},
            400: {'description': 'Token inválido'}
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            
            # Validar que se proporcione el refresh token
            if not refresh_token:
                return Response(
                    {"error": "Se requiere el refresh token"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Invalidar el refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            # También cerrar la sesión de Django si existe
            logout(request)
            
            return Response(
                {"message": "Sesión cerrada exitosamente"}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": "Token inválido"}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Vista para ver y actualizar el perfil del usuario autenticado
    """
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    @extend_schema(
        summary="Obtener perfil de usuario",
        description="Obtiene la información del perfil del usuario autenticado"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Actualizar perfil de usuario",
        description="Actualiza la información del perfil del usuario autenticado"
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class ChangePasswordView(APIView):
    """
    Vista para cambiar la contraseña del usuario autenticado
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Cambiar contraseña",
        description="Cambia la contraseña del usuario autenticado",
        request=ChangePasswordSerializer,
        responses={
            200: {'description': 'Contraseña cambiada exitosamente'},
            400: {'description': 'Error en los datos proporcionados'}
        }
    )
    @rate_limit(requests_per_hour=10, requests_per_minute=2)
    def post(self, request):
        """
        Change password with rate limiting.
        Limited to 10 attempts per hour and 2 per minute per user.
        """
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Contraseña cambiada exitosamente"},
                status=status.HTTP_200_OK
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class UserListCreateView(generics.ListCreateAPIView):
    """
    Vista para listar y crear usuarios
    Solo accesible para administradores
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOnly]
    filterset_fields = ['is_active', 'rol', 'is_staff']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'dni']
    ordering_fields = ['date_joined', 'username', 'last_name']
    ordering = ['-date_joined']

    @extend_schema(
        summary="Listar usuarios",
        description="Lista todos los usuarios del sistema con filtros opcionales",
        parameters=[
            OpenApiParameter('is_active', OpenApiTypes.BOOL, description='Filtrar por estado activo'),
            OpenApiParameter('rol', OpenApiTypes.INT, description='Filtrar por rol'),
            OpenApiParameter('search', OpenApiTypes.STR, description='Buscar en username, nombre, email, dni'),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Crear usuario",
        description="Crea un nuevo usuario en el sistema"
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista para obtener, actualizar y eliminar usuarios específicos
    Solo accesible para administradores
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOnly]

    @extend_schema(
        summary="Obtener usuario",
        description="Obtiene los detalles de un usuario específico"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Actualizar usuario",
        description="Actualiza un usuario específico"
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="Eliminar usuario",
        description="Elimina (desactiva) un usuario específico"
    )
    def delete(self, request, *args, **kwargs):
        # En lugar de eliminar, desactivamos el usuario
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoleListView(generics.ListCreateAPIView):
    """
    Vista para listar y crear roles
    """
    queryset = Role.objects.filter(is_active=True)
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """
        Solo los administradores pueden crear roles
        """
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @extend_schema(
        summary="Listar roles",
        description="Lista todos los roles activos del sistema"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Crear rol",
        description="Crea un nuevo rol en el sistema (solo administradores)"
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@extend_schema(
    summary="Verificar estado de autenticación",
    description="Verifica si el usuario está autenticado y devuelve información básica",
    responses={
        200: {
            'type': 'object',
            'properties': {
                'authenticated': {'type': 'boolean'},
                'user': {'type': 'object'}
            }
        }
    }
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def auth_status(request):
    """
    Vista para verificar el estado de autenticación
    """
    if request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'rol': {
                    'id': request.user.rol.id,
                    'nombre': request.user.rol.nombre,
                    'permisos': request.user.rol.permisos
                } if request.user.rol else None,
            }
        })
    else:
        return Response({
            'authenticated': False,
            'user': None
        })


class UserToggleActiveView(APIView):
    """
    Vista para activar/desactivar usuarios
    Solo accesible para administradores
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminOnly]
    
    @extend_schema(
        summary="Activar/Desactivar usuario",
        description="Cambia el estado activo de un usuario específico. Solo administradores pueden realizar esta acción.",
        request=UserToggleActiveSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'user': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'username': {'type': 'string'},
                            'is_active': {'type': 'boolean'},
                            'email': {'type': 'string'},
                            'first_name': {'type': 'string'},
                            'last_name': {'type': 'string'}
                        }
                    }
                }
            },
            400: {'description': 'Error en los datos proporcionados'},
            403: {'description': 'Sin permisos para realizar esta acción'},
            404: {'description': 'Usuario no encontrado'}
        }
    )
    @rate_limit(requests_per_hour=30, requests_per_minute=5)
    def patch(self, request, user_id):
        """
        Activa o desactiva un usuario específico
        """
        try:
            # Obtener el usuario a modificar
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar que no se esté intentando modificar a sí mismo
        if request.user.id == user.id:
            return Response(
                {'error': 'No puedes cambiar tu propio estado de activación'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear el serializer con el contexto necesario
        serializer = UserToggleActiveSerializer(
            data=request.data,
            context={
                'user': user,
                'request': request
            }
        )
        
        if serializer.is_valid():
            # Guardar los cambios
            updated_user = serializer.save()
            
            # Preparar la respuesta
            action = "activado" if updated_user.is_active else "desactivado"
            message = f"Usuario '{updated_user.username}' {action} exitosamente"
            
            return Response({
                'message': message,
                'user': {
                    'id': updated_user.id,
                    'username': updated_user.username,
                    'is_active': updated_user.is_active,
                    'email': updated_user.email,
                    'first_name': updated_user.first_name,
                    'last_name': updated_user.last_name,
                    'rol': {
                        'id': updated_user.rol.id,
                        'nombre': updated_user.rol.nombre
                    } if updated_user.rol else None
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

"""
Servicio dedicado para la gestión de asignación de equipos sin cliente.
Este servicio maneja la lógica de negocio para equipos no asignados.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import GPS, SIMCard
from .serializers import GPSSerializer, SIMCardSerializer
from entities.models import Cliente


class EquipmentAssignmentService:
    """
    Service class for managing equipment assignment operations.
    Handles business logic for unassigned equipment management.
    """
    
    @staticmethod
    def get_available_equipment():
        """
        Get all available (unassigned) equipment.
        Returns GPS and SIM cards that are not assigned to any client.
        """
        available_gps = GPS.objects.filter(
            estado='no_asignado',
            is_active=True
        ).select_related('proveedor')
        
        available_simcards = SIMCard.objects.filter(
            estado='no_asignado',
            is_active=True
        ).select_related('proveedor')
        
        return {
            'gps_devices': GPSSerializer(available_gps, many=True).data,
            'sim_cards': SIMCardSerializer(available_simcards, many=True).data,
            'summary': {
                'total_gps': available_gps.count(),
                'total_simcards': available_simcards.count()
            }
        }
    
    @staticmethod
    def assign_equipment_to_client(equipment_type, equipment_id, client_id, user=None):
        """
        Assign equipment to a specific client.
        
        Args:
            equipment_type (str): 'gps' or 'simcard'
            equipment_id (int): ID of the equipment
            client_id (int): ID of the client
            user: User performing the operation
        """
        try:
            with transaction.atomic():
                # Get client
                client = get_object_or_404(Cliente, id=client_id, is_active=True)
                
                # Get equipment based on type
                if equipment_type.lower() == 'gps':
                    equipment = get_object_or_404(GPS, id=equipment_id, estado='no_asignado')
                    equipment.asignar_cliente(client, f"Asignado por {user.username if user else 'Sistema'}")
                    serializer = GPSSerializer(equipment)
                elif equipment_type.lower() == 'simcard':
                    equipment = get_object_or_404(SIMCard, id=equipment_id, estado='no_asignado')
                    equipment.asignar_cliente(client, f"Asignado por {user.username if user else 'Sistema'}")
                    serializer = SIMCardSerializer(equipment)
                else:
                    raise ValueError("Tipo de equipo no válido. Use 'gps' o 'simcard'")
                
                return {
                    'success': True,
                    'message': f'{equipment_type.upper()} asignado exitosamente al cliente {client.nombre}',
                    'equipment': serializer.data,
                    'client': {
                        'id': client.id,
                        'nombre': client.nombre,
                        'correo': client.correo
                    }
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al asignar equipo: {str(e)}',
                'equipment': None,
                'client': None
            }
    
    @staticmethod
    def unassign_equipment(equipment_type, equipment_id, user=None):
        """
        Unassign equipment from its current client.
        
        Args:
            equipment_type (str): 'gps' or 'simcard'
            equipment_id (int): ID of the equipment
            user: User performing the operation
        """
        try:
            with transaction.atomic():
                # Get equipment based on type
                if equipment_type.lower() == 'gps':
                    equipment = get_object_or_404(GPS, id=equipment_id, estado='asignado')
                    client_name = equipment.cliente.nombre if equipment.cliente else 'Cliente desconocido'
                    equipment.desasignar_cliente(f"Desasignado por {user.username if user else 'Sistema'}")
                    serializer = GPSSerializer(equipment)
                elif equipment_type.lower() == 'simcard':
                    equipment = get_object_or_404(SIMCard, id=equipment_id, estado='asignado')
                    client_name = equipment.cliente.nombre if equipment.cliente else 'Cliente desconocido'
                    equipment.desasignar_cliente(f"Desasignado por {user.username if user else 'Sistema'}")
                    serializer = SIMCardSerializer(equipment)
                else:
                    raise ValueError("Tipo de equipo no válido. Use 'gps' o 'simcard'")
                
                return {
                    'success': True,
                    'message': f'{equipment_type.upper()} desasignado exitosamente del cliente {client_name}',
                    'equipment': serializer.data
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al desasignar equipo: {str(e)}',
                'equipment': None
            }


# API Views for the Equipment Assignment Service

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_equipment_view(request):
    """
    API endpoint to get all available (unassigned) equipment.
    
    GET /api/inventory/equipment/available/
    """
    try:
        data = EquipmentAssignmentService.get_available_equipment()
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': f'Error al obtener equipos disponibles: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_equipment_view(request):
    """
    API endpoint to assign equipment to a client.
    
    POST /api/inventory/equipment/assign/
    Body: {
        "equipment_type": "gps" | "simcard",
        "equipment_id": int,
        "client_id": int
    }
    """
    equipment_type = request.data.get('equipment_type')
    equipment_id = request.data.get('equipment_id')
    client_id = request.data.get('client_id')
    
    if not all([equipment_type, equipment_id, client_id]):
        return Response(
            {'error': 'equipment_type, equipment_id y client_id son requeridos'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        result = EquipmentAssignmentService.assign_equipment_to_client(
            equipment_type, equipment_id, client_id, request.user
        )
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unassign_equipment_view(request):
    """
    API endpoint to unassign equipment from its current client.
    
    POST /api/inventory/equipment/unassign/
    Body: {
        "equipment_type": "gps" | "simcard",
        "equipment_id": int
    }
    """
    equipment_type = request.data.get('equipment_type')
    equipment_id = request.data.get('equipment_id')
    
    if not all([equipment_type, equipment_id]):
        return Response(
            {'error': 'equipment_type y equipment_id son requeridos'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        result = EquipmentAssignmentService.unassign_equipment(
            equipment_type, equipment_id, request.user
        )
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
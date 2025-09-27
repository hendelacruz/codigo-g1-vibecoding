"""
GPS State Management System

This module provides a robust state management system for GPS devices
that prevents inconsistent states and manages state transitions properly.
"""

from typing import Dict, List, Optional, Tuple
from django.core.exceptions import ValidationError


class GPSStateManager:
    """
    Manages GPS state and process logic.
    
    This class handles the business logic for GPS management with separated
    estado (assignment status) and proceso (operational condition).
    """
    
    # Define valid process transitions
    PROCESO_TRANSITIONS = {
        'en_produccion': ['dañado', 'garantia', 'en_mantenimiento', 'en_transito', 'dado_de_baja'],
        'dañado': ['garantia', 'dado_de_baja'],
        'garantia': ['en_produccion', 'dañado', 'en_mantenimiento', 'dado_de_baja'],
        'en_mantenimiento': ['en_produccion', 'dañado', 'dado_de_baja'],
        'en_transito': ['en_produccion', 'dañado'],
        'dado_de_baja': []  # Terminal state
    }
    
    # Processes that allow assignment
    ASSIGNABLE_PROCESSES = ['en_produccion', 'en_transito']
    
    # Processes that require attention
    ATTENTION_PROCESSES = ['dañado', 'garantia']
    

    
    @classmethod
    def validate_proceso_transition(cls, current_proceso: str, new_proceso: str, estado: str) -> Tuple[bool, str]:
        """
        Validates if a process transition is allowed.
        
        Args:
            current_proceso: Current GPS process
            new_proceso: Desired new process
            estado: Current GPS estado (asignado/no_asignado)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if transition is defined
        valid_transitions = cls.PROCESO_TRANSITIONS.get(current_proceso, [])
        if new_proceso not in valid_transitions:
            return False, f"Invalid transition from '{current_proceso}' to '{new_proceso}'"
        
        # Business logic validations
        if estado == 'asignado' and new_proceso not in cls.ASSIGNABLE_PROCESSES:
            return False, f"Cannot change to '{new_proceso}' while GPS is assigned"
        
        return True, ""
    

    
    @classmethod
    def can_assign_client(cls, proceso: str) -> bool:
        """
        Check if a GPS in the given process can be assigned to a client.
        
        Args:
            proceso: GPS process to check
            
        Returns:
            True if GPS can be assigned to a client in this process
        """
        return proceso in cls.ASSIGNABLE_PROCESSES
    
    @classmethod
    def get_valid_proceso_transitions(cls, current_proceso: str) -> list:
        """
        Get valid process transitions for a given current process.
        
        Args:
            current_proceso: Current GPS process
            
        Returns:
            List of valid next processes
        """
        return cls.PROCESO_TRANSITIONS.get(current_proceso, [])
    
    @classmethod
    def validate_state_transition(cls, current_estado: str, new_estado: str, has_client: bool = False) -> Tuple[bool, str]:
        """
        Validate estado transition based on client assignment.
        
        Args:
            current_estado: Current GPS estado
            new_estado: Target GPS estado
            has_client: Whether GPS has a client assigned
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Define valid estado transitions
        estado_transitions = {
            'no_asignado': ['asignado'],
            'asignado': ['no_asignado']
        }
        
        # Check if transition is valid
        if current_estado not in estado_transitions:
            return False, f"Estado '{current_estado}' no es válido"
        
        if new_estado not in estado_transitions[current_estado]:
            return False, f"Transición de '{current_estado}' a '{new_estado}' no es válida"
        
        # Validate estado consistency with client
        if new_estado == 'asignado' and not has_client:
            return False, "No se puede cambiar a 'asignado' sin cliente"
        
        if new_estado == 'no_asignado' and has_client:
            return False, "No se puede cambiar a 'no_asignado' con cliente asignado"
        
        return True, ""
    
    @classmethod
    def auto_update_state_on_client_change(cls, gps_instance, old_client, new_client) -> str:
        """
        Automatically update GPS estado based on client assignment change.
        
        Args:
            gps_instance: GPS model instance
            old_client: Previous client (or None)
            new_client: New client (or None)
            
        Returns:
            New estado for the GPS
        """
        if new_client and not old_client:
            # Client assigned
            return 'asignado'
        elif old_client and not new_client:
            # Client removed
            return 'no_asignado'
        elif new_client and old_client:
            # Client changed
            return 'asignado'
        else:
            # No change in client status
            return gps_instance.estado
    
    @classmethod
    def get_valid_next_states(cls, current_estado: str, has_client: bool = False) -> list:
        """
        Get valid next estados based on current estado and client status.
        
        Args:
            current_estado: Current GPS estado
            has_client: Whether GPS has a client assigned
            
        Returns:
            List of valid next estados
        """
        estado_transitions = {
            'no_asignado': ['asignado'],
            'asignado': ['no_asignado']
        }
        
        if current_estado not in estado_transitions:
            return []
        
        valid_estados = estado_transitions[current_estado]
        
        # Filter based on client status
        if not has_client:
            # Remove states that require a client
            valid_estados = [estado for estado in valid_estados if estado != 'asignado']
        
        return valid_estados
    
    @classmethod
    def get_assignable_states(cls) -> list:
        """
        Get list of estados that allow client assignment.
        
        Returns:
            List of assignable estados
        """
        return ['no_asignado']
    
    @classmethod
    def requires_attention(cls, proceso: str) -> bool:
        """
        Check if a GPS process requires attention.
        
        Args:
            proceso: GPS process to check
            
        Returns:
            True if process requires attention
        """
        return proceso in cls.ATTENTION_PROCESSES
    
    @classmethod
    def get_proceso_priority(cls, proceso: str) -> int:
        """
        Gets priority level for process (higher number = higher priority).
        
        Used for sorting and filtering GPS devices by urgency.
        
        Args:
            proceso: GPS process
            
        Returns:
            Priority level (0-5)
        """
        priority_map = {
            'dado_de_baja': 0,
            'en_produccion': 1,
            'en_transito': 2,
            'en_mantenimiento': 3,
            'garantia': 4,
            'dañado': 5
        }
        return priority_map.get(proceso, 0)
    



class GPSStateValidator:
    """
    Validates GPS state and process consistency and business rules.
    """
    
    @classmethod
    def validate_gps_state(cls, gps_instance) -> tuple[bool, list]:
        """
        Validates GPS state and process consistency.
        
        Args:
            gps_instance: GPS model instance
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check client assignment consistency
        if gps_instance.estado == 'asignado' and not gps_instance.cliente:
            errors.append("GPS marcado como 'asignado' pero no tiene cliente")
        
        if gps_instance.estado == 'no_asignado' and gps_instance.cliente:
            errors.append("GPS marcado como 'no_asignado' pero tiene cliente asignado")
        
        # Check process validity for assigned GPS
        if gps_instance.estado == 'asignado' and gps_instance.proceso not in GPSStateManager.ASSIGNABLE_PROCESSES:
            errors.append(f"GPS asignado no puede estar en proceso '{gps_instance.proceso}'")
        
        # Check estado validity
        valid_estados = ['asignado', 'no_asignado']
        if gps_instance.estado not in valid_estados:
            errors.append(f"Estado '{gps_instance.estado}' no es válido")
        
        # Check proceso validity
        valid_procesos = list(GPSStateManager.PROCESO_TRANSITIONS.keys())
        if gps_instance.proceso not in valid_procesos:
            errors.append(f"Proceso '{gps_instance.proceso}' no es válido")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def suggest_estado_fix(gps_instance) -> Optional[str]:
        """
        Suggests a corrected estado for GPS with validation issues.
        
        Args:
            gps_instance: GPS model instance
            
        Returns:
            Suggested estado or None if no fix needed
        """
        is_valid, errors = GPSStateValidator.validate_gps_state(gps_instance)
        if is_valid:
            return None
        
        has_client = bool(gps_instance.cliente)
        current_estado = gps_instance.estado
        
        # Suggest fixes based on common issues
        if current_estado == 'asignado' and not has_client:
            return 'no_asignado'
        
        if current_estado == 'no_asignado' and has_client:
            return 'asignado'
        
        return None


# Utility functions for backward compatibility
def validate_gps_proceso_change(gps_instance, new_proceso: str) -> None:
    """
    Validates a GPS process change and raises ValidationError if invalid.
    
    Args:
        gps_instance: GPS model instance
        new_proceso: Proposed new process
        
    Raises:
        ValidationError: If process change is invalid
    """
    current_proceso = gps_instance.proceso
    estado = gps_instance.estado
    
    is_valid, error_msg = GPSStateManager.validate_proceso_transition(
        current_proceso, new_proceso, estado
    )
    
    if not is_valid:
        raise ValidationError(error_msg)


def get_gps_proceso_choices():
    """
    Returns all available GPS process choices for forms/serializers.
    
    Returns:
        List of (value, label) tuples
    """
    from .models import GPS  # Import here to avoid circular imports
    return GPS.PROCESO_CHOICES


def get_gps_estado_choices():
    """
    Returns all available GPS estado choices for forms/serializers.
    
    Returns:
        List of (value, label) tuples
    """
    from .models import GPS  # Import here to avoid circular imports
    return GPS.ESTADO_CHOICES
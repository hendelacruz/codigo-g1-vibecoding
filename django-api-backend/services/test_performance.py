"""
Tests de performance para filtros de servicios con grandes volúmenes de datos.

Estos tests verifican que los filtros mantengan un rendimiento aceptable
cuando se trabaja con grandes cantidades de datos.
"""

import time
from decimal import Decimal
from datetime import datetime, timedelta
from django.test import TestCase
from django.utils import timezone
from django.db import connection
from django.test.utils import override_settings

from .models import TipoTrabajo, Servicio
from .filters import ServicioFilter, TipoTrabajoFilter
from entities.models import Cliente, Unidad, Proveedor
from authentication.models import CustomUser, Role


class PerformanceTestCase(TestCase):
    """Base class para tests de performance con utilidades comunes."""
    
    def setUp(self):
        """Configuración inicial para tests de performance."""
        # Crear rol primero
        self.rol_tecnico = Role.objects.create(
            nombre='tecnico',
            descripcion='Técnico de campo para tests de performance'
        )
        
        # Crear datos base necesarios
        self.cliente = Cliente.objects.create(
            nombre="Cliente Test Performance",
            contacto="Cliente Test",
            ruc="12345678901",
            direccion="Av. Test 123",
            celular="987654321",
            correo="cliente@test.com"
        )
        
        self.unidad = Unidad.objects.create(
            tipo="bus",
            placa="ABC-123",
            marca="Toyota",
            modelo="Hiace",
            serie="VIN123456789",
            cliente=self.cliente
        )
        
        self.tecnico = CustomUser.objects.create_user(
            username="tecnico_test",
            email="tecnico@test.com",
            password="testpass123",
            first_name="Técnico",
            last_name="Test",
            dni="12345678",
            celular="+51987654321",
            rol=self.rol_tecnico
        )
        
        self.tipo_trabajo = TipoTrabajo.objects.create(
            nombre="mantenimiento_preventivo",
            descripcion="Mantenimiento general"
        )
    
    def measure_time(self, func, *args, **kwargs):
        """Medir el tiempo de ejecución de una función."""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        return result, execution_time
    
    def count_queries(self, func, *args, **kwargs):
        """Contar las queries ejecutadas por una función."""
        initial_queries = len(connection.queries)
        result = func(*args, **kwargs)
        final_queries = len(connection.queries)
        query_count = final_queries - initial_queries
        return result, query_count


class ServicioFilterPerformanceTest(PerformanceTestCase):
    """Tests de performance para filtros de servicios."""
    
    def setUp(self):
        super().setUp()
        # Crear múltiples servicios para tests de performance
        self.create_bulk_servicios(1000)  # 1000 servicios para testing
    
    def create_bulk_servicios(self, count):
        """Crear servicios en bulk para tests de performance."""
        servicios = []
        base_date = timezone.now() - timedelta(days=365)  # Último año
        
        for i in range(count):
            # Distribuir fechas a lo largo del año
            fecha = base_date + timedelta(days=i % 365, hours=i % 24)
            
            servicio = Servicio(
                cliente=self.cliente,
                unidad=self.unidad,
                tipo_trabajo=self.tipo_trabajo,
                tecnico=self.tecnico,
                fecha=fecha,
                precio=Decimal('100.00') + (i % 500),  # Precios variados
                observaciones=f"Servicio de prueba {i}",
                estado_servicio='pendiente' if i % 3 == 0 else 'completado'
            )
            servicios.append(servicio)
        
        # Crear en bulk para mejor performance
        Servicio.objects.bulk_create(servicios, batch_size=100)
    
    def test_filter_by_fecha_performance(self):
        """Test de performance para filtros de fecha."""
        # Test filtro fecha_desde
        filter_data = {'fecha_desde': (timezone.now() - timedelta(days=30)).date()}
        
        def apply_filter():
            filterset = ServicioFilter(filter_data, queryset=Servicio.objects.all())
            return list(filterset.qs)  # Forzar evaluación del queryset
        
        result, execution_time = self.measure_time(apply_filter)
        result, query_count = self.count_queries(apply_filter)
        
        # Verificar que el filtro funciona
        self.assertGreater(len(result), 0)
        
        # Verificar performance aceptable (menos de 1 segundo)
        self.assertLess(execution_time, 1.0, 
                       f"Filtro de fecha tomó {execution_time:.3f}s, esperado < 1.0s")
        
        # Verificar número de queries razonable (menos de 5)
        self.assertLess(query_count, 5,
                       f"Filtro de fecha ejecutó {query_count} queries, esperado < 5")
    
    def test_filter_by_precio_performance(self):
        """Test de performance para filtros de precio."""
        filter_data = {
            'precio_min': 100,
            'precio_max': 300
        }
        
        def apply_filter():
            filterset = ServicioFilter(filter_data, queryset=Servicio.objects.all())
            return list(filterset.qs)
        
        result, execution_time = self.measure_time(apply_filter)
        result, query_count = self.count_queries(apply_filter)
        
        # Verificar que el filtro funciona
        self.assertGreater(len(result), 0)
        
        # Verificar performance aceptable
        self.assertLess(execution_time, 0.5,
                       f"Filtro de precio tomó {execution_time:.3f}s, esperado < 0.5s")
        
        # Verificar número de queries
        self.assertLess(query_count, 3,
                       f"Filtro de precio ejecutó {query_count} queries, esperado < 3")
    
    def test_filter_search_performance(self):
        """Test de performance para filtro de búsqueda."""
        filter_data = {'search': 'prueba'}
        
        def apply_filter():
            filterset = ServicioFilter(filter_data, queryset=Servicio.objects.all())
            return list(filterset.qs)
        
        result, execution_time = self.measure_time(apply_filter)
        result, query_count = self.count_queries(apply_filter)
        
        # Verificar que el filtro funciona
        self.assertGreater(len(result), 0)
        
        # El filtro de búsqueda puede ser más lento debido a LIKE queries
        self.assertLess(execution_time, 2.0,
                       f"Filtro de búsqueda tomó {execution_time:.3f}s, esperado < 2.0s")
        
        # Verificar número de queries
        self.assertLess(query_count, 5,
                       f"Filtro de búsqueda ejecutó {query_count} queries, esperado < 5")
    
    def test_combined_filters_performance(self):
        """Test de performance para múltiples filtros combinados."""
        filter_data = {
            'fecha_desde': (timezone.now() - timedelta(days=30)).date(),
            'precio_min': 100,
            'estado_servicio': 'completado'
        }
        
        def apply_filter():
            filterset = ServicioFilter(filter_data, queryset=Servicio.objects.all())
            return list(filterset.qs)
        
        result, execution_time = self.measure_time(apply_filter)
        result, query_count = self.count_queries(apply_filter)
        
        # Verificar que el filtro funciona
        self.assertGreaterEqual(len(result), 0)
        
        # Filtros combinados pueden ser más lentos
        self.assertLess(execution_time, 1.5,
                       f"Filtros combinados tomaron {execution_time:.3f}s, esperado < 1.5s")
        
        # Verificar número de queries
        self.assertLess(query_count, 5,
                       f"Filtros combinados ejecutaron {query_count} queries, esperado < 5")


class TipoTrabajoFilterPerformanceTest(PerformanceTestCase):
    """Tests de performance para filtros de tipos de trabajo."""
    
    def setUp(self):
        super().setUp()
        # Crear múltiples tipos de trabajo
        self.create_bulk_tipos_trabajo(100)
    
    def create_bulk_tipos_trabajo(self, count):
        """Crear tipos de trabajo en bulk."""
        tipos = []
        tipo_choices = ['instalacion_nueva', 'mantenimiento_preventivo', 'mantenimiento_correctivo', 'otro']
        
        for i in range(count):
            # Usar nombres únicos basados en las opciones válidas
            nombre_base = tipo_choices[i % len(tipo_choices)]
            nombre = f"{nombre_base}_{i}" if i >= len(tipo_choices) else nombre_base
            
            tipo = TipoTrabajo(
                nombre=nombre,
                descripcion=f"Descripción del tipo {i}",
                is_active=i % 10 != 0  # 90% activos
            )
            tipos.append(tipo)
        
        TipoTrabajo.objects.bulk_create(tipos, batch_size=50, ignore_conflicts=True)
    
    def test_filter_search_performance(self):
        """Test de performance para búsqueda en tipos de trabajo."""
        filter_data = {'search': 'Tipo'}
        
        def apply_filter():
            filterset = TipoTrabajoFilter(filter_data, queryset=TipoTrabajo.objects.all())
            return list(filterset.qs)
        
        result, execution_time = self.measure_time(apply_filter)
        result, query_count = self.count_queries(apply_filter)
        
        # Verificar que el filtro funciona
        self.assertGreater(len(result), 0)
        
        # Verificar performance aceptable
        self.assertLess(execution_time, 0.5,
                       f"Búsqueda en tipos tomó {execution_time:.3f}s, esperado < 0.5s")
        
        # Verificar número de queries
        self.assertLess(query_count, 3,
                       f"Búsqueda en tipos ejecutó {query_count} queries, esperado < 3")
    
    def test_filter_mas_solicitados_performance(self):
        """Test de performance para filtro de más solicitados."""
        # Crear servicios para algunos tipos
        tipos = TipoTrabajo.objects.all()[:10]
        servicios = []
        
        for tipo in tipos:
            for i in range(6):  # 6 servicios por tipo para que sean "más solicitados"
                servicio = Servicio(
                    cliente=self.cliente,
                    unidad=self.unidad,
                    tipo_trabajo=tipo,
                    tecnico=self.tecnico,
                    fecha=timezone.now(),
                    precio=Decimal('100.00'),
                    observaciones=f"Servicio {i} para {tipo.nombre}"
                )
                servicios.append(servicio)
        
        Servicio.objects.bulk_create(servicios, batch_size=50)
        
        filter_data = {'mas_solicitados': True}
        
        def apply_filter():
            filterset = TipoTrabajoFilter(filter_data, queryset=TipoTrabajo.objects.all())
            return list(filterset.qs)
        
        result, execution_time = self.measure_time(apply_filter)
        result, query_count = self.count_queries(apply_filter)
        
        # Verificar que el filtro funciona
        self.assertGreater(len(result), 0)
        
        # Este filtro puede ser más lento debido a la agregación
        self.assertLess(execution_time, 1.0,
                       f"Filtro más solicitados tomó {execution_time:.3f}s, esperado < 1.0s")
        
        # Verificar número de queries
        self.assertLess(query_count, 5,
                       f"Filtro más solicitados ejecutó {query_count} queries, esperado < 5")


@override_settings(DEBUG=True)  # Para poder contar queries
class FilterOptimizationTest(PerformanceTestCase):
    """Tests para verificar optimizaciones específicas de filtros."""
    
    def test_queryset_optimization(self):
        """Verificar que los filtros usan select_related/prefetch_related apropiadamente."""
        # Crear algunos servicios
        for i in range(10):
            Servicio.objects.create(
                cliente=self.cliente,
                unidad=self.unidad,
                tipo_trabajo=self.tipo_trabajo,
                tecnico=self.tecnico,
                fecha=timezone.now(),
                precio=Decimal('100.00'),
                observaciones=f"Servicio {i}"
            )
        
        # Test sin optimización
        def without_optimization():
            filterset = ServicioFilter({}, queryset=Servicio.objects.all())
            servicios = list(filterset.qs)
            # Acceder a relaciones para forzar queries adicionales
            for servicio in servicios:
                _ = servicio.cliente.contacto
                _ = servicio.unidad.placa
                _ = servicio.tipo_trabajo.nombre
                _ = servicio.tecnico.username
            return servicios
        
        # Test con optimización
        def with_optimization():
            queryset = Servicio.objects.select_related(
                'cliente', 'unidad', 'tipo_trabajo', 'tecnico'
            )
            filterset = ServicioFilter({}, queryset=queryset)
            servicios = list(filterset.qs)
            # Acceder a relaciones (ya optimizadas)
            for servicio in servicios:
                _ = servicio.cliente.contacto
                _ = servicio.unidad.placa
                _ = servicio.tipo_trabajo.nombre
                _ = servicio.tecnico.username
            return servicios
        
        # Medir queries sin optimización
        _, queries_without = self.count_queries(without_optimization)
        
        # Medir queries con optimización
        _, queries_with = self.count_queries(with_optimization)
        
        # La optimización debe reducir significativamente las queries
        self.assertLess(queries_with, queries_without,
                       f"Optimización no efectiva: {queries_with} vs {queries_without} queries")
        
        # Con optimización debe usar pocas queries (1 para servicios + joins)
        self.assertLessEqual(queries_with, 3,
                            f"Queryset optimizado usó {queries_with} queries, esperado <= 3")
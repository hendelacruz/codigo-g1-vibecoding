from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from datetime import datetime, timedelta
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Metric, Alert
from .serializers import (
    MetricSerializer, AlertSerializer, ComprehensiveDashboardSerializer,
    AlertActionSerializer, DashboardFilterSerializer
)
from .services import DashboardService, AlertService


class DashboardViewSet(viewsets.GenericViewSet):
    """
    ViewSet for dashboard operations and KPI retrieval
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get comprehensive dashboard data",
        description="Retrieve all KPIs and metrics for the dashboard",
        parameters=[
            OpenApiParameter(
                name='period_start',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='Start date for the period (ISO format)'
            ),
            OpenApiParameter(
                name='period_end',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='End date for the period (ISO format)'
            ),
        ],
        responses={200: ComprehensiveDashboardSerializer}
    )
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """
        Get comprehensive dashboard overview with all KPIs
        """
        # Parse date parameters
        period_start = request.query_params.get('period_start')
        period_end = request.query_params.get('period_end')
        
        if period_start:
            try:
                period_start = datetime.fromisoformat(period_start.replace('Z', '+00:00'))
            except ValueError:
                return Response(
                    {'error': 'Invalid period_start format. Use ISO format.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if period_end:
            try:
                period_end = datetime.fromisoformat(period_end.replace('Z', '+00:00'))
            except ValueError:
                return Response(
                    {'error': 'Invalid period_end format. Use ISO format.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Get comprehensive dashboard data
        dashboard_data = DashboardService.get_comprehensive_dashboard(
            period_start=period_start,
            period_end=period_end
        )
        
        serializer = ComprehensiveDashboardSerializer(dashboard_data)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get comprehensive dashboard data (alias)",
        description="Retrieve all KPIs and metrics for the dashboard (same as overview)",
        parameters=[
            OpenApiParameter(
                name='period_start',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='Start date for the period (ISO format)'
            ),
            OpenApiParameter(
                name='period_end',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='End date for the period (ISO format)'
            ),
        ],
        responses={200: ComprehensiveDashboardSerializer}
    )
    @action(detail=False, methods=['get'])
    def comprehensive(self, request):
        """
        Get comprehensive dashboard overview with all KPIs (alias for overview)
        """
        return self.overview(request)
    
    @extend_schema(
        summary="Get sales KPIs",
        description="Retrieve sales-related key performance indicators",
        parameters=[
            OpenApiParameter(
                name='period_start',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='Start date for the period'
            ),
            OpenApiParameter(
                name='period_end',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='End date for the period'
            ),
        ]
    )
    @action(detail=False, methods=['get'])
    def sales_kpis(self, request):
        """
        Get sales-specific KPIs
        """
        period_start = request.query_params.get('period_start')
        period_end = request.query_params.get('period_end')
        
        if period_start:
            try:
                period_start = datetime.fromisoformat(period_start.replace('Z', '+00:00'))
            except ValueError:
                return Response(
                    {'error': 'Invalid period_start format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if period_end:
            try:
                period_end = datetime.fromisoformat(period_end.replace('Z', '+00:00'))
            except ValueError:
                return Response(
                    {'error': 'Invalid period_end format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        sales_kpis = DashboardService.get_sales_kpis(period_start, period_end)
        return Response(sales_kpis)
    
    @extend_schema(
        summary="Get inventory KPIs",
        description="Retrieve inventory-related key performance indicators"
    )
    @action(detail=False, methods=['get'])
    def inventory_kpis(self, request):
        """
        Get inventory-specific KPIs
        """
        inventory_kpis = DashboardService.get_inventory_kpis()
        return Response(inventory_kpis)
    
    @extend_schema(
        summary="Get user KPIs",
        description="Retrieve user-related key performance indicators",
        parameters=[
            OpenApiParameter(
                name='period_start',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='Start date for the period'
            ),
            OpenApiParameter(
                name='period_end',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='End date for the period'
            ),
        ]
    )
    @action(detail=False, methods=['get'])
    def user_kpis(self, request):
        """
        Get user-specific KPIs
        """
        period_start = request.query_params.get('period_start')
        period_end = request.query_params.get('period_end')
        
        if period_start:
            period_start = datetime.fromisoformat(period_start.replace('Z', '+00:00'))
        if period_end:
            period_end = datetime.fromisoformat(period_end.replace('Z', '+00:00'))
        
        user_kpis = DashboardService.get_user_kpis(period_start, period_end)
        return Response(user_kpis)
    
    @extend_schema(
        summary="Get financial KPIs",
        description="Retrieve financial key performance indicators",
        parameters=[
            OpenApiParameter(
                name='period_start',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='Start date for the period'
            ),
            OpenApiParameter(
                name='period_end',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='End date for the period'
            ),
        ]
    )
    @action(detail=False, methods=['get'])
    def financial_kpis(self, request):
        """
        Get financial-specific KPIs
        """
        period_start = request.query_params.get('period_start')
        period_end = request.query_params.get('period_end')
        
        if period_start:
            period_start = datetime.fromisoformat(period_start.replace('Z', '+00:00'))
        if period_end:
            period_end = datetime.fromisoformat(period_end.replace('Z', '+00:00'))
        
        financial_kpis = DashboardService.get_financial_kpis(period_start, period_end)
        return Response(financial_kpis)


class MetricViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing metrics
    """
    queryset = Metric.objects.all()
    serializer_class = MetricSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['metric_type', 'period_type']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'period_start', 'value']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """
        Set the created_by field when creating a metric
        """
        serializer.save(created_by=self.request.user)
    
    @extend_schema(
        summary="Get metrics by type",
        description="Retrieve metrics filtered by type",
        parameters=[
            OpenApiParameter(
                name='metric_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Type of metric to filter by'
            ),
        ]
    )
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """
        Get metrics filtered by type
        """
        metric_type = request.query_params.get('metric_type')
        if not metric_type:
            return Response(
                {'error': 'metric_type parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        metrics = self.get_queryset().filter(metric_type=metric_type)
        serializer = self.get_serializer(metrics, many=True)
        return Response(serializer.data)


class AlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing alerts
    """
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['alert_type', 'severity', 'status']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'severity']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """
        Set the created_by field when creating an alert
        """
        serializer.save(created_by=self.request.user)
    
    @extend_schema(
        summary="Get active alerts",
        description="Retrieve all active alerts"
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Get all active alerts
        """
        active_alerts = AlertService.get_active_alerts()
        serializer = self.get_serializer(active_alerts, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Acknowledge or resolve alert",
        description="Perform actions on alerts (acknowledge or resolve)",
        request=AlertActionSerializer
    )
    @action(detail=True, methods=['post'])
    def action_alert(self, request, pk=None):
        """
        Acknowledge or resolve an alert
        """
        alert = self.get_object()
        serializer = AlertActionSerializer(data=request.data)
        
        if serializer.is_valid():
            action_type = serializer.validated_data['action']
            
            if action_type == 'acknowledge':
                updated_alert = AlertService.acknowledge_alert(alert.id, request.user)
            elif action_type == 'resolve':
                updated_alert = AlertService.resolve_alert(alert.id, request.user)
            else:
                return Response(
                    {'error': 'Invalid action'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if updated_alert:
                response_serializer = self.get_serializer(updated_alert)
                return Response(response_serializer.data)
            else:
                return Response(
                    {'error': 'Alert not found or cannot be updated'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Acknowledge alert",
        description="Acknowledge a specific alert"
    )
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """
        Acknowledge an alert
        """
        alert = self.get_object()
        updated_alert = AlertService.acknowledge_alert(alert.id, request.user)
        
        if updated_alert:
            response_serializer = self.get_serializer(updated_alert)
            return Response(response_serializer.data)
        else:
            return Response(
                {'error': 'Alert not found or cannot be acknowledged'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        summary="Resolve alert",
        description="Resolve a specific alert"
    )
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """
        Resolve an alert
        """
        alert = self.get_object()
        updated_alert = AlertService.resolve_alert(alert.id, request.user)
        
        if updated_alert:
            response_serializer = self.get_serializer(updated_alert)
            return Response(response_serializer.data)
        else:
            return Response(
                {'error': 'Alert not found or cannot be resolved'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        summary="Check for new alerts",
        description="Trigger alert checking for low stock and high sales"
    )
    @action(detail=False, methods=['post'])
    def check_alerts(self, request):
        """
        Manually trigger alert checking
        """
        # Check for low stock alerts
        low_stock_alerts = AlertService.check_low_stock_alerts()
        
        # Check for high sales alerts
        high_sales_alerts = AlertService.check_high_sales_alerts()
        
        total_alerts = len(low_stock_alerts) + len(high_sales_alerts)
        
        return Response({
            'message': f'{total_alerts} new alerts created',
            'low_stock_alerts': len(low_stock_alerts),
            'high_sales_alerts': len(high_sales_alerts)
        })
    
    @extend_schema(
        summary="Get alert statistics",
        description="Get statistics about alerts by type and severity"
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get alert statistics
        """
        from django.db.models import Count
        
        # Alerts by type
        alerts_by_type = Alert.objects.values('alert_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Alerts by severity
        alerts_by_severity = Alert.objects.values('severity').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Alerts by status
        alerts_by_status = Alert.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Recent alerts (last 7 days)
        recent_alerts_count = Alert.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        return Response({
            'alerts_by_type': list(alerts_by_type),
            'alerts_by_severity': list(alerts_by_severity),
            'alerts_by_status': list(alerts_by_status),
            'recent_alerts_count': recent_alerts_count,
            'total_alerts': Alert.objects.count()
        })

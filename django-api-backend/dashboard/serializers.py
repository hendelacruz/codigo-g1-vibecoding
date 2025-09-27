from rest_framework import serializers
from .models import Metric, Alert


class MetricSerializer(serializers.ModelSerializer):
    """
    Serializer for Metric model
    """
    period_type_display = serializers.CharField(source='get_period_type_display', read_only=True)
    metric_type_display = serializers.CharField(source='get_metric_type_display', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Metric
        fields = [
            'id', 'name', 'metric_type', 'metric_type_display',
            'value', 'period_type', 'period_type_display',
            'period_start', 'period_end', 'description', 'metadata',
            'created_at', 'updated_at', 'created_by', 'created_by_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return None


class AlertSerializer(serializers.ModelSerializer):
    """
    Serializer for Alert model
    """
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    acknowledged_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Alert
        fields = [
            'id', 'title', 'message', 'alert_type', 'alert_type_display',
            'severity', 'severity_display', 'status', 'status_display',
            'threshold_value', 'current_value', 'metadata',
            'created_at', 'acknowledged_at', 'resolved_at',
            'created_by', 'created_by_name', 'acknowledged_by', 'acknowledged_by_name'
        ]
        read_only_fields = [
            'id', 'created_at', 'acknowledged_at', 'resolved_at',
            'created_by', 'acknowledged_by'
        ]
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return None
    
    def get_acknowledged_by_name(self, obj):
        if obj.acknowledged_by:
            return f"{obj.acknowledged_by.first_name} {obj.acknowledged_by.last_name}".strip()
        return None


class DashboardKPISerializer(serializers.Serializer):
    """
    Serializer for dashboard KPI data
    """
    # Sales KPIs
    total_sales_amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    total_sales_count = serializers.IntegerField(required=False)
    average_sale_amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    sales_by_status = serializers.ListField(required=False)
    top_products = serializers.ListField(required=False)
    daily_sales_trend = serializers.ListField(required=False)
    
    # Inventory KPIs
    total_products = serializers.IntegerField(required=False)
    total_stock_value = serializers.IntegerField(required=False)
    low_stock_count = serializers.IntegerField(required=False)
    products_by_category = serializers.ListField(required=False)
    low_stock_products = serializers.ListField(required=False)
    recent_movements = serializers.ListField(required=False)
    
    # User KPIs
    total_users = serializers.IntegerField(required=False)
    active_users = serializers.IntegerField(required=False)
    new_users = serializers.IntegerField(required=False)
    users_by_role = serializers.ListField(required=False)
    recent_users = serializers.ListField(required=False)
    
    # Financial KPIs
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    total_transactions = serializers.IntegerField(required=False)
    monthly_revenue_trend = serializers.ListField(required=False)
    
    # Meta fields
    period_start = serializers.DateTimeField(required=False)
    period_end = serializers.DateTimeField(required=False)
    generated_at = serializers.DateTimeField(required=False)


class ComprehensiveDashboardSerializer(serializers.Serializer):
    """
    Serializer for comprehensive dashboard data
    """
    sales_kpis = DashboardKPISerializer(required=False)
    inventory_kpis = DashboardKPISerializer(required=False)
    user_kpis = DashboardKPISerializer(required=False)
    financial_kpis = DashboardKPISerializer(required=False)
    generated_at = serializers.DateTimeField()


class AlertActionSerializer(serializers.Serializer):
    """
    Serializer for alert actions (acknowledge, resolve)
    """
    action = serializers.ChoiceField(choices=['acknowledge', 'resolve'])
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)


class DashboardFilterSerializer(serializers.Serializer):
    """
    Serializer for dashboard filter parameters
    """
    period_start = serializers.DateTimeField(required=False)
    period_end = serializers.DateTimeField(required=False)
    metric_type = serializers.ChoiceField(
        choices=Metric.METRIC_TYPES,
        required=False
    )
    period_type = serializers.ChoiceField(
        choices=Metric.PERIOD_TYPES,
        required=False
    )
from django.db.models import Sum, Count, Avg, Q, F
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional

from sales.models import Ventas
from inventory.models import GPS, SIMCard, Otros
from authentication.models import CustomUser
from .models import Metric, Alert


class DashboardService:
    """
    Service class for calculating KPIs and dashboard metrics
    """
    
    @staticmethod
    def get_sales_kpis(period_start: datetime = None, period_end: datetime = None) -> Dict[str, Any]:
        """
        Calculate sales-related KPIs for the specified period
        """
        if not period_start:
            period_start = timezone.now() - timedelta(days=30)
        if not period_end:
            period_end = timezone.now()
        
        sales_queryset = Ventas.objects.filter(
            created_at__range=[period_start, period_end]
        )
        
        # Basic sales metrics
        total_sales = sales_queryset.aggregate(
            total_amount=Sum('total'),
            total_count=Count('id'),
            average_sale=Avg('total')
        )
        
        # Sales by status
        sales_by_status = sales_queryset.values('estado').annotate(
            count=Count('id'),
            total=Sum('total')
        )
        
        # Sales by month
        sales_by_month = sales_queryset.values('mes').annotate(
            count=Count('id'),
            total=Sum('total')
        ).order_by('-total')[:12]
        
        # Daily sales trend
        daily_sales = sales_queryset.extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            total=Sum('total'),
            count=Count('id')
        ).order_by('day')
        
        return {
            'total_sales_amount': total_sales['total_amount'] or Decimal('0.00'),
            'total_sales_count': total_sales['total_count'] or 0,
            'average_sale_amount': total_sales['average_sale'] or Decimal('0.00'),
            'sales_by_status': list(sales_by_status),
            'sales_by_month': list(sales_by_month),
            'daily_sales_trend': list(daily_sales),
            'period_start': period_start,
            'period_end': period_end
        }
    
    @staticmethod
    def get_inventory_kpis() -> Dict[str, Any]:
        """
        Calculate inventory-related KPIs
        """
        # GPS devices metrics
        gps_stats = GPS.objects.aggregate(
            total_gps=Count('id'),
            available_gps=Count('id', filter=Q(estado='no_asignado')),
            assigned_gps=Count('id', filter=Q(estado='asignado'))
        )
        
        # SIM cards metrics
        sim_stats = SIMCard.objects.aggregate(
            total_sims=Count('id'),
            available_sims=Count('id', filter=Q(estado='no_asignado')),
            assigned_sims=Count('id', filter=Q(estado='asignado'))
        )
        
        # Other products metrics
        otros_stats = Otros.objects.aggregate(
            total_otros=Count('id'),
            low_stock_count=Count('id', filter=Q(stock_actual__lte=models.F('stock_minimo'))),
            total_stock_value=Sum('precio_total')
        )
        
        # Low stock products
        low_stock_products = Otros.objects.filter(
            stock_actual__lte=F('stock_minimo')
        ).values(
            'descripcion', 'stock_actual', 'stock_minimo', 'categoria'
        ).order_by('stock_actual')[:10]
        
        return {
            'gps_devices': {
                'total': gps_stats['total_gps'] or 0,
                'available': gps_stats['available_gps'] or 0,
                'assigned': gps_stats['assigned_gps'] or 0
            },
            'sim_cards': {
                'total': sim_stats['total_sims'] or 0,
                'available': sim_stats['available_sims'] or 0,
                'assigned': sim_stats['assigned_sims'] or 0
            },
            'other_products': {
                'total': otros_stats['total_otros'] or 0,
                'low_stock_count': otros_stats['low_stock_count'] or 0,
                'total_value': otros_stats['total_stock_value'] or Decimal('0.00')
            },
            'low_stock_products': list(low_stock_products)
        }
    
    @staticmethod
    def get_user_kpis(period_start: datetime = None, period_end: datetime = None) -> Dict[str, Any]:
        """
        Calculate user-related KPIs
        """
        if not period_start:
            period_start = timezone.now() - timedelta(days=30)
        if not period_end:
            period_end = timezone.now()
        
        # User statistics
        user_stats = CustomUser.objects.aggregate(
            total_users=Count('id'),
            active_users=Count('id', filter=Q(is_active=True)),
            new_users=Count('id', filter=Q(date_joined__range=[period_start, period_end]))
        )
        
        # Users by role
        users_by_role = CustomUser.objects.values(
            'rol'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Recent user registrations
        recent_users = CustomUser.objects.filter(
            date_joined__range=[period_start, period_end]
        ).values(
            'email', 'first_name', 'last_name', 'date_joined', 'rol'
        ).order_by('-date_joined')[:10]
        
        return {
            'total_users': user_stats['total_users'] or 0,
            'active_users': user_stats['active_users'] or 0,
            'new_users_this_period': user_stats['new_users'] or 0,
            'users_by_role': list(users_by_role),
            'recent_users': list(recent_users),
            'period_start': period_start,
            'period_end': period_end
        }
    
    @staticmethod
    def get_financial_kpis(period_start: datetime = None, period_end: datetime = None) -> Dict[str, Any]:
        """
        Calculate financial KPIs
        """
        if not period_start:
            period_start = timezone.now() - timedelta(days=30)
        if not period_end:
            period_end = timezone.now()
        
        # Revenue metrics
        revenue_stats = Ventas.objects.filter(
            created_at__range=[period_start, period_end],
            is_active=True
        ).aggregate(
            total_revenue=Sum('total'),
            total_tax=Sum('igv'),
            net_revenue=Sum('importe')
        )
        
        # Monthly revenue trend (last 12 months)
        twelve_months_ago = timezone.now() - timedelta(days=365)
        monthly_revenue = Ventas.objects.filter(
            is_active=True,
            created_at__gte=twelve_months_ago
        ).extra(
            select={'month': "strftime('%%Y-%%m', created_at)"}
        ).values('month').annotate(
            revenue=Sum('total'),
            transactions=Count('id')
        ).order_by('month')
        
        return {
            'total_revenue': revenue_stats['total_revenue'] or Decimal('0.00'),
            'total_tax': revenue_stats['total_tax'] or Decimal('0.00'),
            'net_revenue': revenue_stats['net_revenue'] or Decimal('0.00'),
            'monthly_revenue_trend': list(monthly_revenue),
            'period_start': period_start,
            'period_end': period_end
        }
    
    @staticmethod
    def get_comprehensive_dashboard(period_start: datetime = None, period_end: datetime = None) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data combining all KPIs
        """
        return {
            'sales_kpis': DashboardService.get_sales_kpis(period_start, period_end),
            'inventory_kpis': DashboardService.get_inventory_kpis(),
            'user_kpis': DashboardService.get_user_kpis(period_start, period_end),
            'financial_kpis': DashboardService.get_financial_kpis(period_start, period_end),
            'generated_at': timezone.now()
        }
    
    @staticmethod
    def save_metrics_to_db(metrics_data: Dict[str, Any], period_type: str = 'daily', created_by=None) -> List[Metric]:
        """
        Save calculated metrics to the database
        """
        saved_metrics = []
        period_start = metrics_data.get('period_start', timezone.now() - timedelta(days=1))
        period_end = metrics_data.get('period_end', timezone.now())
        
        # Sales metrics
        sales_kpis = metrics_data.get('sales_kpis', {})
        if sales_kpis:
            metric = Metric.objects.create(
                name='Total Sales Amount',
                metric_type='sales',
                value=sales_kpis.get('total_sales_amount', 0),
                period_type=period_type,
                period_start=period_start,
                period_end=period_end,
                created_by=created_by,
                metadata={'sales_count': sales_kpis.get('total_sales_count', 0)}
            )
            saved_metrics.append(metric)
        
        # Inventory metrics
        inventory_kpis = metrics_data.get('inventory_kpis', {})
        if inventory_kpis:
            metric = Metric.objects.create(
                name='Total Products',
                metric_type='inventory',
                value=inventory_kpis.get('total_products', 0),
                period_type=period_type,
                period_start=period_start,
                period_end=period_end,
                created_by=created_by,
                metadata={'low_stock_count': inventory_kpis.get('low_stock_count', 0)}
            )
            saved_metrics.append(metric)
        
        # User metrics
        user_kpis = metrics_data.get('user_kpis', {})
        if user_kpis:
            metric = Metric.objects.create(
                name='Active Users',
                metric_type='users',
                value=user_kpis.get('active_users', 0),
                period_type=period_type,
                period_start=period_start,
                period_end=period_end,
                created_by=created_by,
                metadata={'new_users': user_kpis.get('new_users', 0)}
            )
            saved_metrics.append(metric)
        
        return saved_metrics


class AlertService:
    """
    Service class for managing alerts and notifications
    """
    
    @staticmethod
    def check_low_stock_alerts() -> List[Alert]:
        """
        Check for products with low stock and create alerts
        """
        alerts = []
        low_stock_products = Otros.objects.filter(
            stock_actual__lte=models.F('stock_minimo')
        )
        
        for product in low_stock_products:
            # Check if alert already exists for this product
            existing_alert = Alert.objects.filter(
                alert_type='low_stock',
                status='active',
                metadata__product_id=product.id
            ).first()
            
            if not existing_alert:
                severity = 'medium' if product.stock_actual > 5 else 'high'
                
                alert = Alert.objects.create(
                    title=f'Stock Bajo: {product.descripcion}',
                    message=f'El producto {product.descripcion} tiene solo {product.stock_actual} unidades en stock (mínimo: {product.stock_minimo}).',
                    alert_type='low_stock',
                    severity=severity,
                    threshold_value=Decimal(str(product.stock_minimo)),
                    current_value=Decimal(str(product.stock_actual)),
                    metadata={'product_id': product.id, 'product_name': product.descripcion}
                )
                alerts.append(alert)
        
        return alerts
    
    @staticmethod
    def check_high_sales_alerts(threshold: Decimal = Decimal('10000.00')) -> List[Alert]:
        """
        Check for unusually high sales and create alerts
        """
        alerts = []
        now = timezone.now()
        today = now.date()
        
        # Crear rango de fechas para el día actual en UTC
        from datetime import timezone as dt_timezone
        start_of_day = datetime.combine(today, datetime.min.time()).replace(tzinfo=dt_timezone.utc)
        end_of_day = datetime.combine(today, datetime.max.time()).replace(tzinfo=dt_timezone.utc)
        
        daily_sales = Ventas.objects.filter(
            created_at__gte=start_of_day,
            created_at__lte=end_of_day,
            is_active=True
        ).aggregate(total=Sum('total'))
        
        total_sales = daily_sales['total'] or Decimal('0.00')
        
        if total_sales > threshold:
            # Check if alert already exists for today
            existing_alert = Alert.objects.filter(
                alert_type='high_sales',
                status='active',
                created_at__gte=start_of_day,
                created_at__lte=end_of_day
            ).first()
            
            if not existing_alert:
                alert = Alert.objects.create(
                    title='Ventas Altas Detectadas',
                    message=f'Las ventas de hoy han alcanzado ${total_sales}, superando el umbral de ${threshold}.',
                    alert_type='high_sales',
                    severity='high',
                    threshold_value=threshold,
                    current_value=total_sales,
                    metadata={'date': str(today), 'sales_count': Ventas.objects.filter(created_at__date=today).count()}
                )
                alerts.append(alert)
        
        return alerts
    
    @staticmethod
    def get_active_alerts() -> List[Alert]:
        """
        Get all active alerts
        """
        return Alert.objects.filter(status='active').order_by('-created_at')
    
    @staticmethod
    def acknowledge_alert(alert_id: int, user) -> Optional[Alert]:
        """
        Acknowledge an alert
        """
        try:
            alert = Alert.objects.get(id=alert_id, status='active')
            alert.status = 'acknowledged'
            alert.acknowledged_at = timezone.now()
            alert.acknowledged_by = user
            alert.save()
            return alert
        except Alert.DoesNotExist:
            return None
    
    @staticmethod
    def resolve_alert(alert_id: int, user) -> Optional[Alert]:
        """
        Resolve an alert
        """
        try:
            alert = Alert.objects.get(id=alert_id)
            alert.status = 'resolved'
            alert.resolved_at = timezone.now()
            alert.save()
            return alert
        except Alert.DoesNotExist:
            return None
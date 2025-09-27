from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardViewSet, MetricViewSet, AlertViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'overview', DashboardViewSet, basename='dashboard')
router.register(r'metrics', MetricViewSet, basename='metric')
router.register(r'alerts', AlertViewSet, basename='alert')

app_name = 'dashboard'

urlpatterns = [
    # Dashboard API endpoints
    path('', include(router.urls)),
    
    # Additional custom endpoints can be added here if needed
]

# Available endpoints:
# GET /api/dashboard/ - Dashboard overview
# GET /api/dashboard/overview/ - Comprehensive dashboard data
# GET /api/dashboard/overview/sales_kpis/ - Sales KPIs
# GET /api/dashboard/overview/inventory_kpis/ - Inventory KPIs
# GET /api/dashboard/overview/user_kpis/ - User KPIs
# GET /api/dashboard/overview/financial_kpis/ - Financial KPIs
#
# GET /api/dashboard/metrics/ - List all metrics
# POST /api/dashboard/metrics/ - Create new metric
# GET /api/dashboard/metrics/{id}/ - Get specific metric
# PUT /api/dashboard/metrics/{id}/ - Update metric
# DELETE /api/dashboard/metrics/{id}/ - Delete metric
# GET /api/dashboard/metrics/by_type/ - Get metrics by type
#
# GET /api/dashboard/alerts/ - List all alerts
# POST /api/dashboard/alerts/ - Create new alert
# GET /api/dashboard/alerts/{id}/ - Get specific alert
# PUT /api/dashboard/alerts/{id}/ - Update alert
# DELETE /api/dashboard/alerts/{id}/ - Delete alert
# GET /api/dashboard/alerts/active/ - Get active alerts
# POST /api/dashboard/alerts/{id}/action_alert/ - Acknowledge/resolve alert
# POST /api/dashboard/alerts/check_alerts/ - Trigger alert checking
# GET /api/dashboard/alerts/statistics/ - Get alert statistics
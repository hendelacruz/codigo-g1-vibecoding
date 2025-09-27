"""
Django management command to generate and store metrics
"""
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime, timedelta
import sys
from dashboard.services import DashboardService
from dashboard.models import Metric


class Command(BaseCommand):
    """
    Management command to generate and store metrics
    This can be run via cron job for daily/weekly/monthly metrics
    """
    help = 'Generate and store dashboard metrics'

    def add_arguments(self, parser):
        """Add command line arguments"""
        parser.add_argument(
            '--period',
            type=str,
            choices=['daily', 'weekly', 'monthly'],
            default='daily',
            help='Period for metrics generation (default: daily)'
        )
        
        parser.add_argument(
            '--date',
            type=str,
            help='Specific date for metrics (YYYY-MM-DD format, default: yesterday)'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output'
        )

    def handle(self, *args, **options):
        """Execute the command"""
        period = options['period']
        date_str = options['date']
        verbose = options['verbose']
        
        # Parse date
        if date_str:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                self.stderr.write('Invalid date format. Use YYYY-MM-DD')
                sys.exit(1)
        else:
            # Default to yesterday
            target_date = (timezone.now() - timedelta(days=1)).date()
        
        if verbose:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Generating {period} metrics for {target_date}'
                )
            )
        
        try:
            metrics_created = 0
            
            # Calculate period dates
            if period == 'daily':
                period_start = datetime.combine(target_date, datetime.min.time())
                period_end = datetime.combine(target_date, datetime.max.time())
            elif period == 'weekly':
                # Start of week (Monday)
                days_since_monday = target_date.weekday()
                week_start = target_date - timedelta(days=days_since_monday)
                period_start = datetime.combine(week_start, datetime.min.time())
                period_end = datetime.combine(
                    week_start + timedelta(days=6), datetime.max.time()
                )
            else:  # monthly
                period_start = datetime.combine(
                    target_date.replace(day=1), datetime.min.time()
                )
                # Last day of month
                if target_date.month == 12:
                    next_month = target_date.replace(year=target_date.year + 1, month=1)
                else:
                    next_month = target_date.replace(month=target_date.month + 1)
                period_end = datetime.combine(
                    next_month - timedelta(days=1), datetime.max.time()
                )
            
            # Make timezone aware
            period_start = timezone.make_aware(period_start)
            period_end = timezone.make_aware(period_end)
            
            # Generate sales metrics
            sales_kpis = DashboardService.get_sales_kpis(
                period_start, period_end
            )
            
            for key, value in sales_kpis.items():
                if isinstance(value, (int, float)):
                    metric, created = Metric.objects.get_or_create(
                        name=f'sales_{key}',
                        metric_type='sales',
                        period_type=period,
                        period_start=period_start,
                        period_end=period_end,
                        defaults={
                            'value': value,
                            'description': f'Sales {key} for {period} period'
                        }
                    )
                    if created:
                        metrics_created += 1
                        if verbose:
                            self.stdout.write(f'Created metric: sales_{key} = {value}')
            
            # Generate inventory metrics
            inventory_kpis = DashboardService.get_inventory_kpis()
            
            for key, value in inventory_kpis.items():
                if isinstance(value, (int, float)):
                    metric, created = Metric.objects.get_or_create(
                        name=f'inventory_{key}',
                        metric_type='inventory',
                        period_type=period,
                        period_start=period_start,
                        period_end=period_end,
                        defaults={
                            'value': value,
                            'description': f'Inventory {key} for {period} period'
                        }
                    )
                    if created:
                        metrics_created += 1
                        if verbose:
                            self.stdout.write(f'Created metric: inventory_{key} = {value}')
            
            # Generate financial metrics
            financial_kpis = DashboardService.get_financial_kpis(
                period_start, period_end
            )
            
            for key, value in financial_kpis.items():
                if isinstance(value, (int, float)):
                    metric, created = Metric.objects.get_or_create(
                        name=f'financial_{key}',
                        metric_type='financial',
                        period_type=period,
                        period_start=period_start,
                        period_end=period_end,
                        defaults={
                            'value': value,
                            'description': f'Financial {key} for {period} period'
                        }
                    )
                    if created:
                        metrics_created += 1
                        if verbose:
                            self.stdout.write(f'Created metric: financial_{key} = {value}')
            
            # Success message
            self.stdout.write(
                self.style.SUCCESS(
                    f'Metrics generation completed. Created {metrics_created} new metrics.'
                )
            )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during metrics generation: {str(e)}')
            )
            raise
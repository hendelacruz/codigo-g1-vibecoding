"""
Django management command to check and create automatic alerts
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.services import AlertService


class Command(BaseCommand):
    """
    Management command to check for alerts automatically
    This can be run via cron job or scheduled task
    """
    help = 'Check for automatic alerts (low stock, high sales, etc.)'

    def add_arguments(self, parser):
        """Add command line arguments"""
        parser.add_argument(
            '--alert-type',
            type=str,
            choices=['low_stock', 'high_sales', 'all'],
            default='all',
            help='Type of alerts to check (default: all)'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output'
        )

    def handle(self, *args, **options):
        """Execute the command"""
        alert_type = options['alert_type']
        verbose = options['verbose']
        
        if verbose:
            self.stdout.write(
                self.style.SUCCESS(f'Starting alert check at {timezone.now()}')
            )
        
        total_alerts = 0
        
        try:
            if alert_type in ['low_stock', 'all']:
                if verbose:
                    self.stdout.write('Checking for low stock alerts...')
                
                low_stock_alerts = AlertService.check_low_stock_alerts()
                total_alerts += len(low_stock_alerts)
                
                if verbose:
                    self.stdout.write(
                        f'Created {len(low_stock_alerts)} low stock alerts'
                    )
            
            if alert_type in ['high_sales', 'all']:
                if verbose:
                    self.stdout.write('Checking for high sales alerts...')
                
                high_sales_alerts = AlertService.check_high_sales_alerts()
                total_alerts += len(high_sales_alerts)
                
                if verbose:
                    self.stdout.write(
                        f'Created {len(high_sales_alerts)} high sales alerts'
                    )
            
            # Success message
            if verbose or total_alerts > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Alert check completed. Created {total_alerts} new alerts.'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during alert check: {str(e)}')
            )
            raise
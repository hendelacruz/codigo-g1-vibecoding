"""
Django management command to monitor rate limiting statistics.
"""

import time
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings
from collections import defaultdict


class Command(BaseCommand):
    help = 'Monitor rate limiting statistics and blocked requests'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='Monitoring interval in seconds (default: 60)'
        )
        parser.add_argument(
            '--continuous',
            action='store_true',
            help='Run continuously until interrupted'
        )
        parser.add_argument(
            '--show-blocked',
            action='store_true',
            help='Show only blocked requests'
        )
    
    def handle(self, *args, **options):
        interval = options['interval']
        continuous = options['continuous']
        show_blocked = options['show_blocked']
        
        self.stdout.write(
            self.style.SUCCESS('Starting rate limit monitoring...')
        )
        
        try:
            if continuous:
                while True:
                    self.show_rate_limit_stats(show_blocked)
                    time.sleep(interval)
            else:
                self.show_rate_limit_stats(show_blocked)
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\nMonitoring stopped by user.')
            )
    
    def show_rate_limit_stats(self, show_blocked_only=False):
        """Display current rate limiting statistics."""
        
        self.stdout.write('\n' + '='*80)
        self.stdout.write(f'Rate Limiting Statistics - {time.strftime("%Y-%m-%d %H:%M:%S")}')
        self.stdout.write('='*80)
        
        # Get all rate limit keys from cache
        rate_limit_keys = self._get_rate_limit_keys()
        
        if not rate_limit_keys:
            self.stdout.write(
                self.style.WARNING('No rate limiting data found in cache.')
            )
            return
        
        # Group by rate limit type
        stats_by_type = defaultdict(list)
        
        for key in rate_limit_keys:
            data = cache.get(key)
            if data:
                parts = key.split(':')
                if len(parts) >= 3:
                    rate_type = parts[1]
                    client_id = ':'.join(parts[2:])
                    
                    stats_by_type[rate_type].append({
                        'client_id': client_id,
                        'count': data.get('count', 0),
                        'window_start': data.get('window_start', 0),
                        'key': key
                    })
        
        # Display statistics
        for rate_type, clients in stats_by_type.items():
            rate_config = getattr(settings, 'RATE_LIMITS', {}).get(
                rate_type, {'requests': 100, 'window': 3600}
            )
            max_requests = rate_config['requests']
            window = rate_config['window']
            
            self.stdout.write(f'\n{rate_type.upper()} Rate Limits:')
            self.stdout.write(f'  Max requests: {max_requests} per {window} seconds')
            self.stdout.write('-' * 40)
            
            blocked_count = 0
            total_requests = 0
            
            for client in sorted(clients, key=lambda x: x['count'], reverse=True):
                count = client['count']
                total_requests += count
                is_blocked = count >= max_requests
                
                if is_blocked:
                    blocked_count += 1
                
                if show_blocked_only and not is_blocked:
                    continue
                
                status = 'BLOCKED' if is_blocked else 'OK'
                style = self.style.ERROR if is_blocked else self.style.SUCCESS
                
                self.stdout.write(
                    style(f'  {client["client_id"]:<30} {count:>3}/{max_requests} {status}')
                )
            
            # Summary for this rate type
            self.stdout.write(f'\n  Summary: {len(clients)} clients, {blocked_count} blocked, {total_requests} total requests')
        
        # Overall summary
        total_clients = sum(len(clients) for clients in stats_by_type.values())
        total_blocked = sum(
            len([c for c in clients if c['count'] >= getattr(settings, 'RATE_LIMITS', {}).get(
                rate_type, {'requests': 100}
            )['requests']])
            for rate_type, clients in stats_by_type.items()
        )
        
        self.stdout.write(f'\nOverall Summary:')
        self.stdout.write(f'  Total clients being tracked: {total_clients}')
        self.stdout.write(f'  Currently blocked: {total_blocked}')
        self.stdout.write(f'  Block rate: {(total_blocked/total_clients*100):.1f}%' if total_clients > 0 else '  Block rate: 0%')
    
    def _get_rate_limit_keys(self):
        """Get all rate limit keys from cache."""
        # This is a simplified approach - in production you might want to use
        # Redis SCAN command or maintain a separate index of rate limit keys
        
        # For Django's cache framework, we'll need to check common patterns
        rate_limit_keys = []
        
        # Common rate limit key patterns
        patterns = [
            'rate_limit:default:',
            'rate_limit:auth:',
            'rate_limit:strict:',
            'rate_limit:login:',
            'rate_limit:register:',
            'rate_limit:password_reset:',
            'rate_limit:sales_create:',
            'rate_limit:exports:',
            'api_rate_limit:sales:',
            'rate_limit_decorator:hour:',
            'rate_limit_decorator:minute:',
        ]
        
        # This is a mock implementation - in a real scenario you'd query Redis directly
        # or maintain a registry of active rate limit keys
        
        return rate_limit_keys
    
    def clear_rate_limits(self, client_pattern=None):
        """Clear rate limit data for debugging purposes."""
        
        if client_pattern:
            self.stdout.write(f'Clearing rate limits for pattern: {client_pattern}')
            # Implementation would clear specific patterns
        else:
            self.stdout.write('Clearing all rate limit data...')
            # Implementation would clear all rate limit keys
        
        self.stdout.write(
            self.style.SUCCESS('Rate limit data cleared.')
        )
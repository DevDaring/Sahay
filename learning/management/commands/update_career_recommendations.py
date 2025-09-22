#!/usr/bin/env python3
"""
Django management command to update career recommendations
"""

from django.core.management.base import BaseCommand
from services.career_monitoring_service import CareerMonitoringService


class Command(BaseCommand):
    help = 'Update career recommendations for all students and courses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update all recommendations regardless of last update time',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting career recommendations update...')
        )
        
        try:
            service = CareerMonitoringService()
            
            if options['force']:
                self.stdout.write('Force update mode enabled')
                # TODO: Add force update logic if needed
            
            service.monitor_and_update()
            
            self.stdout.write(
                self.style.SUCCESS('Career recommendations update completed successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating career recommendations: {e}')
            )
            raise

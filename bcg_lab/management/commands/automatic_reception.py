# -*- coding: utf8 -*-
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from order.models import Order


class Command(BaseCommand):
    can_import_settings = True
    help = 'Send alerts for order having a non changed status for 21 days and 31 days'
    
    def handle(self, *args, **options):
        verbose = options.get('verbosity', 0)
        
        orders = Order.objects.filter(
            status = 4,
            provider__direct_reception = True, 
            last_change__lte = timezone.now() - timedelta(days = 7)
        )
        
        for order in orders:
            print(u"Commande %s receptionnee et archivee." % ( order.number ))
            order.save_to_history()
            order.delete()

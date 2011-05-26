# -*- encoding: utf8 -*-
from datetime import datetime, date
from django.db import models
from order.models import OrderItem

class History(models.Model):
  """
  History should be completely independant from any other table so 
  that when a deletion is made in the DB, it won't affect the history
  """
  team         = models.CharField(u"Equipe", max_length=100)
  user         = models.CharField(u"Utilisateur", max_length=100)
  provider     = models.CharField(u"Fournisseur", max_length=100)
  number       = models.CharField(u"N° cde", max_length = 100, null = True, blank = True)
  price        = models.DecimalField(u"Prix total", max_digits=12, decimal_places=2)
  budget       = models.CharField(u"Ligne budgétaire", max_length = 100)
  date_created = models.DateField(u"Date", default=date.today())
  items        = models.ManyToManyField( OrderItem, verbose_name = "Produits" )
  
  class Meta:
    verbose_name = "Historique"
    verbose_name_plural = "Historique"
    ordering = ('date_created',)
  
  def __unicode__(self):
    d = datetime.strftime( self.date_created, "%d/%m/%Y %Hh%M" )
    return u"%s - %s" % ( self.provider, d )
  
  @models.permalink
  def get_absolute_url(self):
    return ( 'history_detail', [self.id] )
  

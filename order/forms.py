# coding: utf-8
from decimal import Decimal, InvalidOperation

from django import forms
from django.forms import widgets
from django.urls import reverse_lazy

from bcg_lab.constants import CREDIT, DEBIT
from order.models import OrderItem, OrderComplement
from team.models import Team
from provider.models import Provider
from product.models import ProductCode


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        exclude = ('product_id', 'cost_type')
        widgets = {
            'nomenclature': widgets.TextInput(attrs={
                'class': 'autocomplete', 
                'autocomplete_url': reverse_lazy('product_code:autocomplete')
            })
        }
    
    def clean_nomenclature(self):
        nomenclature = self.cleaned_data.get('nomenclature', None)
        if not nomenclature:
            return None
        
        product_code = nomenclature.split(' - ')[0]
        if ProductCode.objects.filter( code = product_code ).count() == 0:
            raise forms.ValidationError(u"Cette nomenclature (%s) n'est pas reconnue." % product_code)

        return product_code


class AddCreditForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ["name", "reference", "offer_nb", "price", "quantity", "cost_type"]
        widgets = {
            'cost_type': widgets.HiddenInput(attrs = {'value': CREDIT})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget = forms.TextInput(attrs = {
            'class': 'autocomplete',
            'choices': ";".join([c.name for c in OrderComplement.objects.filter(type_comp = CREDIT)])
        })

    def clean_price(self):
        price = self.cleaned_data.get('price', None)
        try:
            price = Decimal(price.replace(',','.'))
        except InvalidOperation:
            raise forms.ValidationError(u"Veuillez saisir un montant positif.")
        
        if price <= 0:
            raise forms.ValidationError(u"Veuillez saisir un montant positif.")
        
        return price
    

class AddDebitForm(forms.ModelForm):
    price = forms.CharField( label = u"Montant" )
    
    class Meta:
        model = OrderItem
        fields = ("name", "reference", "offer_nb", "price", "quantity", "cost_type")
        widgets = {
            'cost_type': widgets.HiddenInput(attrs = {'value': DEBIT})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget = forms.TextInput(attrs = {
            'class': 'autocomplete',
            'choices': ";".join([c.name for c in OrderComplement.objects.filter(type_comp = DEBIT)])
        })

    def clean_price(self):
        price = self.cleaned_data.get('price', None)
        try:
            price = Decimal(price.replace(',','.'))
        except InvalidOperation:
            raise forms.ValidationError(u"Veuillez saisir un montant positif.")
        
        if price <= 0:
            raise forms.ValidationError(u"Veuillez saisir un montant positif.")
        
        return price
    

class FilterForm(forms.Form):
    connector = forms.TypedChoiceField(
        choices = [("AND",u"toutes les"), ("OR", u"l'une des")],
        initial = "AND",
        coerce = str,
        empty_value = None,
        required = True
    )

    team = forms.ModelChoiceField(
        queryset = Team.objects.all(),
        label    = "Equipe",
        required = False
    )
    
    number = forms.CharField(
        label    = u"N°cmde",
        widget   = widgets.TextInput( attrs = { 
            'class' : 'autocomplete', 
            'autocomplete_url': reverse_lazy('order:autocomplete_number')
        }),
        required = False
    )
    
    provider = forms.ModelChoiceField(
        queryset = Provider.objects.exclude( is_local = True ),
        label    = "Fournisseur",
        required = False
    )
    notes__icontains = forms.CharField(
        label    = u"Commentaire",
        required = False
    )
    
    items__name__icontains = forms.CharField(
        label    = u"Produit",
        widget   = widgets.TextInput( attrs = { 
            'class' : 'autocomplete', 
            'autocomplete_url': reverse_lazy('product:autocomplete')
        }),
        required = False
    )


class ServiceForm(forms.Form):
    team = forms.ModelChoiceField(
        label = u"Equipe",
        queryset = Team.objects.all()
    )
    provider = forms.ModelChoiceField(
        label = u"Type de service", 
        queryset = Provider.objects.filter(is_service = True),
        required = True
    )
    name         = forms.CharField( label = u"Désignation" )
    nomenclature = forms.CharField(
        label    = u"Nomenclature",
        required = False,
        widget   = widgets.TextInput( attrs = { 
            'class' : 'autocomplete', 
            'autocomplete_url': reverse_lazy('product_code:autocomplete')
        }),
    )
    cost         = forms.CharField( label = u"Montant" )
    quantity     = forms.IntegerField( label = u"Quantité", initial = 1 )
    confidential = forms.BooleanField( label = u"Confidentiel ?", initial = False, required = False )
    
    def __init__(self, member, *args, **kwargs):
        super( ServiceForm, self ).__init__( *args, **kwargs )
        
        if not member.user.has_perm("order.custom_order_any_team"):
            self.fields['team'].initial = member.team
            self.fields['team'].widget.attrs.update({ 'disabled': 'disabled' })
    
    def clean_cost(self):
        cost = self.cleaned_data.get('cost', None)
        try:
            cost = Decimal(cost.replace(',','.'))
        except InvalidOperation:
            raise forms.ValidationError(u"Veuillez saisir un montant positif.")
        
        if cost <= 0:
            raise forms.ValidationError(u"Veuillez saisir un montant positif.")
        
        return cost
    
    def clean_nomenclature(self):
        nomenclature = self.cleaned_data.get('nomenclature', None)
        if not nomenclature:
            return None
        
        product_code = nomenclature.split(' - ')[0]
        if ProductCode.objects.filter( code = product_code ).count() == 0:
            raise forms.ValidationError(u"Cette nomenclature (%s) n'est pas reconnue." % product_code)
        
        return product_code

# coding: utf-8
from datetime import date
from decimal import Decimal

from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.simple import direct_to_template

from order.models import Order
from budget.models import Budget, BudgetLine
from budget.forms import BudgetForm, CreditBudgetForm, DebitBudgetForm
from budget.forms import TransferForm, BudgetLineForm

from utils import *

@login_required
@transaction.commit_on_success
def index_budget(request):
	if request.method == "GET":		return _budget_list(request)
	if request.method == "POST":	return _budget_creation(request)
	return redirect('error')

@login_required
@transaction.commit_on_success
def index_budgetline(request):
	if request.method == "GET":		return _budgetline_list(request)
	if request.method == "POST":	return _budgetline_creation(request)
	return redirect('error')

@login_required
@transaction.commit_on_success
def item_budget(request, budget_id):
	budget = get_object_or_404( Budget, id = budget_id )
	if request.method == 'GET':		return _budget_detail( request, budget )
	if request.method == 'POST':	return _budget_update( request, budget )
	return redirect('error')

@login_required
@GET_method
def new_budget(request):
	return direct_to_template(request, 'budget/form.html',{
		'form': BudgetForm()
	})


@login_required
@transaction.commit_on_success
def credit_budget(request, budget_id):
	budget = get_object_or_404( Budget, id = budget_id )
	
	if request.method == "GET":
		return direct_to_template(request, "budget/form_credit.html",{
			'budget': budget,
			'form': CreditBudgetForm( budget )
		})
	
	if request.method == 'POST':
		data = request.POST.copy()
		data.update({ 'budget': budget.name }) # otherwise, form is not valid
		
		form = CreditBudgetForm( budget, data = data )
		
		if form.is_valid():
			bl = form.save( commit = False )
			bl.team					= budget.team.name
			bl.budget_id		= budget.id
			bl.nature				= budget.default_nature
			bl.budget_type	= budget.budget_type
			bl.origin				= budget.default_origin
			bl.quantity			= 1
			bl.credit				= bl.product_price
			bl.debit				= 0
			bl.save()
			
			info_msg(request, "Ligne de crédit ajoutée avec succès!")
			return redirect( reverse('budgetlines') + "?budget_name=%s" % budget.name )
		else:
			return direct_to_template(request, 'budget/form_credit.html',{
				'budget': budget,
				'form': form
			})

@login_required
@transaction.commit_on_success
def debit_budget(request, budget_id):
	budget = get_object_or_404( Budget, id = budget_id )
	
	if request.method == "GET":
		return direct_to_template(request, "budget/form_debit.html",{
			'budget': budget,
			'form': DebitBudgetForm( budget )
		})
	
	data = request.POST.copy()
	data.update({ 'budget': budget.name }) # otherwise, form is not valid
	
	form = DebitBudgetForm( budget, data = data )
	if form.is_valid():
		bl = form.save( commit = False )
		bl.team					= budget.team.name
		bl.budget_id		= budget.id
		bl.nature				= budget.default_nature
		bl.budget_type	= budget.budget_type
		bl.origin				= budget.default_origin
		bl.quantity			= 1
		bl.credit				= 0
		bl.debit				= bl.product_price
		bl.save()
		
		info_msg(request, "Ligne de débit ajoutée avec succès!")
		return redirect( reverse('budgetlines') + "?budget_name=%s" % budget.name )
	else:
		return direct_to_template(request, 'budget/form_debit.html',{
			'budget': budget,
			'form': form
		})

@login_required
@transaction.commit_on_success
def transfer_budget(request):
	if request.method == 'GET':
		form = TransferForm()
	elif request.method == 'POST':
		form = TransferForm( data = request.POST )
		if form.is_valid():
			data = form.cleaned_data
			budget1 = data['budget1']
			budget2 = data['budget2']
			amount	= data['amount']
			
			# DEBIT BUDGET1
			BudgetLine.objects.create(
				product			= u"Virement vers %s" % budget2.name,
				team 				= budget1.team.name,
				budget_id 	= budget1.id,
				budget 			= budget1.name,
				nature 			= budget1.default_nature,
				budget_type	= budget1.budget_type,
				origin	= budget1.default_origin,
				quantity		= 1,
				debit				= amount,
				credit			= 0,
				product_price = amount
			)
			# CREDIT BUDGET2
			BudgetLine.objects.create(
				product			= u"Virement reçu de %s" % budget1.name,
				team 				= budget2.team.name,
				budget_id 	= budget2.id,
				budget 			= budget2.name,
				nature 			= budget2.default_nature,
				budget_type	= budget2.budget_type,
				origin	= budget2.default_origin,
				quantity		= 1,
				debit				= 0,
				credit			= amount,
				product_price = amount
			)
			return redirect('budgets')
			
	return direct_to_template(request, 'budget/transfer.html', {
		'form': form
	})

@login_required
@transaction.commit_on_success
def toggle_budget(request, budget_id):
	budget = get_object_or_404( Budget, id = budget_id )
	budget.is_active = not budget.is_active
	budget.save()
	
	for bl in BudgetLine.objects.filter( budget_id = budget.id ):
		bl.is_active = budget.is_active
		bl.save()
	
	return redirect('budgets')

@login_required
@GET_method
def delete_budgetline(request, bl_id):
	bl = get_object_or_404( BudgetLine, id = bl_id )
	budget_name = bl.budget
	bl.delete()
	return redirect( reverse('budgetlines') + "?budget_name=%s" % budget_name )

@login_required
@transaction.commit_on_success
def edit_budgetline(request, bl_id):
	bl = get_object_or_404( BudgetLine, id = bl_id )
	
	if request.method == 'GET':
		form = BudgetLineForm( instance = bl )
	
	elif request.method == 'POST':
		data = request.POST
		form = BudgetLineForm( instance = bl, data = data )
		if form.is_valid():
			bl = form.save( commit = False )
			
			bl.is_active = True
			if data["cost_type"] == "credit":
				bl.credit = Decimal(data["cost"])
				bl.debit = 0
				bl.product_price = bl.credit * bl.quantity
			elif data["cost_type"] == "debit":
				bl.credit = 0
				bl.debit = Decimal(data["cost"])
				bl.product_price = bl.debit * bl.quantity
			bl.save()
			return redirect( reverse('budgetlines') + "?budget_name=%s" % bl.budget )
	
	return direct_to_template( request, 'budget/budgetline_edit.html', {
		'form': form,
		'bl': bl
	})

@login_required
def history_budgetline(request):
	return direct_to_template( request, 'history/budgets.html')

# 
#		PRIVATE VIEWS
# 

@GET_method
def _budget_list(request):
	if is_secretary(request.user) or is_super_secretary(request.user) or is_super_validator(request.user):
		budget_list = Budget.objects.filter( is_active = True )
	elif is_validator(request.user):
		budget_list = Budget.objects.filter(
			is_active = True,
			team__in = get_teams(request.user)
		)
	else:
		budget_list = Budget.objects.none()
	
	return direct_to_template(request, 'tab_budgets.html',{
		'budgets': paginate( request, budget_list )
	})

@POST_method
def _budget_creation(request):
	form = BudgetForm(data = request.POST)
	
	if form.is_valid():
		budget = form.save()
		info_msg(request, "Ligne budgétaire ajoutée avec succès.")
		
		return redirect('budgets')
	else:
		return direct_to_template(request, 'budget/form.html',{
			'form': form
		})

@GET_method
def _budget_detail(request, budget):
	return direct_to_template( request, 'budget/item.html', {
		'budget': budget,
		'form': BudgetForm( instance = budget )
	})

@POST_method
def _budget_update(request, budget):
	form = BudgetForm(data = request.POST, instance = budget)
	
	if form.is_valid():
		form.save()
		info_msg(request, "Budget modifié avec succès.")
		
		return redirect('budgets')
	else:
		return direct_to_template(request, 'budget/item.html', {
			'budget': budget,
			'form': form
		})


@GET_method
def _budgetline_list(request):
	budget_lines = BudgetLine.objects.filter( is_active = True )
	
	if is_validator(request.user) and not is_admin(request.user):
		team_names = []
		for team in get_teams(request.user):
			if not team.name in team_names:
				team_names.append(team.name)
			
		budget_lines = budget_lines.filter( team__in = team_names )
	
	budget_name = request.GET.get("budget_name", None)
	if budget_name:
		budget_lines = budget_lines.filter( budget = budget_name )
		try:
			budget = Budget.objects.get( name = budget_name, is_active = True )
		except:
			budget = None
	else:
		budget = None
	
	return direct_to_template(request, "budget/budgetlines.html", {
		'budget': budget,
		'budget_lines' : paginate( request, budget_lines )
	})

# @GET_method
# def budgetline_export(request):
# 	wb = xlwt.Workbook()
# 	green = xlwt.easyxf(
# 		"""
# 		pattern:
# 			fore_color: green
# 		"""
# 	)
# 	red = xlwt.easyxf(
# 		"""
# 		pattern:
# 			fore_color: red
# 		"""
# 	)
# 	budgets = request.GET['budget_names'].split(';')
# 	for budget_name in budgets:
# 		ws = wb.add_sheet(budget_name)
# 
# 		ws.write(0,0,'BUDGET')
# 		ws.write(0,1,'N°CMDE')
# 		ws.write(0,2,'DATE')
# 		ws.write(0,3,'NATURE')
# 		ws.write(0,4,'TUTELLE')
# 		ws.write(0,5,'ORIGINE')
# 		ws.write(0,6,'FOURNISSEUR')
# 		ws.write(0,7,'OFFRE')
# 		ws.write(0,8,'DESIGNATION')
# 		ws.write(0,9,'REFERENCE')
# 		ws.write(0,10,'CREDIT')
# 		ws.write(0,11,'DEBIT')
# 		ws.write(0,12,'QUANTITE')
# 		ws.write(0,13,'TOTAL')
# 		ws.write(0,14,'MONTANT DISPO')
# 
# 		row = 1
# 		for bl in budget_lines.filter( budget = budget_name ):
# 			ws.write( row, 0, budget_name )
# 			ws.write( row, 1, bl.number )
# 			ws.write( row, 2, bl.date )
# 			ws.write( row, 3, bl.nature )
# 			ws.write( row, 4, bl.get_budget_type_display() )
# 			ws.write( row, 5, bl.origin )
# 			ws.write( row, 6, bl.provider )
# 			ws.write( row, 7, bl.offer )
# 			ws.write( row, 8, bl.product )
# 			ws.write( row, 9, bl.ref )
# 			ws.write( row, 10, bl.credit )
# 			ws.write( row, 11, bl.debit )
# 			ws.write( row, 12, bl.quantity )
# 			ws.write( row, 13, bl.product_price )
# 			ws.write( row, 14, bl.get_amount_left )
# 			row += 1
# 	
# 	response = HttpResponse(mimetype="application/ms-excel")
# 	response['Content-Disposition'] = 'attachment; filename=export.xls'
# 	wb.save(response)
# 	
# 	return response

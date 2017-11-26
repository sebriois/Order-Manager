# coding: utf8
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import redirect
from utils.request_messages import error_msg


def GET_method(view):
    """
    Decorator that checks whether the view is called using the GET method
    """
    def _wrapped_view( request, *args, **kwargs ):
        if not request.method == 'GET':
            error_msg( request, "This request method (%s) is not handled on this page" % request.method )
            return redirect( 'error' )
        return view(request, *args, **kwargs)
    
    return _wrapped_view


def POST_method(view):
    """
    Decorator that checks whether the view is called using the POST method
    """
    def _wrapped_view( request, *args, **kwargs ):
        if not request.method == 'POST':
            error_msg( request, "This request method (%s) is not handled on this page" % request.method )
            return redirect( 'error' )
        return view(request, *args, **kwargs)
    
    return _wrapped_view


def AJAX_method(view):
    """
    Decorator that checks whether the view is called using AJAX
    """
    def _wrapped_view( request, *args, **kwargs ):
        if not request.is_ajax():
            error_msg(request, 'Method %s not allowed at this URL' % request.method )
            return redirect( 'error' )
        return view(request, *args, **kwargs)
    
    return _wrapped_view
    

def superuser_required( view ):
    """
    Decorator that checks whether the user is a superuser, redirecting
    to the error page if not.
    """
    def _wrapped_view( request, *args, **kwargs ):
        if not request.user.is_superuser:
            error_msg( request, u"Vous ne pouvez pas accéder à cette page." )
            return redirect('error')
        return view(request, *args, **kwargs)
    return _wrapped_view


def paginate( request, object_list, nb_items = 40 ):
    paginator = Paginator(object_list, nb_items ) # Show nb_items per page
    
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    
    # If page request (9999) is out of range, deliver last page of results.
    try:
        return paginator.page(page)
    except (EmptyPage, InvalidPage):
        return paginator.page(paginator.num_pages)


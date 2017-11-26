# encoding: utf8
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render

from attachments.forms import AttachmentForm
from attachments.models import Attachment
from utils.request_messages import info_msg


@login_required
def new(request):
    if request.method == 'GET':
        form = AttachmentForm()
        content_type = request.GET['content_type']
        object_id = request.GET['object_id']
        next = request.GET['next']

    elif request.method == 'POST':
        data = request.POST
        next = data['next']

        form = AttachmentForm(data = data, files = request.FILES)
        if form.is_valid():
            form.save()
            info_msg(request, u"Pièce jointe ajoutée avec succès.")
            return redirect(next)
        else:
            content_type = data['content_type']
            object_id = data['object_id']

    return render(request, "attachments/form.html", {
        'form': form,
        'content_type': content_type,
        'object_id': object_id,
        'next': next
    })


@login_required
def delete(request, attachment_id):
    attachment = get_object_or_404( Attachment, id = attachment_id )
    attachment.attached_file.delete()
    attachment.delete()

    info_msg(request, u"Pièce jointe supprimée avec succès.")
    return redirect( request.GET.get('next','home') )

from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, View

from .forms import DocumentForm
from .models import Document


class DocumentCreateView(CreateView):
    model = Document

    # Using 'fields' creates a basic ModelForm automatically with default sginature widget
    # This is convenient for simple forms when you don't need widget options
    # fields = ["name", "signature"]

    # Using 'form_class' lets you specify a custom form with detailed control over widget options
    form_class = DocumentForm

    success_url = reverse_lazy("document_list")
    template_name = "demo/document_form.html"


class DocumentListView(ListView):
    model = Document
    template_name = "demo/document_list.html"
    context_object_name = "documents"


class ClearDocumentsView(View):
    def post(self, request, *args, **kwargs):
        Document.objects.all().delete()
        return redirect("document_list")

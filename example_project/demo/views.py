from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from .models import Document


class DocumentCreateView(CreateView):
    model = Document
    fields = ["name", "signature"]
    success_url = reverse_lazy("document_list")
    template_name = "demo/document_form.html"


class DocumentListView(ListView):
    model = Document
    template_name = "demo/document_list.html"
    context_object_name = "documents"

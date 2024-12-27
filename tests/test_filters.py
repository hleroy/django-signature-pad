# tests/test_filters.py

import json

from django.template import Context, Template
from django.test import TestCase

signature_data = json.loads(
    "[{'penColor': 'black', 'dotSize': 0, 'minWidth': 0.5, 'maxWidth': 2.5, 'velocityFilterWeight': 0.7, 'compositeOperation': 'source-over', 'points': [{'time': 1735421102034, 'x': 86, 'y': 63.16668701171875, 'pressure': 0.5}, {'time': 1735421102128, 'x': 93, 'y': 67.16668701171875, 'pressure': 0.5}, {'time': 1735421102145, 'x': 103, 'y': 72.16668701171875, 'pressure': 0.5}, {'time': 1735421102161, 'x': 119, 'y': 82.16668701171875, 'pressure': 0.5}, {'time': 1735421102178, 'x': 128, 'y': 88.16668701171875, 'pressure': 0.5}, {'time': 1735421102194, 'x': 134, 'y': 91.16668701171875, 'pressure': 0.5}]}]".replace(  # noqa: E501
        "'", '"'
    )
)

rendered_data = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB2aWV3Qm94PSIwIDAgNDAwIDIwMCIgd2lkdGg9IjQwMCIgaGVpZ2h0PSIyMDAiPjxwYXRoIGQ9Ik0gODYuMDAwLDYzLjE2NyBDIDg5LjQzOSw2NS4yODEgODkuNTAwLDY1LjE2NyA5My4wMDAsNjcuMTY3IiBzdHJva2Utd2lkdGg9IjUuMzA2IiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48cGF0aCBkPSJNIDkzLjAwMCw2Ny4xNjcgQyA5OC4xNjMsNjkuMzc2IDk3LjkzOSw2OS43ODEgMTAzLjAwMCw3Mi4xNjciIHN0cm9rZS13aWR0aD0iMy44MDUiIHN0cm9rZT0iYmxhY2siIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PC9wYXRoPjxwYXRoIGQ9Ik0gMTAzLjAwMCw3Mi4xNjcgQyAxMTEuMDU1LDc3LjA4MiAxMTEuMTYzLDc2Ljg3NiAxMTkuMDAwLDgyLjE2NyIgc3Ryb2tlLXdpZHRoPSIyLjg1NyIgc3Ryb2tlPSJibGFjayIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L3BhdGg+PHBhdGggZD0iTSAxMTkuMDAwLDgyLjE2NyBDIDEyMy4zNzEsODUuMzg5IDEyMy41NTUsODUuMDgyIDEyOC4wMDAsODguMTY3IiBzdHJva2Utd2lkdGg9IjMuMjQwIiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvcGF0aD48L3N2Zz4="  # noqa: E501


class SignatureFilterTests(TestCase):
    def setUp(self):
        self.template = Template("""
            {% load signature_filters %}
            <img src="{{ signature|signature_base64 }}" alt="Signature">
        """)

    def test_filter_valid_data(self):
        # Test with valid data
        context = Context({"signature": signature_data})
        rendered = self.template.render(context)
        self.assertIn(rendered_data, rendered)

    def test_filter_invalid_data(self):
        # Test with invalid data
        context = Context({"signature": None})
        rendered = self.template.render(context)
        self.assertIn('src=""', rendered)

from django.http import HttpResponse
from django.shortcuts import render

import logging

logger = logging.getLogger('django')

# Create your views here.

def hello_world(request):
    return HttpResponse("Hello World!")

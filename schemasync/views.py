import mysql.connector
from django.shortcuts import render
from .models import SourceForm,DatabaseModel,SyncInfoForm
from django.views import generic
from django.contrib.auth import views
from django.http import HttpResponseRedirect
from .services import PageServices as pageServices
# Create your views here.

class CustomView(generic.View):
    def get(self,request):
        # if this is a POST request we need to process the form data
        form = SourceForm()
        return render(request, 'home.html', {'form': form})
    def post(self,request):
            # create a form instance and populate it with data from the request:
        form = SourceForm(request.POST)
            # check whether it's valid:
        if form.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:
            return HttpResponseRedirect('')
class SyncView(generic.View):
    # template_name = 'sync.html'
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect('/schemasync/')
    def post(self,request):
            # create a form instance and populate it with data from the request:
            # check whether it's valid:
        form = SourceForm(request.POST)
        if form.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:
            try:
                status=[]
                syncform=SyncInfoForm()
                status=pageServices.init(self,form)
            except Exception as error:
                status.append(("Failed to Validating Table {}".format(error)))
            finally:
                pagecontext = { i : status[i] for i in range(0, len(status) ) }
                return render(request, "sync.html", context={'status':status,'syncform':syncform})
        else:
            print("Invalid Form")
            context = {}
            return render(request, "sync.html", {'status':status})

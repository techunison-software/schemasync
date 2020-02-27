from django.http import HttpResponseRedirect
from django.views import generic
from django.contrib.auth import views



class CustomLogin(generic.View):
    def get(self,request):
        if request.user.is_authenticated:
            return HttpResponseRedirect("/schemasync/")
        else:
            return HttpResponseRedirect("login/")
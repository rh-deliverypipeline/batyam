from django.shortcuts import render
from django.http import HttpResponse

from .models import CodeContribution

def index(request):
    cc_list = CodeContribution.objects.all()
    #print(cc_list[0][0])
    context = {
        'codecontribution_list': cc_list,
        'fields': ['Project', 'Contributor', 'Last Updated', 'URL', 'Title',
        'State', 'Vendor', 'Team']
    }
    #output = ', '.join([cc.title for cc in cc_list])
    #return HttpResponse(output)
    return render(request, 'index.html', context=context)

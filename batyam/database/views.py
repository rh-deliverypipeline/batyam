from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from .models import CodeContribution
from .models import Project
from .models import Contributor

import json

def __extract_vendor(url):
        if url.find("gerrit") > 0:
            return "Gerrit"
        elif url.find("gitlab") > 0:
            return "Gitlab"
        else:
            return "Github"


def index(request):
    cc_list = CodeContribution.objects.all()
    context = {
        'codecontribution_list': cc_list,
        'fields': ['Project', 'Contributor', 'Last Updated', 'URL', 'Title',
        'State', 'Vendor', 'Team']
    }
    return render(request, 'index.html', context=context)


@csrf_exempt
def update(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        for obj in body:
            proj = Project.objects.create(name=obj['project'])
            lu = obj['last updated']
            cont = Contributor.objects.create(name=obj['contributor'])
            state = obj['state']
            title = obj['title']
            web_url = obj['web_url']
            vendor = __extract_vendor(web_url)
            team = ''
            CodeContribution.objects.create(
                project=proj,
                contributor=cont,
                last_updated=lu,
                url=web_url,
                title=title,
                state=state,
                vendor=vendor,
                team=team
            )

    return HttpResponse('')


def clear(request):
    Contributor.objects.all().delete()
    Project.objects.all().delete()
    CodeContribution.objects.all().delete()
    return redirect('index')

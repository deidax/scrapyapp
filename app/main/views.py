import csv
from uuid import uuid4
from urllib.parse import urlparse
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST, require_http_methods
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from scrapyd_api import ScrapydAPI
from main.models import Product
from django.http import HttpResponse
from django.shortcuts import redirect
from datetime import datetime, timedelta

filename = ''
# Create your views here.
def scraper_view(request):
    return render(request, "scraper.html")

# connect scrapyd service
scrapyd = ScrapydAPI('http://scrapyd-service:6800/')

def is_valid_company_name(company_name):
    company_name = company_name.strip()
    global filename
    filename = company_name.lower().replace(" ", "_")+".csv"
    
    if company_name == '':
        return False

    return True

@csrf_exempt
@require_http_methods(['POST', 'GET']) # only get and post
def crawl(request):
    # Post requests are for new crawling tasks
    if request.method == 'POST':

        company_name = request.POST.get('company_name', None) # take company_name comes from client. (From an input may be?)

        if not company_name:
            return JsonResponse({'error': 'Missing  args'})
        
        if not is_valid_company_name(company_name):
            return JsonResponse({'error': 'company name is invalid'})
        
        handle1=open('./data/company.txt','w+')
        handle1.write(filename)
        handle1.close()

        now = datetime.now() + timedelta(hours=1)
        datefile=open('./data/scraper_date.txt','w+')
        datefile.write(now.strftime("%b %d, %Y %H:%M:%S"))
        datefile.close()
        
        #domain = company_nameparse(company_name).netloc # parse the company_name and extract the domain
        unique_id = str(uuid4()) # create a unique ID. 
        
        # This is the custom settings for scrapy spider. 
        # We can send anything we want to use it inside spiders and pipelines. 
        # I mean, anything
        settings = {
            'unique_id': unique_id, # unique ID for each record for DB
            'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        }

        # Here we schedule a new crawling task from scrapyd. 
        # Notice that settings is a special argument name. 
        # But we can pass other arguments, though.
        # This returns a ID which belongs and will be belong to this task
        # We are goint to use that to check task's status.
        task = scrapyd.schedule('default', 'icrawler', 
            settings=settings, company_name=company_name)
        
        args = {'company': filename, 'task_id': task, 'unique_id': unique_id, 'status': 'started' }
        #response = redirect('main:crawl')
        #return response
        return JsonResponse({'company': filename, 'task_id': task, 'unique_id': unique_id, 'status': 'started' })
        #return redirect('scraper.html')

    # Get requests are for getting result of a specific crawling task
    elif request.method == 'GET':
        # We were passed these from past request above. Remember ?
        # They were trying to survive in client side.
        # Now they are here again, thankfully. <3
        # We passed them back to here to check the status of crawling
        # And if crawling is completed, we respond back with a crawled data.
        task_id = request.GET.get('task_id', None)
        unique_id = request.GET.get('unique_id', None)

        if not task_id or not unique_id:
            return JsonResponse({'error': 'Missing args'})

        # Here we check status of crawling that just started a few seconds ago.
        # If it is finished, we can query from database and get results
        # If it is not finished we can return active status
        # Possible results are -> pending, running, finished
        status = scrapyd.job_status('default', task_id)
        if status == 'finished':
            try:
                # this is the unique_id that we created even before crawling started.
                item = Product.objects.get(unique_id=unique_id) 
                return JsonResponse({'data': item.to_dict['data']})
            except Exception as e:
                return JsonResponse({'error': str(e)})
        else:
            return JsonResponse({'status': status})

def csv_export(request):
    response =  HttpResponse(content_type='text/csv')

    writer = csv.writer(response)
    writer.writerow(['Manufacturer', 'Brand', 'Name', 'Description', 'URL'])

    for product in Product.objects.all().values_list('manufacturer','brand','name', 'description', 'url'):
        writer.writerow(product)

    handle=open('./data/company.txt','r+')
    filename_csv=handle.read()
    response['Content-Disposition'] = 'attachement; filename="{filename}"'.format(filename=filename_csv)

    return response

@require_http_methods(['GET']) # only get
def get_csv_filename(request):
    handle=open('data/company.txt','r+')
    filename_csv=handle.read()
    count=Product.objects.all().count()
    data={'filename': filename_csv, 'count': count}
    return JsonResponse(data)

@require_http_methods(['GET']) # only get 
def get_scraper_date(request):
    handle=open('./data/scraper_date.txt','r+')
    scraper_date=handle.read()

    return HttpResponse(scraper_date)




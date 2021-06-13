# -*- coding: utf-8 -*-
import scrapy
from itertools import combinations
import logging
# import pyfiglet
from main.models import Product

class IcrawlerSpider(scrapy.Spider):
    name = 'icrawler'

    #configure_logging(install_root_handler=False)
    #logging.basicConfig(
    #    filename='logs/errors.txt',
    #    format='%(levelname)s: %(message)s',
    #    level=logging.ERROR
    #)

    
    allowed_domains = ['www.radwell.co.uk']
    company_name = ""
    manufacturer = ""
    FEED_URI = ""
    possible_search_patterns = []
    scraped_count = 0

    search_pattern = '0123456789ACDEFHKMNPRSTVWXY'

   #start_urls = ["https://www.radwell.co.uk/en-GB/Search/Advanced/{company_name}?SearchText=&SortField=&ABSale=False&SearchType=Default&SortDirection=0&Manufacturer={manufacturer}&InStockFlag=false&PageSize=10000000".format(company_name= company_name, manufacturer= manufacturer)]
    # 6 = G
    # 2 = Z
    # 1 = L = I
    # 0 = O = Q
    # 8 = B
    # V = U
    def __init__(self, company_name='', **kwargs):
        if company_name == '':
            logging.info("===> EXIT SCRAPING -->")
            exit()

        self.manufacturer = self.get_manufacturer(company_name)
        self.company_name = self.get_company_name(company_name)
        # ascii_banner = pyfiglet.figlet_format(self.company_name)
        # logging.info(ascii_banner)
        self.FEED_URI = self.get_FEED_URI(company_name)
        self.start_urls = ["https://www.radwell.co.uk/en-GB/Search/Advanced/{company_name}?SearchText=&SortField=&ABSale=False&SearchType=Default&SortDirection=0&Manufacturer={manufacturer}&InStockFlag=false&PageSize=10000000".format(company_name= self.company_name, manufacturer= self.manufacturer)]
        # generate the  possible search patterens
        self.possible_search_patterns = self.generate_search_pattern()
        logging.info(self.possible_search_patterns)
        super().__init__(**kwargs)  # python3
    
    # this is equivalent to what you would set in settings.py file
    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': FEED_URI
    }
    


    def parse(self, response):
        urls = self.generate_next_url(response)
        categories = self.parse_categories(response)
        print(self.FEED_URI)
        logging.info("===> CATEGORIES -->")
        for index, url in enumerate(urls):
            # for search_pattern in search_patterns:
            base_url = response.urljoin(self.get_value_of(urls,index))
            categorie = self.get_category_name_in_run_time(categories, urls, index)
            logging.info("     |__ ["+categorie+"]")
            yield response.follow(url=base_url, callback=self.parse_scrap_data, meta={'category': url, 'category_name': categorie})
            #print(base_url)

    def parse_scrap_data(self, response):
        subcategories_url = self.parse_subcategories(response)
        categorie = response.request.meta['category_name']
        logging.info("===> SCRAPING CATEGORY NAME ----> ["+categorie+"]")
        for index, subcategory_url in enumerate(subcategories_url):
            scraping_url = self.make_url(response.request.meta['category'] ,self.get_value_of(subcategories_url,index))
            logging.info("---> SCRAPING SUBCATEGORY --> ["+categorie+"/"+self.get_key_of(subcategories_url,index)+"]")
            location = categorie+"/"+self.get_key_of(subcategories_url,index)
            logging.info("Scraping url --> "+response.urljoin(scraping_url))
            yield response.follow(url=response.urljoin(scraping_url), callback=self.parse_scrap_data_for_each_search_pattern, meta={'url': response.urljoin(scraping_url), 'location': location})
            # print(response.request.meta['base_url']+self.make_url(self.get_value_of(subcategories_url,index)))
            # print(response.request.meta['base_url']+self.make_url(self.get_value_of(subcategories_url,index)))

            #print(response.urljoin(scraping_url))
    
    def parse_scrap_data_for_each_search_pattern(self, response):
        for index, search_pattern in enumerate(self.possible_search_patterns): #self.generate_search_pattern():
            number_of_remaining_patterns = len(self.possible_search_patterns) - index
            
            yield response.follow(response.request.meta['url']+self.make_url_with_search_pattern(search_pattern), callback=self.parse_item, meta={'sp': search_pattern, 'location': response.request.meta['location'], 'remaing_patterns': number_of_remaining_patterns})



    def parse_categories(self, response):
        categories = response.xpath("//select[@id='TopCategoryId']/option")

        categories_dict = {}

        for category in categories:
            if category.xpath(".//@value").get() != '':
                categories_dict[ category.xpath(".//text()").get() ] = category.xpath(".//@value").get()
        
        return categories_dict

    def parse_subcategories(self, response):
        subcategories = response.xpath("//select[@id='CategoryId']/option")

        subcategories_dict = {}

        for subcategory in subcategories:
            if subcategory.xpath(".//@value").get() != '':
                subcategories_dict[ subcategory.xpath(".//text()").get() ] = subcategory.xpath(".//@value").get()
        
        return subcategories_dict

    def parse_item(self, response):
        remaining_search_patterns = len(self.possible_search_patterns) - response.request.meta['remaing_patterns']
        str_remaining_search_patterns = str(remaining_search_patterns)+"/"+str(len(self.possible_search_patterns))
        logging.info("===>[ SC:: "+str(self.scraped_count)+"] SCRAPED WITH SEARCH PATTERN --> ["+response.request.meta['sp']+"]"+"["+response.request.meta['location']+"]"+ " REMAINING PATTERNS ["+str_remaining_search_patterns+"]")
        products = response.xpath('//a[@class="searchResult"]')
        
        for product in products:
            url = product.xpath('.//@href').get()
            manufacturer = product.xpath('.//div[@class="mfgr searchResulti"]/h2/text()').get()
            brand = product.xpath('.//div[@class="brand searchResulti"]/h2/text()').get()
            name = product.xpath('.//div[@class="partno searchResulti"]/h2/text()').get()
            description = product.xpath('.//p[@class="desc searchResulti"]/text()').get()

            product_dict = {
                'manufacturer': manufacturer,
                'brand': brand,
                'name': name,
                'description': description,
                'url': response.urljoin(url)
            }

            item = Product(url=url,manufacturer=manufacturer,brand=brand,name=name,description=description)
            item.save()

            

            self.scraped_count += 1

            yield product_dict

            return product_dict

        

    def get_value_of(self, dictvar, index):
        return list(dictvar.values())[index]
    
    def get_key_of(self, dictvar, index):
        return list(dictvar.keys())[index]

    def make_url(self, categoryId, subcategoryId):
        start_url = "/en-GB/Search/Advanced/{company_name}?SearchText=&SortField=&ABSale=False&SearchType=Default&SortDirection=0&Manufacturer={manufacturer}&SearchMethod=starts&Description=&TopCategoryId={categoryId}&CategoryId={subcategoryId}&InStockFlag=false&PageSize=10000000".format(categoryId = categoryId, subcategoryId = subcategoryId, company_name= self.company_name, manufacturer= self.manufacturer)

        return start_url

    def generate_next_url(self, response):
        categories = self.parse_categories(response)
        sub_categories = self.parse_subcategories(response)

        url_dict = {}

        for categorie in categories:
            # url = "/en-GB/Search/Advanced/SIEMENS?SearchText=&SortField=&ABSale=False&SearchType=Default&SortDirection=0&Manufacturer=SIEMENS&PartNumber=&SearchMethod=contains&Description=&TopCategoryId="+categories[categorie]
            url = "/en-GB/Search/Advanced/{company_name}?SearchText=&SortField=&ABSale=False&SearchType=Default&SortDirection=0&Manufacturer={manufacturer}&SearchMethod=starts&Description=&TopCategoryId={categoryId}&InStockFlag=false&PageSize=10000000".format(categoryId = categories[categorie], company_name= self.company_name, manufacturer= self.manufacturer)
            url_dict[categories[categorie]] = url
        
        return url_dict
    
    def make_url_with_search_pattern(self, search_pattern):
        url_search_pattern = "&PartNumber={search_pattern}".format(search_pattern = search_pattern)
        return url_search_pattern

    def generate_search_pattern(self):
        logging.info("=====> Generating the search pattern...")
        possible_search_patterns = list(combinations(self.search_pattern, 2))
        # joining all the tuples
        result = map(self.join_tuple_string, possible_search_patterns)

        search_pattern = list(self.search_pattern)
        two_characters_pattern = list(result)
        search_pattern.extend(two_characters_pattern)
        return search_pattern

    def join_tuple_string(self, strings_tuple) -> str:
       return ''.join(strings_tuple)
    
    def get_company_name(self, company_arrg):
        company_name = company_arrg.upper().replace(" ", "%")
        logging.info("=====> COMPANY NAME TO SCRAP:: ["+company_name+"]")

        return company_name 
    
    def get_manufacturer(self, company_arrg):
        manufacturer = company_arrg.upper().replace(" ", "+")
        logging.info("=====> MANUFACTURER NAME TO SCRAP:: ["+manufacturer+"]")
        
        return manufacturer

   
    def get_category_name_in_run_time(self, categories, urls, index):
        return list(categories.keys())[list(categories.values()).index(self.get_key_of(urls,index))]
    
    def get_FEED_URI(self, company_name):
        feed_url = company_name.lower().replace(" ", "_")
        logging.info("=====> CSV DATA FILE NAME:: ["+feed_url+".csv]")
        feed_url = feed_url+".csv"

        return feed_url
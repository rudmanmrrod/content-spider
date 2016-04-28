import scrapy
import json
from scrapy.http import HtmlResponse

from utils.utils import *
from utils.settings import settings

class SiteSpySpider(scrapy.Spider):
	
	name = "el_nacional-all"
	start_urls = ["http://www.el-nacional.com/presos_politicos/"]	
	
	def parse(self, response):
		#limit = int(response.css('.page::text').extract()[-1])
		my_url = response.css('.page::attr(href)').extract()[1]
		for i in range(1,3):
			page = 'page='+str(i)
			my_url = re.sub(r'page=\d+',page,my_url)
			full_url = response.urljoin(my_url)
			yield scrapy.Request(full_url, callback=self.parse_json)

				
	def parse_json(self,response):
		data = response.body[1:-1]
		js = json.loads(data)
		response = HtmlResponse(url=response.url,body=js['data'].encode('utf8'))
		for href in response.css(settings["el_nacional"]['links']):
			full_url = response.urljoin(href.extract())
			yield scrapy.Request(full_url, callback=self.parse_links)
				
	def parse_links(self, response):
		fecha = response.css(settings["el_nacional"]['fecha']).extract()[0]
		current_date = obtener_fecha_tipo1(fecha)
		#if(current_date):
		body = get_body_en([response.css(settings["el_nacional"]['body'][0]).extract(),response.css(settings["el_nacional"]['body'][1]).extract()])
		yield {
		'titulo': response.css(settings["el_nacional"]['titulo']).extract()[0],
		'autor': response.css(settings["el_nacional"]['autor']).extract()[0],
		'fecha': fecha,
		'body': [body],
		'link': response.url,
		}

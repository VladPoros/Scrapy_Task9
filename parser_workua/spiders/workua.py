# -*- coding: utf-8 -*-
import scrapy


class WorkuaSpider(scrapy.Spider):
    name = 'workua'
    allowed_domains = ['work.ua']
    start_urls = ['https://www.work.ua/ru/resumes-kharkiv/']

    def parse(self, response):

        for item in response.css('div#pjax-resume-list div.card.resume-link'):

            worker_uri = item.css('h2 a::attr(href)').get()

            result = {
                'name': item.css('div b::text').get(),
                'age': None,
                'position': item.css('h2 a::text').get(),
                'link': worker_uri
            }

            cost = item.css('h2 span.nowrap::text').get()
            if cost:
                result['cost'] = float(cost.replace(' грн', ''))

            yield response.follow(worker_uri, self.parse_worker, meta={
                'result': result
            })
        for page in response.css('ul.pagination li'):
            if page.css('a::text').get() == 'Следующая':
                yield response.follow(
                    page.css('a::attr(href)').get(),
                    self.parse)

    def parse_worker(self, response):

        age_worker = response.css('div.card div.row dl.dl-horizontal dd::text').get()[:2]

        header = response.css('div.card > h2::text').get()

        description_worker = ' '.join(response.css('div.card > p::text').getall())
        description_worker = header + ': ' + ' '.join(description_worker.split())

        response.meta['result']['description'] = description_worker
        response.meta['result']['age'] = age_worker

        yield response.meta['result']
import json
from typing import Dict

from .. import cvr

import scrapy


class CompaniesSpider(scrapy.Spider):
    name = "companies"

    def start_requests(self):
        seed = getattr(self, 'seed', 42)

        cvrs = [
            # '35408002',
            '41542446',
        ] + cvr.make_cvrs(2000, seed)

        for cvr_number in cvrs:
            # TODO: what about the locale?
            yield scrapy.Request(f'https://datacvr.virk.dk/gateway/virksomhed/hentVirksomhed?cvrnummer={cvr_number}&locale=en',
                                 callback=self.parse)

    def parse(self, response: scrapy.http.Response, **kwargs):
        # actually, there's more-or-less structured JSON available (wow)
        item = json.loads(response.text)
        # self.log(f"Response: {response}")

        return item


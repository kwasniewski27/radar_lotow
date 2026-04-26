import scrapy
from scrapy_playwright.page import PageMethod
from datetime import datetime, timedelta

class RyanairSpider(scrapy.Spider):
    name = "ryanair"
    allowed_domains = ["ryanair.com"]
    dzisiaj = datetime.now().strftime("%Y-%m-%d")
    custom_settings = {
        'ITEM_PIPELINES': {
            'zaliczenie.pipelines.BazaDanychPipeline': 300,
        },
        'DOWNLOAD_DELAY': 2.0, 
        'RANDOMIZE_DOWNLOAD_DELAY': True,
    }
    

    def start_requests(self):
        today = datetime.now()
        yield self.stworz_zapytanie(today, puste_dni = 0)
    def stworz_zapytanie(self, obiekt_daty, puste_dni):
        data_str = obiekt_daty.strftime("%Y-%m-%d")
        url = f"https://www.ryanair.com/pl/pl/fare-finder?originIata=KRK&dateOut={data_str}&dateIn=&isExactDate=true&outboundFromHour=00:00&outboundToHour=23:59&priceValueTo=&currency=PLN&destinationIata=ANY&isReturn=false&isMacDestination=false&promoCode=&adults=1&teens=0&children=0&infants=0&isFlexibleDay=false"

        return scrapy.Request(
            url=url,
            dont_filter=True,
            meta={
                'playwright': True,
                'playwright_page_methods': [
                    PageMethod('wait_for_timeout', 3000),
                    PageMethod('evaluate', "document.querySelector('button[data-ref=\"cookie.accept-all\"]')?.click()"),
                    PageMethod('wait_for_selector', 'ry-price', timeout=15000),
                    PageMethod('evaluate', "window.scrollTo(0, document.body.scrollHeight)"),
                    PageMethod('wait_for_timeout', 3000)
                ],
                'obecna_data' : obiekt_daty,
                'puste_dni' : puste_dni
            },
            callback=self.parse,
            errback=self.blad_strony
        )
    def parse(self, response):
        karty = response.css('ffd-result-card')
        obecna_data = response.meta['obecna_data']
        if karty:
            for karta in karty:
                kierunek = karta.css('.result-card-content__destination::text').get()
                cena = karta.css('.price__integers::text').get()
                waluta = karta.css('.price__symbol::text').get()
                dokladna_data = obecna_data.strftime("%Y-%m-%d")
                if kierunek and cena:
                    yield {
                        'kierunek': kierunek.strip(), 
                        'data': dokladna_data,
                        'cena': cena.strip(),
                        'waluta': waluta.strip() if waluta else None,
}
            kolejny_dzien = obecna_data + timedelta(days=1)
            yield self.stworz_zapytanie(kolejny_dzien, puste_dni = 0)
    def blad_strony(self, failure):
        request = failure.request
        obecna_data = request.meta['obecna_data']
        puste_dni = request.meta['puste_dni'] + 1  

        if puste_dni < 3:
            kolejny_dzien = obecna_data + timedelta(days=1)
            yield self.stworz_zapytanie(kolejny_dzien, puste_dni)
        else:
            self.logger.info('Koniec kalendarza lotów')
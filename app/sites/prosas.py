import requests
import json
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.database import Database
from app.notifier import AnnouncementsNotifier
from pprint import pprint

class ProsasScraper:
    BASE_URL = "https://prosas.com.br"
    ANNOUNCEMENT_URL = f"{BASE_URL}/editais/{{id}}"
    SEARCH_URL = f"{BASE_URL}/selecao/api/v2/publics/oportunidades"
    webhook = "1303555833556111360/QeCyDI6Nb-iMkV5yF0YRdO7VlRFvbQDJtGQOpV4ktzv0igzb-J3fHpCphVhAn7pZJhzC"

    def __init__(self):
        self.session = requests.Session()
        self.session.get(self.BASE_URL)
        self.db = Database()
        self.notifier = AnnouncementsNotifier(self.webhook)

    def _clean_text(self, text: str) -> str:
        return text.replace("\n", "").replace("  ", "").replace("location_on", "").strip()

    def _select_and_clean(self, soup, selector: str) -> list[str]:
        return [self._clean_text(item.text) for item in soup.select(selector)]

    def enrich_announcements(self, data: dict) -> dict:
        announcement_url = self.ANNOUNCEMENT_URL.format(id=data['id'])
        response = self.session.get(announcement_url)

        if response.status_code != 200:
            raise Exception(f"Falha ao obter dados do anúncio {data['id']}")

        soup = BeautifulSoup(response.content, "lxml")
        data['fontes'] = self._select_and_clean(soup, "li.lista-fontes-oportunidade p")
        data['locais'] = self._select_and_clean(soup, ".locais-atuacao > ul li")
        data['url'] = announcement_url

        return data

    def search_announcements(self):
        curr_page, max_pages = 0, 5
        while curr_page < max_pages:
            curr_page += 1
            url = f"{self.SEARCH_URL}?page[page]={curr_page}&page[size]=100"
            response = self.session.get(url)
            if response.status_code != 200:
                raise Exception(f"Falha ao buscar oportunidades {response.status_code=}")

            announcements = json.loads(response.content).get('data', [])
            
            if len(announcements) == 0:
                pprint(f"{announcements=} {url=}")
                break

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [
                    executor.submit(self.enrich_announcements, self._arrange_data(event.get('attributes', {})))
                    for event in announcements
                ]
                for future in as_completed(futures):
                    try:
                        enriched_data = future.result()
                        enriched_data = enriched_data
                        pprint(enriched_data)
                        if self.db.save_announcement(enriched_data):
                            self.notifier.send_notification(enriched_data)
                    except Exception as e:
                        print(f"Erro ao processar anúncio: {e}")

    @staticmethod
    def _arrange_data(data: dict) -> dict:
        for field in ['whitelabel', 'subdominio', 'logo', 'subdominio_widget', 'e_central?']:
            data.pop(field, None)
        return data


if __name__ == "__main__":
    scraper = ProsasScraper()
    scraper.search_announcements()

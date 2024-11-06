import requests
from pprint import pprint

from bs4 import BeautifulSoup
from app.database import Database
from app.notifier import Notifier


class AbcrScraper:
    BASE_URL = "https://captadores.org.br"
    ANNOUNCEMENT_URL = f"{BASE_URL}/category/editais/"
    webhook = "1303555637027930132/bLy6HZhbfJNHSPwzqOhQtlSET8YBCrPFK0X_LZ-0kZ5Qy8XZO1v9eamnK9B-6BqqEb1i"

    def __init__(self):
        self.session = requests.Session()
        self.session.get(self.BASE_URL)
        self.db = Database()
        self.notifier = Notifier(self.webhook)

    def search_announcements(self):
        response = self.session.get(self.ANNOUNCEMENT_URL)
        if response.status_code != 200:
            raise Exception("Falha ao buscar oportunidades")

        soup = BeautifulSoup(response.content, "html.parser")
        announcements = soup.select("div.post-title a")

        for announcement in announcements:
            item = {
                'id': announcement.get('href', self.ANNOUNCEMENT_URL),
                'nome': announcement.text,
                'fontes': '',
                'locais': '',
                'url': announcement.get('href', self.ANNOUNCEMENT_URL),
            }
            pprint(item)
            if self.db.save_announcement(item):
                self.notifier.send_notification(item)


if __name__ == "__main__":
    scraper = AbcrScraper()
    scraper.search_announcements()

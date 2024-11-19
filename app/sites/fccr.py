import requests
from pprint import pprint

from bs4 import BeautifulSoup
from app.database import Database
from app.notifier import AnnouncementsNotifier


class FundassScraper:
    BASE_URL = "https://fccr.sp.gov.br"
    ANNOUNCEMENT_URL = f"{BASE_URL}/fccr/home/noticias"
    webhook = "1305686340612128768/cJJ7xbEbzCjb_Zc941KEHudZKKRmdoIAEqhk7Eg2K1kDHdMWARAEOb1_S-EsaSzDcz0A"
    headers = {
        "Host": "fccr.sp.gov.br",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://fccr.sp.gov.br/fccr/portal/",
        "Connection": "keep-alive",
        "Cookie": "PHPSESSID=20af21043c85cc6fc597f503d007ee28",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Sec-GPC": "1",
        "Priority": "u=0, i",
        "TE": "trailers"
    }




    def __init__(self):
        self.session = requests.Session()
        self.session.get(self.BASE_URL, headers=self.headers)
        self.db = Database()
        self.notifier = AnnouncementsNotifier(self.webhook)

    def search_announcements(self):
        response = self.session.get(self.ANNOUNCEMENT_URL, headers=self.headers)
        if response.status_code != 200:
            print(response.status_code, response.history)
            raise Exception("Falha ao buscar oportunidades")

        soup = BeautifulSoup(response.content, "html.parser")
        announcements = soup.select("h4 a")


        new_announcements = []
        for announcement in announcements:
            item = {
                'id': self.BASE_URL + announcement.get('href', self.ANNOUNCEMENT_URL),
                'nome': announcement.text,
                'fontes': '',
                'locais': '',
                'url': self.BASE_URL + announcement.get('href', self.ANNOUNCEMENT_URL),
            }
            if self.db.save_announcement(item):
                self.notifier.send_notification(item)
                new_announcements.append(item)
        


if __name__ == "__main__":
    scraper = FundassScraper()
    scraper.search_announcements()

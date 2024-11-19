import requests
from pprint import pprint

from bs4 import BeautifulSoup
from app.database import Database
from app.notifier import AnnouncementsNotifier


class FundassScraper:
    BASE_URL = "https://fundacc.sp.gov.br"
    ANNOUNCEMENT_URL = f"{BASE_URL}/categorias/editais/"
    webhook = "1305684904020938913/h2eu2gvmKlz213kPmjbcEUpBe-juFrIRX2YWAMulWmzA9W7dhtpdakG9TxshFOFTCxZD"
    headers = {
        "Host": "fundacc.sp.gov.br",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
        "Cookie": "nrjGUKB_fLuS=h6d8ve; Whv-sEeXUcxt=V40k5sxHC; qOpwB-zLNTWZDxoh=u.HL%5B%40mKMtJQz",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Sec-GPC": "1",
        "Priority": "u=0, i"
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
        announcements = soup.select("div.post-entry-content a")


        new_announcements = []
        for announcement in announcements:
            item = {
                'id': announcement.get('href', self.ANNOUNCEMENT_URL),
                'nome': announcement.text,
                'fontes': '',
                'locais': '',
                'url': announcement.get('href', self.ANNOUNCEMENT_URL),
            }
            if self.db.save_announcement(item):
                self.notifier.send_notification(item)
                new_announcements.append(item)
        


if __name__ == "__main__":
    scraper = FundassScraper()
    scraper.search_announcements()

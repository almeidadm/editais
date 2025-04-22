import requests
import json
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.database import Database
from app.notifier import AnnouncementsNotifier
from pprint import pprint

class ProsasScraper:
    BASE_URL = "https://prosas.com.br"
    ENTITY_URL = f"{BASE_URL}/patrocinadores/{{entity_id}}"
    ANNOUNCEMENT_URL = f"{BASE_URL}/editais/{{id}}"
    SEARCH_URL = f"{BASE_URL}/selecao/api/v2/publics/oportunidades"
    webhook = "1303555833556111360/QeCyDI6Nb-iMkV5yF0YRdO7VlRFvbQDJtGQOpV4ktzv0igzb-J3fHpCphVhAn7pZJhzC"

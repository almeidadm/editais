import requests
import time


class Notifier:
    hook_base = "https://discordapp.com/api/webhooks/"
    def __init__(self, webhook_url):
        self.webhook_url = self.hook_base+webhook_url

    def send_notification(self, announcement: dict):
        subject = f"Novo edital: {announcement['nome']}"
        body = f"Detalhes do edital em: {announcement['url']}"

        payload = {
            "content": f"**{subject}**\n{body}"
        }

        def post():
            return requests.post(self.webhook_url, json=payload)

        while True:
            response = post()
            if response.status_code == 204:
                break
            elif response.status_code == 429:
                retry_after = float(response.headers.get("Retry-After", 1)) 
                print(f"Rate limited. Aguardando {retry_after} segundos antes de tentar novamente...")
                time.sleep(retry_after)
            else:
                raise Exception(f"Falha ao enviar a notificação: {response.status_code}, {response.text}")



if __name__ == "__main__":
    notifier = Notifier()

from pydantic import BaseModel
from typing import Any, Dict
import requests
import time
from abc import ABC, abstractmethod


class LogMessage(BaseModel):
    level: str
    message: str
    timestamp: str


class Notifier(ABC):
    hook_base: str = "https://discordapp.com/api/webhooks/"
    
    def __init__(self, webhook_url: str):
        self.webhook_url: str = self.hook_base + webhook_url

    def send_payload(self, payload: Dict[str, str]) -> None:
        """
        Envia o payload para o webhook com controle de erros e tratamento de limitações de taxa.
        """
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


    @abstractmethod
    def send_notification(self, *args: Any, **kwargs: Any) -> None:
        pass


class LogNotifier(Notifier):
    def send_notification(self, log_message: LogMessage) -> None:
        payload: Dict[str, str] = {
            "content": f"[{log_message.level}] {log_message.timestamp} - {log_message.message}"
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
                raise Exception(f"Falha ao enviar a notificação de log: {response.status_code}, {response.text}")

class AnnouncementsNotifier(Notifier):

    def send_notification(self, announcement) -> None:
        subject = f"Novo edital: {announcement['nome']}"
        body = f"Detalhes do edital em: {announcement['url']}"

        payload: Dict[str, str] = {
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


# Exemplo de uso
if __name__ == "__main__":
    webhook_url = "seu_webhook_url"  # substitua pelo ID específico do webhook
    log_notifier = LogNotifier(webhook_url)
    
    # Exemplo de mensagem de log
    log_message = LogMessage(level="INFO", message="Execução iniciada com sucesso", timestamp="2024-11-08T12:00:00Z")
    log_notifier.send_notification(log_message)

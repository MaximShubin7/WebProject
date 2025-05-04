import json
import requests
import cv2
from pyzbar.pyzbar import decode


class ParserReceiptQRCodeToData:
    HOST = 'irkkt-mobile.nalog.ru:8888'
    ACCEPT = '*/*'
    DEVICE_OS = 'iOS'
    DEVICE_ID = '7C82010F-16CC-446B-8F66-FC4080C66521'
    CLIENT_VERSION = '2.9.0'
    ACCEPT_LANGUAGE = 'ru-RU;q=1, en-US;q=0.9'
    USER_AGENT = 'billchecker/2.9.0'
    CLIENT_SECRET = 'IyvrAbKt9h/8p6a7QPh8gpkXYQ4='

    def __init__(self):
        self.session_id = None
        self.set_session_id()

    def set_session_id(self) -> None:
        self.phone_number = input('Input phone in +70000000000 format: ')
        url = f'https://{self.HOST}/v2/auth/phone/request'
        payload = {
            'phone': self.phone_number,
            'client_secret': self.CLIENT_SECRET,
            'os': self.DEVICE_OS
        }
        headers = {
            'Host': self.HOST,
            'Accept': self.ACCEPT,
            'Device-OS': self.DEVICE_OS,
            'Device-Id': self.DEVICE_ID,
            'clientVersion': self.CLIENT_VERSION,
            'Accept-Language': self.ACCEPT_LANGUAGE,
            'User-Agent': self.USER_AGENT,
        }
        response = requests.post(url, json=payload, headers=headers)

        self.code = input('Input code from SMS: ')
        url = f'https://{self.HOST}/v2/auth/phone/verify'
        payload = {
            'phone': self.phone_number,
            'client_secret': self.CLIENT_SECRET,
            'code': self.code,
            "os": self.DEVICE_OS
        }
        response = requests.post(url, json=payload, headers=headers)

        self.session_id = response.json()['sessionId']
        self.refresh_token = response.json()['refresh_token']

    def refresh_token_function(self) -> None:
        url = f'https://{self.HOST}/v2/mobile/users/refresh'
        payload = {
            'refresh_token': self.refresh_token,
            'client_secret': self.CLIENT_SECRET
        }
        headers = {
            'Host': self.HOST,
            'Accept': self.ACCEPT,
            'Device-OS': self.DEVICE_OS,
            'Device-Id': self.DEVICE_ID,
            'clientVersion': self.CLIENT_VERSION,
            'Accept-Language': self.ACCEPT_LANGUAGE,
            'User-Agent': self.USER_AGENT,
        }
        response = requests.post(url, json=payload, headers=headers)

        self.session_id = response.json()['sessionId']
        self.refresh_token = response.json()['refresh_token']

    def get_ticket_id(self, qr: str) -> str:
        url = f'https://{self.HOST}/v2/ticket'
        payload = {'qr': qr}
        headers = {
            'Host': self.HOST,
            'Accept': self.ACCEPT,
            'Device-OS': self.DEVICE_OS,
            'Device-Id': self.DEVICE_ID,
            'clientVersion': self.CLIENT_VERSION,
            'Accept-Language': self.ACCEPT_LANGUAGE,
            'sessionId': self.session_id,
            'User-Agent': self.USER_AGENT,
        }
        response = requests.post(url, json=payload, headers=headers)
        return response.json()["id"]

    def get_ticket(self, qr: str) -> dict:
        ticket_id = self.get_ticket_id(qr)
        url = f'https://{self.HOST}/v2/tickets/{ticket_id}'
        headers = {
            'Host': self.HOST,
            'Accept': self.ACCEPT,
            'Device-OS': self.DEVICE_OS,
            'Device-Id': self.DEVICE_ID,
            'clientVersion': self.CLIENT_VERSION,
            'Accept-Language': self.ACCEPT_LANGUAGE,
            'User-Agent': self.USER_AGENT,
            'sessionId': self.session_id,
            'Content-Type': 'application/json'
        }
        response = requests.get(url, headers=headers)
        return response.json()

    def decode_qr_code(self, image_path: str) -> str:
        try:
            image = cv2.imread(image_path)
            decoded_objects = decode(image)
            for obj in decoded_objects:
                return obj.data.decode("utf-8")
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == '__main__':
    client = ParserReceiptQRCodeToData()
    qr_code = client.decode_qr_code("path")
    ticket = client.get_ticket(qr_code)
    print(json.dumps(ticket, indent=4, ensure_ascii=False))

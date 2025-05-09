from typing import Optional
import numpy as np
import requests
import cv2

from DataBase.QRCodesTable import QRCodesTable
from Classes.User import UserResponse
from DataBase.UsersTable import UsersTable


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

    def set_session_id(self, phone_number: str) -> None:
        url = f'https://{self.HOST}/v2/auth/phone/request'
        payload = {
            'phone': phone_number,
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

    def verify_session_id(self, phone_number: str, code: str):
        url = f'https://{self.HOST}/v2/auth/phone/verify'
        payload = {
            'phone': phone_number,
            'client_secret': self.CLIENT_SECRET,
            'code': code,
            "os": self.DEVICE_OS
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
        return response.json()["ticket"]

    def decode_qr_code(self, image_np: np.ndarray) -> Optional[str]:
        try:
            detector = cv2.QRCodeDetector()
            data, _, _ = detector.detectAndDecode(image_np)
            return data
        except Exception as e:
            print(f"Ошибка: {e}")


class UseParserReceipt:
    def request_session_id(self, user: UserResponse):
        client = ParserReceiptQRCodeToData()
        client.set_session_id(user.phone_number)

    def add_bonus(self, user: UserResponse, code: str, image_np: np.ndarray):
        try:
            client = ParserReceiptQRCodeToData()
            client.verify_session_id(user.phone_number, code)
        except Exception:
            raise ValueError("Invalid code")
        try:
            qr_code_data = client.decode_qr_code(image_np)
            repository = QRCodesTable()
            if repository.get_qr_code(qr_code_data) is not None:
                raise ValueError("The QR code has already been read")

            ticket = client.get_ticket(qr_code_data)
            ticket_sum = ticket["document"]["receipt"]["totalSum"]
            bonus = round(ticket_sum / 100 / 200, 2)
            repository = UsersTable()
            repository.change_bonus(user.user_id, bonus)

            repository = QRCodesTable()
            repository.add_qr_code(qr_code_data)
        except Exception:
            raise ValueError("Unknown error")

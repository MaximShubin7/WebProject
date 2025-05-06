from typing import Optional


class QRCodesTable:
    def __init__(self, connection):
        self.connection = connection

    def add_qr_code(self, qr_code_data: str) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO qr_codes (qr_code_data)
                VALUES (%s)
                """,
                (qr_code_data,))
            self.connection.commit()

    def get_qr_code(self, qr_code_data: str) -> Optional[str]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM qr_codes WHERE qr_code_data = %s",
                (qr_code_data,))
            result = cursor.fetchone()[0]
            return result

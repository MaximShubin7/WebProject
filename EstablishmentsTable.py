from typing import Optional
from uuid import UUID
from Establishment import EstablishmentCreate, EstablishmentUpdate, EstablishmentResponse


class EstablishmentsTable:
    def __init__(self, connection):
        self.connection = connection

    def add_establishment(self, establishment: EstablishmentCreate) -> UUID:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO establishments (
                    establishment_type_id, address_id, menu_id, rating, count_comment,
                    official_website, working_hours, average_check
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING establishment_id
                """,
                (establishment.establishment_type_id, establishment.address_id, establishment.menu_id,
                 establishment.rating, establishment.count_comment, establishment.official_website,
                 establishment.working_hours, establishment.average_check))
            establishment_id = cursor.fetchone()[0]
            self.connection.commit()
            return establishment_id

    def get_establishment(self, establishment_id: str) -> Optional[EstablishmentResponse]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM establishments WHERE establishment_id = %s",
                (establishment_id,))
            result = cursor.fetchone()
            if result:
                columns = [desc[0] for desc in cursor.description]
                return EstablishmentResponse(zip(columns, result))
            return None

    def update_establishment(self, establishment: EstablishmentUpdate) -> bool:
        fields = establishment.dict()
        updates = []
        params = []

        for field, value in fields.items():
            if field != "establishment_id" and value is not None:
                updates.append(f"{field} = %s")
                params.append(value)

        if not updates:
            return False

        params.append(establishment.establishment_id)
        query = f"UPDATE establishments SET {', '.join(updates)} WHERE establishment_id = %s"

        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.rowcount > 0

    def delete_establishment(self, establishment_id: str) -> bool:
        with self.connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM establishments WHERE establishment_id = %s",
                (establishment_id,))
            self.connection.commit()
            return cursor.rowcount > 0

    def increment_comment_count(self, establishment_id: str) -> bool:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE establishments 
                SET count_comment = count_comment + 1 
                WHERE establishment_id = %s
                """,
                (establishment_id,))
            self.connection.commit()
            return cursor.rowcount > 0

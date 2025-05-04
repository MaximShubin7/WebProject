from typing import List
from uuid import UUID
from EstablishmentType import EstablishmentTypeCreate, EstablishmentTypeUpdate, EstablishmentTypeResponse


class EstablishmentTypesTable:
    def __init__(self, connection):
        self.connection = connection

    def add_establishment_type(self, establishment_type: EstablishmentTypeCreate) -> UUID:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO establishmentTypes (establishment_type)
                VALUES (%s)
                RETURNING establishment_type_id
                """,
                (establishment_type.establishment_type,))
            establishment_type_id = cursor.fetchone()[0]
            self.connection.commit()
            return establishment_type_id

    def get_establishment_type(self, establishment_type_id: str) -> List:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM establishmentTypes 
                WHERE establishment_type_id = %s
                """,
                (establishment_type_id,))
            result = cursor.fetchone()
            if result:
                columns = [desc[0] for desc in cursor.description]
                return EstablishmentTypeResponse(zip(columns, result))
            return None

    def update_establishment_type(self, establishment_type: EstablishmentTypeUpdate) -> bool:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE establishmentTypes 
                SET establishment_type = %s 
                WHERE establishment_type_id = %s
                """,
                (establishment_type.establishment_type, establishment_type.establishment_type_id))
            self.connection.commit()
            return cursor.rowcount > 0

    def delete_type(self, establishment_type_id: str) -> bool:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM establishmentTypes 
                WHERE establishment_type_id = %s
                """,
                (establishment_type_id,))
            self.connection.commit()
            return cursor.rowcount > 0

from typing import Optional, List
from uuid import UUID

from AddressesTable import AddressesTable
from Establishment import EstablishmentCreate, EstablishmentUpdate, EstablishmentResponse, EstablishmentAddressResponse


class EstablishmentsTable:
    def __init__(self, connection):
        self.connection = connection

    def add_establishment(self, establishment: EstablishmentCreate) -> UUID:
        repository = AddressesTable(self.connection)
        address_id = repository.add_address(establishment.address)
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO establishments (address_id, name, rating, count_comment, contacts,
                    official_website, social_links, working_hours)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING establishment_id
                """,
                (address_id, establishment.name, establishment.rating, establishment.count_comment,
                 establishment.contacts, establishment.official_website, establishment.social_links,
                 establishment.working_hours))
            establishment_id = cursor.fetchone()[0]
            self.connection.commit()
            return establishment_id

    def get_all_establishments(self) -> Optional[List[EstablishmentAddressResponse]]:
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT e.establishment_id,
                       e.name,
                       a.address_id,
                       a.address,
                       a.latitude,
                       a.longitude
                FROM establishments e
                JOIN addresses a ON e.address_id = a.address_id
            """)

            results = cursor.fetchall()
            if not results:
                return None

            columns = [desc[0] for desc in cursor.description]
            establishments = []
            for row in results:
                row_data = dict(zip(columns, row))
                address_data = {
                    'address_id': row_data['address_id'],
                    'address': row_data['address'],
                    'latitude': row_data['latitude'],
                    'longitude': row_data['longitude']
                }
                establishment_data = {
                    'establishment_id': row_data['establishment_id'],
                    'name': row_data['name'],
                    'address': address_data
                }
                establishments.append(EstablishmentAddressResponse(**establishment_data))
            return establishments

    def get_establishment(self, establishment_id: str) -> Optional[EstablishmentResponse]:
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT e.*,
                       a.address_id,
                       a.address,
                       a.latitude,
                       a.longitude
                FROM establishments e
                JOIN addresses a ON e.address_id = a.address_id
                WHERE e.establishment_id = %s
            """, (establishment_id,))

            result = cursor.fetchone()
            if not result:
                return None

            columns = [desc[0] for desc in cursor.description]
            row_data = dict(zip(columns, result))
            address_data = {
                'address_id': row_data['address_id'],
                'address': row_data['address'],
                'latitude': row_data['latitude'],
                'longitude': row_data['longitude']
            }
            row_data['address'] = address_data
            return EstablishmentResponse(**row_data)

    def update_establishment(self, establishment: EstablishmentUpdate) -> bool:
        fields = establishment.dict()
        updates = []
        params = []

        if establishment.address is not None:
            repository = AddressesTable(self.connection)
            repository.update_address(establishment.address)

        for field, value in fields.items():
            if field != "establishment_id" and field != "address" and value is not None:
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

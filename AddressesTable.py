from typing import Optional
from uuid import UUID
from Address import AddressCreate, AddressUpdate, AddressResponse


class AddressesTable:
    def __init__(self, connection):
        self.connection = connection

    def add_address(self, address: AddressCreate) -> UUID:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO addresses (
                    country, region, city, street, house_number, 
                    building, floor, postal_code, latitude, longitude
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING address_id
                """,
                (address.country, address.region, address.city, address.street, address.house_number,
                 address.building, address.floor, address.postal_code, address.latitude, address.longitude))
            address_id = cursor.fetchone()[0]
            self.connection.commit()
            return address_id

    def get_address(self, address_id: str) -> Optional[AddressResponse]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM addresses WHERE address_id = %s",
                (address_id,))
            result = cursor.fetchone()
            if result:
                columns = [desc[0] for desc in cursor.description]
                return AddressResponse(zip(columns, result))
            return None

    def update_address(self, address: AddressUpdate) -> bool:
        fields = address.dict()
        updates = []
        params = []

        for field, value in fields.items():
            if field != "address_id" and value is not None:
                updates.append(f"{field} = %s")
                params.append(value)

        if not updates:
            return False

        params.append(address.address_id)
        query = f"UPDATE addresses SET {', '.join(updates)} WHERE address_id = %s"

        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.rowcount > 0

    def delete_address(self, address_id: str) -> bool:
        with self.connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM addresses WHERE address_id = %s",
                (address_id,))
            self.connection.commit()
            return cursor.rowcount > 0

from contextlib import contextmanager
from typing import Optional
from uuid import UUID
from sqlalchemy import Table, MetaData, select, insert, update, delete

from Classes.Address import AddressCreate, AddressUpdate, AddressResponse
from DataBase.ConnectDataBase import get_sqlalchemy_engine


class AddressesTable:
    def __init__(self):
        self.engine = get_sqlalchemy_engine()
        self.metadata = MetaData()
        self.addresses = Table(
            'addresses',
            self.metadata,
            autoload_with=self.engine
        )

    @contextmanager
    def get_connection(self):
        conn = self.engine.connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def add_address(self, address: AddressCreate) -> UUID:
        stmt = insert(self.addresses).values(
            address=address.address,
            latitude=address.latitude,
            longitude=address.longitude
        ).returning(self.addresses.c.address_id)

        with self.get_connection() as conn:
            result = conn.execute(stmt)
            address_id = result.scalar_one()
            return address_id

    def get_address(self, address_id: UUID) -> Optional[AddressResponse]:
        stmt = (select(
            self.addresses.c.address_id,
            self.addresses.c.address,
            self.addresses.c.latitude,
            self.addresses.c.longitude)
                .where(self.addresses.c.address_id == address_id))

        with self.get_connection() as conn:
            result = conn.execute(stmt).fetchone()
            if result:
                return AddressResponse(
                    address_id=result.address_id,
                    address=result.address,
                    latitude=result.latitude,
                    longitude=result.longitude
                )
            return None

    def update_address(self, address: AddressUpdate) -> bool:
        update_data = {}
        if address.address is not None:
            update_data['address'] = address.address
        if address.latitude is not None:
            update_data['latitude'] = address.latitude
        if address.longitude is not None:
            update_data['longitude'] = address.longitude

        if not update_data:
            return False

        stmt = (update(self.addresses)
                .where(self.addresses.c.address_id == address.address_id)
                .values(**update_data))

        with self.get_connection() as conn:
            result = conn.execute(stmt)
            return result.rowcount > 0

    def delete_address(self, address_id: UUID) -> bool:
        stmt = (delete(self.addresses)
                .where(self.addresses.c.address_id == address_id))

        with self.get_connection() as conn:
            result = conn.execute(stmt)
            return result.rowcount > 0

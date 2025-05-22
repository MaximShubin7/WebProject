from contextlib import contextmanager
from typing import Optional, List
from uuid import UUID
from sqlalchemy import Table, MetaData, select, insert, update, delete, join, and_

from Classes.Address import AddressResponse
from Classes.FilterEstablishments import FilterEstablishments
from DataBase.AddressesTable import AddressesTable
from Classes.Establishment import EstablishmentCreate, EstablishmentUpdate, EstablishmentResponse, \
    EstablishmentAddressResponse
from DataBase.ConnectDataBase import get_sqlalchemy_engine


class EstablishmentsTable:
    def __init__(self):
        self.engine = get_sqlalchemy_engine()
        self.metadata = MetaData()

        self.establishments = Table('establishments', self.metadata, autoload_with=self.engine)
        self.addresses = Table('addresses', self.metadata, autoload_with=self.engine)
        self.addresses_table = AddressesTable()

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

    def add_establishment(self, establishment: EstablishmentCreate) -> UUID:
        address_id = self.addresses_table.add_address(establishment.address)

        stmt = insert(self.establishments).values(
            address_id=address_id,
            name=establishment.name,
            rating=establishment.rating,
            count_comment=establishment.count_comment,
            contacts=establishment.contacts,
            official_website=establishment.official_website,
            social_links=establishment.social_links,
            working_hours=establishment.working_hours
        ).returning(self.establishments.c.establishment_id)

        with self.get_connection() as conn:
            result = conn.execute(stmt)
            establishment_id = result.scalar_one()
            return establishment_id

    def get_all_establishments(self, filters: FilterEstablishments) -> Optional[List[EstablishmentAddressResponse]]:
        j = join(
            self.establishments,
            self.addresses,
            self.establishments.c.address_id == self.addresses.c.address_id
        )

        stmt = select(
            self.establishments.c.establishment_id,
            self.establishments.c.name,
            self.addresses.c.address_id,
            self.addresses.c.address,
            self.addresses.c.latitude,
            self.addresses.c.longitude
        ).select_from(j)

        conditions = []
        if filters.name is not None:
            conditions.append(self.establishments.c.name.ilike(f"%{filters.name}%"))
        if filters.rating is not None:
            conditions.append(self.establishments.c.rating >= filters.rating)
        if filters.latitude is not None:
            conditions.append(self.addresses.c.latitude.between(
                filters.latitude - 0.005,
                filters.latitude + 0.005
            ))
        if filters.longitude is not None:
            conditions.append(self.addresses.c.longitude.between(
                filters.longitude - 0.01,
                filters.longitude + 0.01
            ))
        if conditions:
            stmt = stmt.where(and_(*conditions))

        with self.get_connection() as conn:
            results = conn.execute(stmt).fetchall()

            if not results:
                return None

            return [
                EstablishmentAddressResponse(
                    establishment_id=row.establishment_id,
                    name=row.name,
                    address=AddressResponse(
                        address_id=row.address_id,
                        address=row.address,
                        latitude=row.latitude,
                        longitude=row.longitude
                    )
                )
                for row in results
            ]

    def get_establishment(self, establishment_id: UUID) -> Optional[EstablishmentResponse]:
        j = join(
            self.establishments,
            self.addresses,
            self.establishments.c.address_id == self.addresses.c.address_id
        )

        stmt = (select(
            self.establishments,
            self.addresses.c.address_id,
            self.addresses.c.address,
            self.addresses.c.latitude,
            self.addresses.c.longitude)
                .select_from(j)
                .where(self.establishments.c.establishment_id == establishment_id))
        with self.get_connection() as conn:
            result = conn.execute(stmt).fetchone()

            if not result:
                return None

            establishment_data = dict(result._asdict())
            address_data = {
                'address_id': establishment_data.pop('address_id'),
                'address': establishment_data.pop('address'),
                'latitude': establishment_data.pop('latitude'),
                'longitude': establishment_data.pop('longitude')
            }
            establishment_data['address'] = address_data

            return EstablishmentResponse(**establishment_data)

    def update_establishment(self, establishment: EstablishmentUpdate) -> bool:
        if establishment.address is not None:
            if not self.addresses_table.update_address(establishment.address):
                return False

        update_data = {}
        if establishment.name is not None:
            update_data['name'] = establishment.name
        if establishment.rating is not None:
            update_data['rating'] = establishment.rating
        if establishment.count_comment is not None:
            update_data['count_comment'] = establishment.count_comment
        if establishment.contacts is not None:
            update_data['contacts'] = establishment.contacts
        if establishment.official_website is not None:
            update_data['official_website'] = establishment.official_website
        if establishment.social_links is not None:
            update_data['social_links'] = establishment.social_links
        if establishment.working_hours is not None:
            update_data['working_hours'] = establishment.working_hours

        if not update_data:
            return True

        stmt = (update(self.establishments)
                .where(self.establishments.c.establishment_id == establishment.establishment_id)
                .values(**update_data))

        with self.get_connection() as conn:
            result = conn.execute(stmt)
            return result.rowcount > 0

    def delete_establishment(self, establishment_id: UUID) -> bool:
        stmt = (delete(self.establishments)
                .where(self.establishments.c.establishment_id == establishment_id))

        with self.get_connection() as conn:
            result = conn.execute(stmt)
            return result.rowcount > 0

    def increment_comment_count(self, establishment_id: UUID) -> bool:
        stmt = (update(self.establishments)
                .where(self.establishments.c.establishment_id == establishment_id)
                .values(count_comment=self.establishments.c.count_comment + 1))

        with self.get_connection() as conn:
            result = conn.execute(stmt)
            return result.rowcount > 0

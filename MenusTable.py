from typing import Optional
from uuid import UUID
from Menu import MenuCreate, MenuUpdate, MenuResponse


class MenusTable:
    def __init__(self, connection):
        self.connection = connection

    def add_menu(self, menu: MenuCreate) -> UUID:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO menus (menu)
                VALUES (%s)
                RETURNING menu_id
                """,
                (menu.menu,))
            menu_id = cursor.fetchone()[0]
            self.connection.commit()
            return menu_id

    def get_menu(self, menu_id: str) -> Optional[MenuResponse]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM menus WHERE menu_id = %s",
                (menu_id,))
            result = cursor.fetchone()
            if result:
                columns = [desc[0] for desc in cursor.description]
                return MenuResponse(zip(columns, result))
            return None

    def update_menu(self, menu: MenuUpdate) -> bool:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE menus 
                SET menu = %s 
                WHERE menu_id = %s
                """,
                (menu.menu, menu.menu_id))
            self.connection.commit()
            return cursor.rowcount > 0

    def delete_menu(self, menu_id: str) -> bool:
        with self.connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM menus WHERE menu_id = %s",
                (menu_id,))
            self.connection.commit()
            return cursor.rowcount > 0

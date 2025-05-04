from typing import Optional, List
from uuid import UUID
from Comment import CommentCreate, CommentUpdate, CommentResponse


class CommentsTable:
    def __init__(self, connection):
        self.connection = connection

    def add_comment(self, comment: CommentCreate) -> UUID:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO comments (user_id, establishment_id, rating, text)
                VALUES (%s, %s, %s, %s)
                RETURNING comment_id
                """,
                (comment.user_id, comment.establishment_id, comment.rating, comment.text))
            comment_id = cursor.fetchone()[0]
            self.connection.commit()
            return comment_id

    def get_comment(self, comment_id: str) -> Optional[CommentResponse]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM comments WHERE comment_id = %s",
                (comment_id,))
            result = cursor.fetchone()
            if result:
                columns = [desc[0] for desc in cursor.description]
                return CommentResponse(zip(columns, result))
            return None

    def get_comments_by_establishment(self, establishment_id: str) -> List:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT c.*, u.name as user_name 
                FROM comments c
                JOIN users u ON c.user_id = u.user_id
                WHERE c.establishment_id = %s
                ORDER BY c.created_at DESC
                """,
                (establishment_id,))
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def update_comment(self, comment: CommentUpdate) -> bool:
        fields = comment.dict()
        updates = []
        params = []

        for field, value in fields.items():
            if field != "comment_id" and value is not None:
                updates.append(f"{field} = %s")
                params.append(value)

        if not updates:
            return False

        params.append(comment.comment_id)
        query = f"UPDATE comments SET {', '.join(updates)} WHERE comment_id = %s"

        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.rowcount > 0

    def delete_comment(self, comment_id: str) -> bool:
        with self.connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM comments WHERE comment_id = %s",
                (comment_id,))
            self.connection.commit()
            return cursor.rowcount > 0

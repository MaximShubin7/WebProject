from contextlib import contextmanager
from typing import Optional, List
from uuid import UUID
from sqlalchemy import Table, MetaData, select, insert, update, delete, join

from Classes.Comment import CommentCreate, CommentUpdate, CommentResponse
from DataBase.ConnectDataBase import get_sqlalchemy_engine


class CommentsTable:
    def __init__(self):
        self.engine = get_sqlalchemy_engine()
        self.metadata = MetaData()

        self.comments = Table('comments', self.metadata, autoload_with=self.engine)
        self.users = Table('users', self.metadata, autoload_with=self.engine)
        self.establishments = Table('establishments', self.metadata, autoload_with=self.engine)

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

    def add_comment(self, comment: CommentCreate) -> UUID:
        stmt = (insert(self.comments)
                .values(
            user_id=comment.user_id,
            establishment_id=comment.establishment_id,
            rating=comment.rating,
            text=comment.text)
                .returning(self.comments.c.comment_id))

        with self.get_connection() as conn:
            result = conn.execute(stmt)
            comment_id = result.scalar_one()
            return comment_id

    def get_comment(self, comment_id: UUID) -> Optional[CommentResponse]:
        stmt = (select(self.comments)
                .where(self.comments.c.comment_id == comment_id))

        with self.get_connection() as conn:
            result = conn.execute(stmt).fetchone()
            if result:
                return CommentResponse(**result._asdict())
            return None

    def get_comments_by_establishment(self, establishment_id: UUID) -> List[CommentResponse]:
        j = join(
            self.comments,
            self.users,
            self.comments.c.user_id == self.users.c.user_id
        )

        stmt = (select(
            self.comments,
            self.users.c.name.label('user_name'))
                .select_from(j).where(
            self.comments.c.establishment_id == establishment_id)
                .order_by(self.comments.c.created_time.desc()))

        with self.get_connection() as conn:
            results = conn.execute(stmt).fetchall()
            return [CommentResponse(**row._asdict()) for row in results]

    def get_comments_by_user(self, user_id: UUID) -> List[CommentResponse]:
        j = join(
            self.comments,
            self.establishments,
            self.comments.c.establishment_id == self.establishments.c.establishment_id
        )

        stmt = (select(
            self.comments,
            self.establishments.c.name.label('establishment_name'),
            self.establishments.c.rating.label('establishment_rating'))
                .select_from(j).where(self.comments.c.user_id == user_id)
                .order_by(self.comments.c.created_time.desc()))

        with self.get_connection() as conn:
            results = conn.execute(stmt).fetchall()
            return [CommentResponse(**row._asdict()) for row in results]

    def update_comment(self, comment: CommentUpdate) -> bool:
        update_data = {}
        if comment.rating is not None:
            update_data['rating'] = comment.rating
        if comment.text is not None:
            update_data['text'] = comment.text

        if not update_data:
            return False

        stmt = (update(self.comments)
                .where(self.comments.c.comment_id == comment.comment_id)
                .values(**update_data))

        with self.get_connection() as conn:
            result = conn.execute(stmt)
            return result.rowcount > 0

    def delete_comment(self, comment_id: UUID) -> bool:
        stmt = (delete(self.comments)
                .where(self.comments.c.comment_id == comment_id))

        with self.get_connection() as conn:
            result = conn.execute(stmt)
            return result.rowcount > 0

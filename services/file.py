from uuid import UUID
from database import get_session
from models.file import File
from typing import Optional
from sqlmodel import select, asc, desc, delete, exists, func
from schemas.file import FileFilter


class FileService:
    @classmethod
    def create_file(cls, name: str, path: str, size: int, content_type: str) -> File:
        file = File(name=name, path=path, size=size, content_type=content_type)
        with get_session() as session:
            session.add(file)
            session.commit()
            session.refresh(file)
        return file

    @classmethod
    def update_file(cls, file_id: UUID, name: Optional[str]) -> File:
        file = cls.ensure_file(file_id=file_id)
        with get_session() as session:
            file.name = name or file.name
            session.add(file)
            session.commit()
            session.refresh(file)
        return file

    @classmethod
    def update_file_status(cls, file_id: UUID) -> File:
        file = cls.ensure_file(file_id=file_id)
        with get_session() as session:
            session.add(file)
            session.commit()
            session.refresh(file)
        return file

    @classmethod
    def delete_file(cls, file_id: UUID) -> File:
        with get_session() as session:
            file = cls.ensure_file(file_id=file_id)
            session.delete(file)
            session.commit()
            return File

    @classmethod
    def delete_files(cls, file_ids: list[UUID]) -> None:
        with get_session() as session:
            stmt = delete(File).where(File.id.in_(file_ids))
            session.exec(stmt)
            session.commit()

    @staticmethod
    def _get_filter_query(query, filter: Optional[FileFilter] = None):
        if filter is None:
            return query
        if filter.id:
            query = query.where(File.id == UUID(str(filter.id)))
        if filter.name:
            query = query.where(File.name == filter.name)
        if filter.q:
            query = query.where(File.name.contains(filter.q))
        return query

    @staticmethod
    def _get_sort_query(
        query, sort_field: Optional[str] = None, sort_order: Optional[str] = None
    ):
        if not sort_field or sort_field == "id":
            query = query.order_by(desc(File.created_at))
            return query
        sort_col = getattr(File, sort_field, None)
        if sort_col is None:
            return query
        if sort_order and sort_order.lower() == "desc":
            query = query.order_by(desc(sort_col))
            return query
        query = query.order_by(asc(sort_col))
        return query

    @classmethod
    def get_files(
        cls,
        filter: Optional[FileFilter] = None,
        sort_field: Optional[str] = None,
        sort_order: Optional[str] = "asc",
        page: int = 1,
        per_page: int = 10,
    ) -> list[File]:
        query = select(File)

        query = cls._get_filter_query(query, filter=filter)

        query = cls._get_sort_query(query, sort_field=sort_field, sort_order=sort_order)

        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        with get_session() as session:
            return session.exec(query).all()

    @classmethod
    def get_files_count(
        cls,
        filter: Optional[FileFilter] = None,
    ) -> list[File]:
        query = select(func.count()).select_from(File)

        query = cls._get_filter_query(query, filter=filter)

        with get_session() as session:
            return session.exec(query).one()

    @classmethod
    def get_file(cls, file_id: UUID) -> Optional[File]:
        with get_session() as session:
            return session.exec(select(File).where(File.id == file_id)).one_or_none()

    @classmethod
    def get_files_by_file_ids(cls, file_ids: list[UUID]) -> list[File]:
        with get_session() as session:
            return session.exec(
                select(File).where(File.id.in_(file_ids), File.is_deleted == False)
            ).all()

    @classmethod
    def ensure_file_name(cls, name: str) -> bool:
        with get_session() as session:
            stmt = select(exists().where(File.name == name))
            return session.exec(stmt).one_or_none()

    @classmethod
    def ensure_file(cls, file_id: UUID) -> File:
        file = cls.get_file(file_id=file_id)
        if file is None:
            raise ValueError(f"file not found, id: {file_id}")
        return file

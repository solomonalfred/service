from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Base(DeclarativeBase):
    repr_attrs = ("id",)

    def __repr__(self):
        body = ", ".join(f"{a}={getattr(self, a)!r}" for a in self.repr_attrs)
        return f"<{self.__class__.__name__} {body}>"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

import uuid, enum, re
from datetime import date
from typing import Optional
from sqlalchemy.dialects.postgresql import UUID, VARCHAR
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    validates
)
from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    Enum,
    ForeignKey,
    String,
    UniqueConstraint,
    text
)

from src.db.base import Base
from src.core.constants import UserRole, UserType

class User(Base):
    __tablename__ = "users"

    type: Mapped[UserType] = mapped_column(Enum(UserType), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole),
                                           nullable=False,
                                           server_default=UserRole.employee.value)

    name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    shortname: Mapped[Optional[str]] = mapped_column(VARCHAR(255))

    tin: Mapped[Optional[str]] = mapped_column(String(12))
    ogrn: Mapped[Optional[str]] = mapped_column(String(15))
    kpp: Mapped[Optional[str]] = mapped_column(String(9))

    brand: Mapped[Optional[str]] = mapped_column(VARCHAR(255))
    manager_name: Mapped[Optional[str]] = mapped_column(VARCHAR(255))
    manager_position: Mapped[Optional[str]] = mapped_column(VARCHAR(255))

    passport: Mapped["PassportDetails"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    address: Mapped["Address"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    bank_details: Mapped["BankDetails"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    contacts: Mapped["Contacts"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    password_hash: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "(type NOT IN ('LE', 'IE', 'SE') "
            "OR tin IS NOT NULL)",
            name="chk_tin_required"
        ),
        CheckConstraint(
            "(type NOT IN ('LE', 'IE') "
            "OR ogrn IS NOT NULL)",
            name="chk_ogrn_required"
        ),
        CheckConstraint(
            "(type != 'LE' OR kpp IS NOT NULL)",
            name="chk_kpp_for_le"
        ),
    )

    PHONE_RE = re.compile(r"^(?:\+7|8)\d{10}$")
    EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

    @validates("tin")
    def _validate_tin(self, _, value):
        if value and len(value) not in (10, 12):
            raise ValueError("TIN must be 10 or 12 digits")
        return value

    @validates("ogrn")
    def _validate_ogrn(self, _, value):
        if value and len(value) not in (13, 15):
            raise ValueError("OGRN / OGRNIP must be 13 or 15 digits")
        return value

class PassportDetails(Base):
    __tablename__ = "passport_details"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True
    )

    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    series: Mapped[str] = mapped_column(String(4),  nullable=False)
    number: Mapped[str] = mapped_column(String(6),  nullable=False)
    passport_issued:Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    date_of_issued: Mapped[date] = mapped_column(Date, nullable=False)
    division_code: Mapped[str] = mapped_column(String(7), nullable=False)
    user: Mapped[User] = relationship(back_populates="passport")
    __repr_attrs__ = ("id", "user_id")

class Address(Base):
    __tablename__ = "address"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True
    )
    legal_address: Mapped[Optional[str]] = mapped_column(VARCHAR(500))
    registration_address: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    actual_address: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)

    user: Mapped[User] = relationship(back_populates="address")


class BankDetails(Base):
    __tablename__ = "bank_details"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True
    )
    bic: Mapped[str] = mapped_column(String(9),  nullable=False)
    bank_name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    correspondent_account: Mapped[str] = mapped_column(String(20), nullable=False)
    current_account: Mapped[str] = mapped_column(String(20), nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(VARCHAR(256))

    user: Mapped[User] = relationship(back_populates="bank_details")


class Contacts(Base):
    __tablename__ = "contacts"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True
    )

    personal_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    extra_phone: Mapped[Optional[str]] = mapped_column(String(20))
    public_phone: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    whatsapp: Mapped[Optional[str]] = mapped_column(String(50))
    telegram: Mapped[Optional[str]] = mapped_column(String(50))

    user: Mapped[User] = relationship(back_populates="contacts")
    PHONE_RE = User.PHONE_RE
    EMAIL_RE = User.EMAIL_RE

    @validates("personal_phone", "extra_phone", "public_phone", "whatsapp")
    def _phone_check(self, key, value):
        if value and not self.PHONE_RE.fullmatch(value):
            raise ValueError(f"{key} must be +7XXXXXXXXXX or 8XXXXXXXXXX")
        return value

    @validates("email")
    def _email_check(self, _, value):
        if not self.EMAIL_RE.fullmatch(value):
            raise ValueError("Invalid e-mail format")
        return value

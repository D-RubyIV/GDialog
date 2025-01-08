from datetime import datetime

import pytz
from sqlalchemy import DateTime, ForeignKey, create_engine, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.inspection import inspect

vietnam_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
current_time_in_vietnam = datetime.now(vietnam_timezone)


class PERMISSION:
    READ = "R"
    CREATE = "C"
    UPDATE = "U"


class BaseModel(DeclarativeBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        info={PERMISSION.READ: True, PERMISSION.CREATE: True, PERMISSION.UPDATE: True}
    )
    created_time: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=current_time_in_vietnam,
        info={PERMISSION.READ: True, PERMISSION.CREATE: True, PERMISSION.UPDATE: True}
    )
    updated_time: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=current_time_in_vietnam,
        onupdate=current_time_in_vietnam,
        info={PERMISSION.READ: True, PERMISSION.CREATE: True, PERMISSION.UPDATE: True}
    )

    @classmethod
    def get_filtered_allow_update(cls):
        return [col for col in cls.__mapper__.columns if col.info.get(PERMISSION.READ, False)]

    @classmethod
    def get_filtered_allow_create(cls):
        return [col for col in cls.__mapper__.columns if col.info.get(PERMISSION.CREATE, False)]

    @classmethod
    def get_filtered_allow_view(cls):
        return [col for col in cls.__mapper__.columns if col.info.get(PERMISSION.UPDATE, False)]


class LinkRecord(BaseModel):
    __tablename__ = "link"
    url: Mapped[str] = mapped_column(String(50), nullable=True)

    group_id: Mapped[int] = mapped_column(ForeignKey("group.id"), nullable=True)
    group: Mapped["GroupRecord"] = relationship("GroupRecord", back_populates="links", lazy="joined")


class GroupRecord(BaseModel):
    __tablename__ = "group"

    identifier: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        info={PERMISSION.READ: True, PERMISSION.CREATE: True, PERMISSION.UPDATE: True}
    )
    title: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        info={PERMISSION.READ: True, PERMISSION.CREATE: True, PERMISSION.UPDATE: True}
    )
    username: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        info={PERMISSION.READ: True, PERMISSION.CREATE: True, PERMISSION.UPDATE: True}
    )
    restricted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=True,
        info={PERMISSION.READ: True, PERMISSION.CREATE: True, PERMISSION.UPDATE: True}
    )
    megagroup: Mapped[bool] = mapped_column(
        Boolean,
        nullable=True,
        info={PERMISSION.READ: True, PERMISSION.CREATE: False, PERMISSION.UPDATE: True}
    )
    gigagroup: Mapped[bool] = mapped_column(
        Boolean,
        nullable=True,
        info={PERMISSION.READ: True, PERMISSION.CREATE: True, PERMISSION.UPDATE: True}
    )

    links: Mapped[list["LinkRecord"]] = relationship("LinkRecord", back_populates="group", lazy="joined")

    def __repr__(self):
        return f"GroupRecord(id={self.id}, identifier={self.identifier}, title={self.title}, username={self.username}, restricted={self.restricted}, megagroup={self.megagroup}, gigagroup={self.gigagroup})"


print([col.name for col in GroupRecord.get_filtered_allow_update()])

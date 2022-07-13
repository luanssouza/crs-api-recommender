from sqlalchemy import Boolean, Column, DateTime, Integer, SmallInteger, String, func

from ..util.database import Base

class Dialog(Base):
    __tablename__ = "dialog"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegramId = Column(Integer, nullable=False)
    age = Column(SmallInteger, nullable=False)
    authorization = Column(Boolean, nullable=False)
    property = Column(String(50))
    object = Column(String(50))
    createdAt = Column(DateTime(timezone=True), default=func.now())
    updatedAt = Column(DateTime(timezone=True))
    
    @classmethod
    def fromdict(self, telegramId, age, authorization):
        instance = self()
        
        instance.telegramId = telegramId
        instance.age = age
        instance.authorization = authorization

        return instance

    @classmethod
    def fromdict(self, id):
        instance = self()
        
        instance.id = id

        return instance
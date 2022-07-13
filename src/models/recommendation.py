from numpy import recarray
from sqlalchemy import Boolean, Column, DateTime, Integer, ForeignKey, String, func
from sqlalchemy.sql.sqltypes import JSON

from ..util.database import Base

class Recommendation(Base):
    __tablename__ = "recommendation"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    dialogId = Column(Integer, ForeignKey("dialog.id"), nullable=False)
    movieId = Column(Integer, nullable=False)
    imdbId = Column(String(10))
    properties = Column(JSON)
    requested = Column(Boolean, default=False)
    created = Column(DateTime(timezone=True), default=func.now())

    @classmethod
    def fromdict(self, dialogId, movieId, imdbId, properties, requested = False):
        instance = self()
        
        instance.dialogId = dialogId
        instance.movieId = movieId
        instance.imdbId = imdbId
        instance.properties = properties
        instance.requested = requested

        return instance
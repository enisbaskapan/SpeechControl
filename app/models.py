from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from app import Base

class Sentence(Base):
    __tablename__ = 'ner_sentence'
    __table_args__ = ({"schema": "speech_control"})

    id = Column(Integer, primary_key=True)
    sentence = Column(String)

    def __repr__(self):
       return "<Sentence(id='%d', sentence='%s')>" % (
                               self.id, self.sentence)

class Words(Base):
    
    __tablename__ = 'ner_words'
    __table_args__ = ({"schema": "speech_control"})
    
    id = Column(Integer, primary_key=True)
    start_index = Column(Integer, nullable=False)
    end_index = Column(Integer, nullable=False)
    tag = Column(String)

    sentence_id = Column(Integer, ForeignKey('speech_control.ner_sentence.id'))
    sentence = relationship("Sentence", backref=backref('words'))

    def __repr__(self):
        return "<Words(tag='%s')>" % self.tag
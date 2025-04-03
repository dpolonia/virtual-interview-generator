from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import datetime
import os

Base = declarative_base()

class Persona(Base):
    __tablename__ = 'personas'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    role = Column(String, nullable=False)
    age = Column(Integer)
    position = Column(String)
    company = Column(String)
    experience = Column(Integer)
    education = Column(String)
    background = Column(Text)
    expertise = Column(Text)
    communication_style = Column(Text)
    ai_views = Column(Text)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Interview(Base):
    __tablename__ = 'interviews'
    
    id = Column(Integer, primary_key=True)
    interviewer_id = Column(Integer, ForeignKey('personas.id'))
    interviewee_id = Column(Integer, ForeignKey('personas.id'))
    category = Column(String, nullable=False)
    model_used = Column(String, nullable=False)
    raw_interview = Column(Text)
    xml_formatted = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    interviewer = relationship("Persona", foreign_keys=[interviewer_id])
    interviewee = relationship("Persona", foreign_keys=[interviewee_id])

class Analysis(Base):
    __tablename__ = 'analyses'
    
    id = Column(Integer, primary_key=True)
    interview_id = Column(Integer, ForeignKey('interviews.id'))
    key_points = Column(Text)
    notable_quotes = Column(Text)
    ai_attitudes = Column(Text)
    rq1_insights = Column(Text)
    rq2_insights = Column(Text)
    rq3_insights = Column(Text)
    rq4_insights = Column(Text)
    contradictions = Column(Text)
    authenticity_assessment = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class DatabaseManager:
    def __init__(self, db_path='sqlite:///data/interviews.db'):
        self.engine = create_engine(db_path)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_session(self):
        return self.Session()
    
    def create_persona(self, persona_data):
        """Create a new persona in the database."""
        session = self.get_session()
        try:
            persona = Persona(**persona_data)
            session.add(persona)
            session.commit()
            return persona.id
        finally:
            session.close()
    
    def get_personas_by_category(self, category, role=None):
        """Fetch all personas for a specific category and optionally role."""
        session = self.get_session()
        try:
            query = session.query(Persona).filter_by(category=category)
            if role:
                query = query.filter_by(role=role)
            personas = query.all()
            return personas
        finally:
            session.close()
    
    def create_interview(self, interviewer_id, interviewee_id, category, model_used, raw_interview, xml_formatted):
        """Create a new interview record."""
        session = self.get_session()
        try:
            interview = Interview(
                interviewer_id=interviewer_id,
                interviewee_id=interviewee_id,
                category=category,
                model_used=model_used,
                raw_interview=raw_interview,
                xml_formatted=xml_formatted
            )
            session.add(interview)
            session.commit()
            return interview.id
        finally:
            session.close()
    
    def create_analysis(self, interview_id, analysis_data):
        """Create a new analysis record."""
        session = self.get_session()
        try:
            analysis = Analysis(interview_id=interview_id, **analysis_data)
            session.add(analysis)
            session.commit()
            return analysis.id
        finally:
            session.close()

# Initialize the database when imported
db_manager = DatabaseManager()
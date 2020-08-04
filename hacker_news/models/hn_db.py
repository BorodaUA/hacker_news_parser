from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    JSON,
    DateTime,
    Boolean,
    ForeignKey,
    MetaData,
)
from sqlalchemy.orm import relationship

Base = declarative_base()


class HackerNewsTopStory(Base):
    __bind_key__ = "hacker_news"
    __tablename__ = "hacker_news_top_story"
    #
    id = Column(Integer, primary_key=True, nullable=False)
    deleted = Column(Boolean)
    type = Column(String)
    by = Column(String)
    time = Column(Integer)
    text = Column(String)
    dead = Column(Boolean)
    parent = Column(Integer)
    poll = Column(Integer)
    kids = Column(JSON)
    url = Column(String)
    score = Column(Integer)
    title = Column(String)
    parts = Column(JSON)
    descendants = Column(Integer)
    #
    comments = relationship(
        "HackerNewsTopStoryComment",
        backref="hacker_news_top_story",
        order_by="desc(HackerNewsTopStoryComment.id)",
    )
    #
    origin = Column(String)
    parsed_time = Column(DateTime)


class HackerNewsTopStoryComment(Base):
    __bind_key__ = "hacker_news"
    __tablename__ = "hacker_news_top_story_comment"
    #
    id = Column(Integer, primary_key=True, nullable=False)
    deleted = Column(Boolean)
    type = Column(String)
    by = Column(String)
    time = Column(Integer)
    text = Column(String)
    dead = Column(Boolean)
    parent = Column(Integer, ForeignKey("hacker_news_top_story.id"))
    poll = Column(Integer)
    kids = Column(JSON)
    url = Column(String)
    score = Column(Integer)
    title = Column(String)
    parts = Column(JSON)
    descendants = Column(Integer)
    #
    origin = Column(String)
    parsed_time = Column(DateTime)


class HackerNewsNewStory(Base):
    __bind_key__ = "hacker_news"
    __tablename__ = "hacker_news_new_story"
    #
    id = Column(Integer, primary_key=True, nullable=False)
    deleted = Column(Boolean)
    type = Column(String)
    by = Column(String)
    time = Column(Integer)
    text = Column(String)
    dead = Column(Boolean)
    parent = Column(Integer)
    poll = Column(Integer)
    kids = Column(JSON)
    url = Column(String)
    score = Column(Integer)
    title = Column(String)
    parts = Column(JSON)
    descendants = Column(Integer)
    comments = relationship(
        "HackerNewsNewStoryComment",
        backref="hacker_news_new_story",
        order_by="desc(HackerNewsNewStoryComment.id)",
    )
    origin = Column(String)
    parsed_time = Column(DateTime)


class HackerNewsNewStoryComment(Base):
    __bind_key__ = "hacker_news"
    __tablename__ = "hacker_news_new_story_comment"
    #
    id = Column(Integer, primary_key=True, nullable=False)
    deleted = Column(Boolean)
    type = Column(String)
    by = Column(String)
    time = Column(Integer)
    text = Column(String)
    dead = Column(Boolean)
    parent = Column(Integer, ForeignKey("hacker_news_new_story.id"))
    poll = Column(Integer)
    kids = Column(JSON)
    url = Column(String)
    score = Column(Integer)
    title = Column(String)
    parts = Column(JSON)
    descendants = Column(Integer)
    #
    origin = Column(String)
    parsed_time = Column(DateTime)

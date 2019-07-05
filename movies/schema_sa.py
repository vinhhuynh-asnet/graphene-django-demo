# Define graphql schema to work SQLAlchemy
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from sqlalchemy import Column, Integer, String, ARRAY
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# SQLAlchemy Models
class ActorModel(Base):
    __tablename__ = 'actor'
    id = Column(Integer, primary_key=True)
    name = Column(String)

class MovieModel(Base):
    __tablename__ = 'movie'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    year = Column(String)
    # actors = Column(ARRAY)


# Define Types
class ActorType(SQLAlchemyObjectType):
    class Meta:
        model = ActorModel
        # only return specified fields
        only_fields = ('name',)

class MovieType(SQLAlchemyObjectType):
    class Meta:
        model = MovieModel
        # only return specified fields
        only_fields = ('title', 'year',)

# Build Query
class Query(graphene.ObjectType):
    actors = graphene.List(ActorType)
    actor = graphene.Field(ActorType, id=graphene.Int())

    def resolve_actor(self, info, id):
        query = ActorType.get_query(info)  # SQLAlchemy query
        return query.all()

    def resolve_actors(self, info):
        query = ActorType.get_query(info)  # SQLAlchemy query
        return query.all()

schema = graphene.Schema(query=Query)
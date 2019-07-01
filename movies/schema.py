import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from movies import models

# Create GraphQL Types for the following models
# Simply, just binding to django model
class ActorType(DjangoObjectType):
    class Meta:
        model = models.Actor

class MovieType(DjangoObjectType):
    class Meta:
        model = models.Movie

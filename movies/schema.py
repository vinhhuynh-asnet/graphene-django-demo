import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from movies.models import Actor, Movie

#########################################################################
# Create GraphQL Types for the following models
#########################################################################
# Simply, just binding to django model
class ActorType(DjangoObjectType):
    class Meta:
        model = Actor

class MovieType(DjangoObjectType):
    class Meta:
        model = Movie

# Next, continue creating the Query Type
class Query(ObjectType):
    actor = graphene.Field(ActorType, id=graphene.Int())
    movie = graphene.Field(MovieType, id=graphene.Int())
    actors = graphene.List(ActorType)
    movies = graphene.List(MovieType)

    def resolve_actor(self, info, id):
        if id is not None:
            return Actor.objects.get(pk=id)
        return None

    def resolve_movie(self, info, id):
        if id is not None:
            return Movie.objects.get(pk=id)
        return None

    def resolve_actors(self, info):
        return Actor.objects.all()

    def resolve_movies(self, info):
        return Movie.objects.all()

#########################################################################
# Define the Inputs
#########################################################################
class ActorInput(graphene.InputObjectType):
    id = graphene.ID()
    name = graphene.String()

class MovieInput(graphene.InputObjectType):
    id = graphene.ID()
    title = graphene.String()
    actors = graphene.List(ActorInput)
    year = graphene.Int()

#########################################################################
# Define the Mutations
#########################################################################
# The Class Name corresponds to the GraphQL's query name
class CreateActor(graphene.Mutation):
    # The Mutators Arguments
    class Arguments():
        input = ActorInput(required=True)

    # Define Payloads: ok and actor
    ok = graphene.Boolean
    actor = graphene.Field(ActorType)

    # Control the execution
    @staticmethod
    def mutate(root, info, input=None):
        ok = True
        actor_instance = Actor(name=input.name)
        actor_instance.save()
        return CreateActor(ok=ok, actor=actor_instance)

class UpdateActor(graphene.Mutation):
    # The Mutator Arguments
    class Arguments:
        id = graphene.Int(required=True)
        input = ActorInput(required=True)

    # Payloads
    ok = graphene.Boolean()
    actor = graphene.Field(ActorType)

    # Control the execution
    @staticmethod
    def mutate(root, info, id, input=None):
        ok = False
        actor_instance = Actor.objects.get(pk=id)

        if actor_instance:
            ok = True
            actor_instance.name = input.name
            actor_instance.save()
            return UpdateActor(ok=ok, actor=actor_instance)

        return UpdateActor(ok=ok, actor=None)

# Create mutations for movies
class CreateMovie(graphene.Mutation):
    class Arguments:
        input = MovieInput(required=True)

    ok = graphene.Boolean()
    movie = graphene.Field(MovieType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = True
        actors = []
        for actor_input in input.actors:
          actor = Actor.objects.get(pk=actor_input.id)
          if actor is None:
            return CreateMovie(ok=False, movie=None)
          actors.append(actor)
        movie_instance = Movie(
          title=input.title,
          year=input.year
          )
        movie_instance.save()
        movie_instance.actors.set(actors)
        return CreateMovie(ok=ok, movie=movie_instance)


class UpdateMovie(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = MovieInput(required=True)

    ok = graphene.Boolean()
    movie = graphene.Field(MovieType)

    @staticmethod
    def mutate(root, info, id, input=None):
        ok = False
        movie_instance = Movie.objects.get(pk=id)
        if movie_instance:
            ok = True
            actors = []
            for actor_input in input.actors:
              actor = Actor.objects.get(pk=actor_input.id)
              if actor is None:
                return UpdateMovie(ok=False, movie=None)
              actors.append(actor)
            movie_instance.title=input.title
            movie_instance.year=input.year

            # Need to save before set actors into movie_instance
            # For resolving the many-to-many relationship
            movie_instance.save()
            movie_instance.actors.set(actors)
            return UpdateMovie(ok=ok, movie=movie_instance)
        return UpdateMovie(ok=ok, movie=None)

class Mutation(graphene.ObjectType):
    create_actor = CreateActor.Field()
    update_actor = UpdateActor.Field()
    create_movie = CreateMovie.Field()
    update_movie = UpdateMovie.Field()

#########################################################################
# Define Schema, include in: Query & Mutation
#########################################################################
schema = graphene.Schema(query=Query, mutation=Mutation)
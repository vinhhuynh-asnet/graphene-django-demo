import graphene
from graphene import relay
from graphql_relay import from_global_id
from graphene_django.types import DjangoObjectType, ObjectType
from graphene_django.filter import DjangoFilterConnectionField
from movies.models import Actor, Movie

#########################################################################
# Create GraphQL Types for the following models
#########################################################################
# Simply, just binding to django model
class ActorType(DjangoObjectType):
    class Meta:
        model = Actor
        filter_fields = {
            'name': ['exact', 'istartswith',],
        }
        interfaces = (relay.Node, )

class MovieType(DjangoObjectType):
    class Meta:
        model = Movie
        filter_fields = {
            'title': ['exact', 'istartswith', 'icontains',],
            'year': ['exact'],
        }
        interfaces = (relay.Node, )

# Next, continue creating the Query Type
class Query(ObjectType):
    actor = graphene.Field(ActorType, id=graphene.Int())
    movie = graphene.Field(MovieType, id=graphene.Int())
    # actors = graphene.List(ActorType)
    # movies = graphene.List(MovieType)
    # actor = relay.Node.Field(ActorType)
    # movie = relay.Node.Field(MovieType)
    actors = DjangoFilterConnectionField(ActorType)
    movies = DjangoFilterConnectionField(MovieType)

    def resolve_actor(self, info, **kwargs):
        id = kwargs.get('id', None)

        if id is not None:
            return Actor.objects.get(pk=id)
        return None

    def resolve_movie(self, info, **kwargs):
        id = kwargs.get('id', None)

        if id is not None:
            return Movie.objects.get(pk=id)
        return None

    def resolve_actors(self, info, **kwargs):
        return Actor.objects.all()

    def resolve_movies(self, info, **kwargs):
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

    # Payloads
    ok = graphene.Boolean()
    actor = graphene.Field(ActorType)

    # Control the execution
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

    # Control the execution
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

    # Payloads
    ok = graphene.Boolean()
    movie = graphene.Field(MovieType)

    # Control the execution
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


#########################################################################
# Define the Relay Mutations
#########################################################################
class RelayCreateActor(relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)

    ok = graphene.Boolean()
    actor = graphene.Field(ActorType)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        print('inputs: ', input)
        name = input.get('name')
        ok = True
        actor_instance = Actor(name=name)
        actor_instance.save()
        return CreateActor(ok=ok, actor=actor_instance)

class RelayUpdateActor(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)

    ok = graphene.Boolean()
    actor = graphene.Field(ActorType)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        id = input.get('id', None)
        name = input.get('name', None)

        if not id:
            return UpdateActor(ok=False, actor=None)

        ok = True
        actor_instance = Actor.objects.get(pk=id)
        actor_instance.name = name
        actor_instance.save()
        return CreateActor(ok=ok, actor=actor_instance)

class RelayCreateMovie(relay.ClientIDMutation):
    class Input:
        title = graphene.String(required=True)
        year = graphene.Int(required=True)
        actors = graphene.List(ActorInput)

    ok = graphene.Boolean()
    movie = graphene.Field(MovieType)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        title = input.get('title')
        year = input.get('year')
        actors_input = input.get('actors', [])
        input_ids = []

        for actor_input in actors_input:
            if not actor_input:
                return RelayCreateMovie(ok=False, movie=None)
            input_ids.append(actor_input.get('id'))

        movie_instance = Movie(
            title=title,
            year=year,
        )
        movie_instance.save()
        actors = Actor.objects.filter(pk__in=input_ids)
        movie_instance.actors.set(actors)
        return RelayCreateMovie(ok=True, movie=movie_instance)

class Mutation(graphene.ObjectType):
    create_actor = CreateActor.Field()
    update_actor = UpdateActor.Field()
    create_movie = CreateMovie.Field()
    update_movie = UpdateMovie.Field()
    relay_create_actor = RelayCreateActor.Field()
    relay_update_actor = RelayUpdateActor.Field()
    relay_create_movie = RelayCreateMovie.Field()
    # relay_update_movie = RelayUpdateMovie.Field()

#########################################################################
# Define Schema, include in: Query & Mutation
#########################################################################
schema = graphene.Schema(query=Query, mutation=Mutation)
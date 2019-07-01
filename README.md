# graphene-django-demo
This is repository serves demo for using graphene on django and django rest framework

## TECHNICAL STACKS:
* Python v3.7.2
* Django v2.2
* GraphQL with graphene v2.1.6

### Make some installations:
* pip install -r requirements.txt

### Create database
* createdb demo

### How to run
* Apply testing data: `python manage.py loaddata movies.json`
* Running server: `python manage.py runserver`
* Running testing on graphql: `http://localhost:8000/graphql/`

### Some GraphQL sample queries: `refer file queries.graphql`


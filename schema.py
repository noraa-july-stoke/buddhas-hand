from graphql import GraphQLSchema, GraphQLObjectType, GraphQLField, GraphQLString

query_type = GraphQLObjectType(
    name="Query",
    fields={
        "hello": GraphQLField(GraphQLString, resolver=lambda obj, info: "world")
    }
)

schema = GraphQLSchema(query=query_type)

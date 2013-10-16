# If you have not yet seen the source in matching_queries_to_indexes/main.py and
# custom_alias_properties/main.py, please take a look.

# In this sample we define an EndpointsAliasProperty which does not override
# one of the helper properties provided by EndpointsModel; this is a first as
# all the other samples have simply tweaked existing alias properties. We use
# this property in conjuction with another alias property to define entity keys
# which have an ancestor -- for example ndb.Key(MyParent, ..., MyModel, ...) --
# which is slightly more complex than the keys we have seen so far.

# We define an extra model MyParent to hold all the data for the ancestors being
# used (though this is not strictly necessary, an ancestor key does not need to
# exist in the datastore to be used). In addition, since we will be requiring
# that a MyParent entity exists to be used as an ancestor, we provide a method
# MyParentInsert to allow API users to create or update parent objects.

import endpoints

from google.appengine.ext import ndb
from protorpc import remote

# See matching_queries_to_indexes/main.py for reference on this import.
from endpoints_proto_datastore.ndb import EndpointsAliasProperty
from endpoints_proto_datastore.ndb import EndpointsModel


class MyParent(EndpointsModel):
  # As in simple_get/main.py, by setting _message_fields_schema, we can set a
  # custom ProtoRPC message schema. We set the schema to the alias property
  # "name" and ignore the NDB property updated.
  _message_fields_schema = ('name',)

  updated = ndb.DateTimeProperty(auto_now=True)

  # This is a setter which will be used by the alias property "name".
  def NameSet(self, value):
    # The property "name" is a string field, so we expect a value passed in from
    # a ProtoRPC message to be a string. Since (as seen below), "name" is
    # required, we also need not worry about the case that the value is None.
    if not isinstance(value, basestring):
      raise TypeError('Name must be a string.')
    # We update the key using the name.
    self.UpdateFromKey(ndb.Key(MyParent, value))

  # This EndpointsAliasProperty is used for the property "name". It is required,
  # meaning that a value must always be set if the corresponding field is
  # contained in a ProtoRPC message schema.

  # Since no property_type is specified, the default value of
  # messages.StringField is used.

  # See matching_queries_to_indexes/main.py for more information on
  # EndpointsAliasProperty.
  @EndpointsAliasProperty(setter=NameSet, required=True)
  def name(self):
    # First check if the entity has a key.
    if self.key is not None:
      # If the entity has a key, return only the string_id since the property is
      # a string field.
      return self.key.string_id()


class MyModel(EndpointsModel):
  # These values are placeholders to be used when a key is created; the _parent
  # will be used as the ancestor and the _id as the ID. For example:
  #  ndb.Key(MyParent, _parent, MyModel, _id)
  # Since these values will be set by alias properties which are not set
  # simultaneously, we need to hold them around until both are present before we
  # can create a key from them.
  _parent = None
  _id = None

  attr1 = ndb.StringProperty()
  attr2 = ndb.StringProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)

  # This is a helper method that will set the key on the entity only if both the
  # parent and ID are present. It will be used by property setters that provide
  # values for _parent and _id.
  def SetKey(self):
    # Can only set the key if both the parent and the child ID are set.
    if self._parent is not None and self._id is not None:
      key = ndb.Key(MyParent, self._parent, MyModel, self._id)
      # Will set the key and attempt to update the entity if it exists.
      self.UpdateFromKey(key)

  # This is a helper method that will set the _parent and _id values using the
  # entity key, if it exists. It will be used by property getters that retrieve
  # the current values of _parent and _id.
  def SetParts(self):
    # If there is no key, nothing can be set.
    if self.key is not None:
      # If there are not two tuples in the key pairs, a ValueError will occur.
      parent_pair, id_pair = self.key.pairs()
      # Each pair in key pairs will be a tuple (model kind, value) where model
      # kind is a string representing the name of the model and value is the
      # actual string or integer ID that was set.
      self._parent = parent_pair[1]
      self._id = id_pair[1]

  # This is a setter which will be used by the alias property "parent". This
  # method will be called when parent is set from a ProtoRPC request.
  def ParentSet(self, value):
    # The property "parent" is a string field, so we expect a value passed in
    # from a ProtoRPC message to be a string. Since (as seen below), "parent" is
    # required, we also need not worry about the case that the value is None.
    if not isinstance(value, basestring):
      raise TypeError('Parent name must be a string.')

    self._parent = value
    # After setting the value, we must make sure the parent exists before it can
    # be used as an ancestor.
    if ndb.Key(MyParent, value).get() is None:
      # If the MyParent key does not correspond to an entity in the datastore,
      # we return an HTTP 404 Not Found.
      raise endpoints.NotFoundException('Parent %s does not exist.' % value)
    # The helper method SetKey is called to set the entity key if the _id has
    # also been set already.
    self.SetKey()

    # If the "parent" property is used in a query method, we want the ancestor
    # of the query to be the parent key.
    self._endpoints_query_info.ancestor = ndb.Key(MyParent, value)

  # This EndpointsAliasProperty is used to get and set a parent for our entity
  # key. It is required, meaning that a value must always be set if the
  # corresponding field is contained in a ProtoRPC message schema.

  # Since no property_type is specified, the default value of
  # messages.StringField is used.

  # See matching_queries_to_indexes/main.py for more information on
  # EndpointsAliasProperty.
  @EndpointsAliasProperty(setter=ParentSet, required=True)
  def parent(self):
    # If _parent has not already been set on the entity, try to set it.
    if self._parent is None:
      # Using the helper method SetParts, _parent will be set if a valid key has
      # been set on the entity.
      self.SetParts()
    return self._parent

  # This is a setter which will be used by the alias property "id". This
  # method will be called when id is set from a ProtoRPC request. This replaces
  # the helper property "id" provided by EndpointsModel, but does not use any of
  # the functionality from that method.
  def IdSet(self, value):
    # The property "id" is a string field, so we expect a value passed in from a
    # ProtoRPC message to be a string. Since (as seen below), "id" is required,
    # we also need not worry about the case that the value is None.
    if not isinstance(value, basestring):
      raise TypeError('ID must be a string.')

    self._id = value
    # The helper method SetKey is called to set the entity key if the _parent
    # has also been set already.
    self.SetKey()

  # This EndpointsAliasProperty is used to get and set an id value for our
  # entity key. It is required, meaning that a value must always be set if the
  # corresponding field is contained in a ProtoRPC message schema.

  # Since no property_type is specified, the default value of
  # messages.StringField is used.

  # See matching_queries_to_indexes/main.py for more information on
  # EndpointsAliasProperty.
  @EndpointsAliasProperty(setter=IdSet, required=True)
  def id(self):
    # If _id has not already been set on the entity, try to set it.
    if self._id is None:
      # Using the helper method SetParts, _id will be set if a valid key has
      # been set on the entity.
      self.SetParts()
    return self._id


@endpoints.api(name='myapi', version='v1', description='My Little API')
class MyApi(remote.Service):

  # This method is not defined in any of the previous examples; it allows a
  # parent entity to be inserted so that it can be used as an ancestor. Since
  # the ProtoRPC message schema for MyParent is a single field "name", this will
  # be all that is contained in the request and the response.
  @MyParent.method(path='myparent', http_method='POST',
                   name='myparent.insert')
  def MyParentInsert(self, my_parent):
    # Though we don't actively change the model passed in, the value of updated
    # is set to the current time. No check is performed to see if the MyParent
    # entity already exists, since the values other than the name (set in the
    # key) are not relevant.
    my_parent.put()
    return my_parent

  # Since we require MyModel instances also have a MyParent ancestor, we include
  # "parent" in the request path by setting path='mymodel/{parent}'. Since "id"
  # is also required, an "id" must be included in the request body or it will be
  # rejected by ProtoRPC before this method is called.
  @MyModel.method(path='mymodel/{parent}', http_method='POST',
                  name='mymodel.insert')
  def MyModelInsert(self, my_model):
    # If the entity already exists (as evidenced by from_datastore equal to
    # True), an HTTP 400 Bad Request is returned. Since both "parent" and "id"
    # are required fields, both _parent and _id will be set on the entity and
    # MyModel.SetKey must have been called.

    # Checking in this fashion is not truly safe against duplicates. To do this,
    # a datastore transaction would be necessary.
    if my_model.from_datastore:
      raise endpoints.BadRequestException(
          'MyModel %s with parent %s already exists.' %
          (my_model.id, my_model.parent))
    my_model.put()
    return my_model

  # To make sure queries have a specified ancestor, we use the alias property
  # "parent" which we defined on MyModel and specify query_fields equal to
  # ('parent',). To specify the parent in the query, it is included in the path
  # as it was in MyModelInsert. So no query parameters will be required, simply
  # a request to
  #   .../mymodels/someparent
  # where ... is the full path to the API.
  @MyModel.query_method(query_fields=('parent',),
                        path='mymodels/{parent}', name='mymodel.list')
  def MyModelList(self, query):
    return query


application = endpoints.api_server([MyApi], restricted=False)

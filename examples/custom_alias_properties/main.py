# If you have not yet seen the source in simple_get/main.py, please take a look.

# In this sample, we override two of the helper properties provided by
# EndpointsModel: id and order. The purpose of this sample is to understand
# how these properties -- called alias properties -- are used. For more
# reference on EndpointsAliasProperty, see matching_queries_to_indexes/main.py
# and keys_with_ancestors/main.py.

import endpoints

from google.appengine.ext import ndb
from protorpc import remote

# See matching_queries_to_indexes/main.py for reference on this import.
from endpoints_proto_datastore.ndb import EndpointsAliasProperty
from endpoints_proto_datastore.ndb import EndpointsModel


# The helper property "order" provided by EndpointsModel has no default value,
# but we can provide it with this one, which will result in ordering a query
# first by attr1 and then attr2 in descending order. To ensure queries using
# this order do not fail, we specify the equivalent index in index.yaml.
DEFAULT_ORDER = 'attr1,-attr2'


class MyModel(EndpointsModel):
  # As in simple_get/main.py, by setting _message_fields_schema, we can set a
  # custom ProtoRPC message schema. We set the schema to the alias property
  # "id" -- which we override here -- and the three properties corresponding to
  # the NDB properties and exclude the fifth property, which is the alias
  # property "order".

  # The property "order" is excluded since we defined our own schema but would
  # have been included otherwise. We have observed that the helper property
  # "order" from EndpointsModel is not included in the ProtoRPC message schema
  # when _message_fields_schema is not present, but this case does not
  # contradict that fact. When "order" (or any of the other four helper
  # properties) is overridden, it is treated like any other NDB or alias
  # property and is included in the schema.
  _message_fields_schema = ('id', 'attr1', 'attr2', 'created')

  attr1 = ndb.StringProperty()
  attr2 = ndb.StringProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)

  # This is a setter which will be used by the helper property "id", which we
  # are overriding here. The setter used for that helper property is also named
  # IdSet. This method will be called when id is set from a ProtoRPC query
  # request.
  def IdSet(self, value):
    # By default, the property "id" assumes the "id" will be an integer in a
    # simple key -- e.g. ndb.Key(MyModel, 10) -- which is the default behavior
    # if no key is set. Instead, we wish to use a string value as the "id" here,
    # so first check if the value being set is a string.
    if not isinstance(value, basestring):
      raise TypeError('ID must be a string.')
    # We call UpdateFromKey, which each of EndpointsModel.IdSet and
    # EndpointsModel.EntityKeySet use, to update the current entity using a
    # datastore key. This method sets the key on the current entity, attempts to
    # retrieve a corresponding entity from the datastore and then patch in any
    # missing values if an entity is found in the datastore.
    self.UpdateFromKey(ndb.Key(MyModel, value))

  # This EndpointsAliasProperty is our own helper property and overrides the
  # original "id". We specify the setter as the function IdSet which we just
  # defined. We also set required=True in the EndpointsAliasProperty decorator
  # to signal that an "id" must always have a value if it is included in a
  # ProtoRPC message schema.

  # Since no property_type is specified, the default value of
  # messages.StringField is used.

  # See matching_queries_to_indexes/main.py for more information on
  # EndpointsAliasProperty.
  @EndpointsAliasProperty(setter=IdSet, required=True)
  def id(self):
    # First check if the entity has a key.
    if self.key is not None:
      # If the entity has a key, return only the string_id. The method id()
      # would return any value, string, integer or otherwise, but we have a
      # specific type we wish to use for the entity "id" and that is string.
      return self.key.string_id()

  # This EndpointsAliasProperty only seeks to override the default value used by
  # the helper property "order". Both the original getter and setter are used;
  # the first by setter=EndpointsModel.OrderSet and the second by using super
  # to call the original getter. The argument default=DEFAULT_ORDER is used to
  # augment the EndpointsAliasProperty decorator by specifying a default value.
  # This value is used by the corresponding ProtoRPC field to set a value if
  # none is set by the request. Therefore, if a query has no order, rather than
  # a basic query, the order of DEFAULT_ORDER will be used.

  # Since no property_type is specified, the default value of
  # messages.StringField is used.
  @EndpointsAliasProperty(setter=EndpointsModel.OrderSet, default=DEFAULT_ORDER)
  def order(self):
    # Use getter from parent class.
    return super(MyModel, self).order


@endpoints.api(name='myapi', version='v1', description='My Little API')
class MyApi(remote.Service):

  # Since "id" is required, we require that the request contain an "id" to be
  # set on the entity. Rather than being specified in the POST body, we ask that
  # the "id" be sent in the request by setting path='mymodel/{id}'. To insert
  # a new value with id equal to cheese we would submit a request to
  #   .../mymodel/cheese
  # where ... is the full path to the API.
  @MyModel.method(path='mymodel/{id}', http_method='POST',
                  name='mymodel.insert')
  def MyModelInsert(self, my_model):
    # If the API user is trying to insert an entity which already exists in the
    # datastore (as evidenced by from_datastore being True) then we return an
    # HTTP 400 Bad request saying the entity already exists. We only want users
    # to be able to insert new entities, not to overwrite existing ones.

    # See simple_get/main.py for more about from_datastore.
    if my_model.from_datastore:
      # We can use the entity name by retrieving the string_id, since we know
      # our overridden definition of "id" ensures the string_id is set.
      name = my_model.key.string_id()
      # We raise an exception which results in an HTTP 400.
      raise endpoints.BadRequestException(
          'MyModel of name %s already exists.' % (name,))
    # If the entity does not already exist, insert it into the datastore. Since
    # the key is set when UpdateFromKey is called within IdSet, the "id" of the
    # inserted entity will be the value passed in from the request.
    my_model.put()
    return my_model

  # To use the helper property "order" that we defined, we specify query_fields
  # equal to ('order',) in the MyModel.query_method decorator. This will result
  # in a single string field in the ProtoRPC message schema. If no "order" is
  # specified in the query, the default value from the "order" property we
  # defined will be used instead.
  @MyModel.query_method(query_fields=('order',),
                        path='mymodels', name='mymodel.list')
  def MyModelList(self, query):
    return query


application = endpoints.api_server([MyApi], restricted=False)

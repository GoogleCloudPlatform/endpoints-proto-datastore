# If you have not yet seen the source in basic_with_auth/main.py and
# paging/main.py, please take a look.

# In this sample we use a custom Enum for the "order" property in queries
# to strictly control the indexes used and make sure we have corresponding
# indexes created in index.yaml.

import endpoints

from google.appengine.ext import ndb
# This import allows us to define our own Enum using the ProtoRPC messages
# library. This is not usually needed, since EndpointsModel handles message
# definition, but in this case it is.
from protorpc import messages
from protorpc import remote

# We import EndpointsAliasProperty so that we can define our own helper property
# similar to the properties "id", "entityKey", "limit", "order" and "pageToken"
# provided by EndpointsModel.
from endpoints_proto_datastore.ndb import EndpointsAliasProperty
from endpoints_proto_datastore.ndb import EndpointsModel


# This is an Enum used to strictly define which order values are allowed.
# In this case, we are only allowing two query orders and have an enum value
# corresponding to each.
class Order(messages.Enum):
  MYFIRST = 1
  MYSECOND = 2


class MyModel(EndpointsModel):
  # As in simple_get/main.py, by setting _message_fields_schema, we can set a
  # custom ProtoRPC message schema. We set the schema to the four properties
  # corresponding to the NDB properties and exclude the fifth property, which is
  # the alias property "order". Though the helper property "order" from
  # EndpointsModel is not included in the message schema, since we define our
  # own "order", this would be included if we did not define our own schema.
  _message_fields_schema = ('attr1', 'attr2', 'owner', 'created')

  # The properties attr1 and attr2 are required here so that all entities will
  # have values for performing queries.
  attr1 = ndb.StringProperty(required=True)
  attr2 = ndb.StringProperty(required=True)
  created = ndb.DateTimeProperty(auto_now_add=True)
  # As in basic_with_auth/main.py, an owner property is used and each entity
  # created will have the current user saved as the owner. As with attr1 and
  # attr2 above, we are also requiring the owner field so we can use it for
  # queries too.
  owner = ndb.UserProperty(required=True)

  # This is a setter which will be used by the helper property "order", which we
  # are overriding here. The setter used for that helper property is also named
  # OrderSet. This method will be called when order is set from a ProtoRPC
  # query request.
  def OrderSet(self, value):
    # Since we wish to control which queries are made, we only accept values
    # from our custom Enum type Order.
    if not isinstance(value, Order):
      raise TypeError('Expected an enum, received: %s.' % (value,))

    # For MYFIRST, we order by attr1.
    if value == Order.MYFIRST:
      # Use the method OrderSet from the parent class to set the string value
      # based on the enum.
      super(MyModel, self).OrderSet('attr1')
    # For MYSECOND, we order by attr2, but in descending order.
    elif value == Order.MYSECOND:
      # Use the method OrderSet from the parent class to set the string value
      # based on the enum.
      super(MyModel, self).OrderSet('-attr2')
    # For either case, the order used here will be combined with an equality
    # filter based on the current user, and we have the corresponding indexes
    # specified in index.yaml so no index errors are experienced by our users.

    # If the value is not a valid Enum value, raise a TypeError. This should
    # never occur since value is known to be an instance of Order.
    else:
      raise TypeError('Unexpected value of Order: %s.' % (value,))

  # This EndpointsAliasProperty is our own helper property and overrides the
  # original "order". We specify the setter as the function OrderSet which we
  # just defined. The property_type is the class Order and the default value of
  # the alias property is MYFIRST.

  # Endpoints alias properties must have a corresponding property type, which
  # can be either a ProtoRPC field or a ProtoRPC message class or enum class.
  # Here, by providing a property type of Order, we aid in the creation of a
  # field corresponding to this property in a ProtoRPC message schema.

  # The EndpointsAliasProperty can be used as a decorator as is done here, or
  # can be used in the same way NDB properties are, e.g.
  #   attr1 = ndb.StringProperty()
  # and the similar
  #   order = EndpointsAliasProperty(OrderGet, setter=OrderSet, ...)
  # where OrderGet would be the function defined here.
  @EndpointsAliasProperty(setter=OrderSet, property_type=Order,
                          default=Order.MYFIRST)
  def order(self):
    # We only need to limit the values to Order enums, so we can use the getter
    # from the helper property with no changes.
    return super(MyModel, self).order



# Since we are using auth, we want to test with the Google APIs Explorer:
# https://developers.google.com/apis-explorer/
# By default, if allowed_client_ids is not specified, this is enabled by
# default. If you specify allowed_client_ids, you'll need to include
# endpoints.API_EXPLORER_CLIENT_ID in this list. This is necessary for auth
# tokens obtained by the API Explorer (on behalf of users) to be considered
# valid by our API.
@endpoints.api(name='myapi', version='v1', description='My Little API')
class MyApi(remote.Service):

  # We use specify that request_fields is ('attr1', 'attr2') because the
  # created value is set when the entity is put to the datastore and the owner
  # is set from the current user. As in basic_with_auth, since user_required is
  # set to True, the current user will always be valid.

  # Since no response_fields are set, the four fields from
  # _message_fields_schema will be sent in the response.
  @MyModel.method(request_fields=('attr1', 'attr2'),
                  user_required=True,
                  path='mymodel', http_method='POST', name='mymodel.insert')
  def MyModelInsert(self, my_model):
    my_model.owner = endpoints.get_current_user()
    my_model.put()
    return my_model

  # As in paging/main.py, we use the fields limit, order and pageToken for
  # paging, but here "order" is the Enum-based property we defined above. As
  # mentioned in the definition of OrderSet, these order values are coupled with
  # the filter for current user.

  # Since no collection_fields are set, each value in "items" in the response
  # will use the four fields from _message_fields_schema.
  @MyModel.query_method(query_fields=('limit', 'order', 'pageToken'),
                        user_required=True,
                        path='mymodels', name='mymodel.list')
  def MyModelList(self, query):
    # Current user is valid since user_required is set to True.
    return query.filter(MyModel.owner == endpoints.get_current_user())


application = endpoints.api_server([MyApi], restricted=False)

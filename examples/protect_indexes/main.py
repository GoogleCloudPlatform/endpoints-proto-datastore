from google.appengine.ext import ndb
from protorpc import messages
from protorpc import remote

import endpoints

from endpoints_proto_datastore.ndb import EndpointsAliasProperty
from endpoints_proto_datastore.ndb import EndpointsModel


class Order(messages.Enum):
  MYFIRST = 1
  MYSECOND = 2


class MyModel(EndpointsModel):
  attr1 = ndb.StringProperty(required=True)
  attr2 = ndb.StringProperty(required=True)
  owner = ndb.UserProperty(required=True)
  created = ndb.DateTimeProperty(auto_now_add=True)

  def OrderSet(self, value):
    if not isinstance(value, Order):
      raise TypeError('Expected an enum, received: %s.' % (value,))

    if value == Order.MYFIRST:
      super(MyModel, self).OrderSet('attr1')
    elif value == Order.MYSECOND:
      super(MyModel, self).OrderSet('-attr2')
    else:
      raise TypeError('Unexpected value of Order: %s.' % (value,))

  @EndpointsAliasProperty(setter=OrderSet, property_type=Order,
                          default=Order.MYFIRST, exempt=True)
  def order(self):
    return super(MyModel, self).order


@endpoints.api(name='myapi', version='v1', description='My Little API',
               audiences=[endpoints.API_EXPLORER_CLIENT_ID])
class MyApi(remote.Service):

  @MyModel.method(request_ordering=('attr1', 'attr2'),
                  user_required=True,
                  path='mymodel', http_method='POST', name='mymodel.insert')
  def MyModelInsert(self, my_model):
    my_model.owner = endpoints.get_current_user()
    my_model.put()
    return my_model

  @MyModel.query_method(query_ordering=('limit', 'order', 'pageToken'),
                        user_required=True,
                        path='mymodels', name='mymodel.list')
  def MyModelList(self, query):
    return query.filter(MyModel.owner == endpoints.get_current_user())


application = endpoints.api_server([MyApi], restricted=False)

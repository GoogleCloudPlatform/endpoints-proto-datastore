from google.appengine.ext import ndb
from protorpc import messages
from protorpc import remote

import endpoints

from endpoints_proto_datastore.ndb import EndpointsAliasProperty
from endpoints_proto_datastore.ndb import EndpointsModel


DEFAULT_ORDER = 'attr1,-attr2'


class MyModel(EndpointsModel):
  _message_fields_schema = ('id', 'attr1', 'attr2', 'created')

  attr1 = ndb.StringProperty()
  attr2 = ndb.StringProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)

  def IdSet(self, value):
    if not isinstance(value, basestring):
      raise TypeError('ID must be a string.')

    self.key = ndb.Key(MyModel, value)
    self._MergeFromKey()

  @EndpointsAliasProperty(setter=IdSet, required=True,
                          property_type=messages.StringField)
  def id(self):
    if self.key is not None:
      return self.key.string_id()

  @EndpointsAliasProperty(setter=EndpointsModel.OrderSet, default=DEFAULT_ORDER)
  def order(self):
    return super(MyModel, self).order


@endpoints.api(name='myapi', version='v1', description='My Little API')
class MyApi(remote.Service):

  @MyModel.method(path='mymodel/{id}', http_method='POST',
                  name='mymodel.insert')
  def MyModelInsert(self, my_model):
    if my_model.from_datastore:
      name = my_model.key.string_id()
      raise endpoints.BadRequestException(
          'MyModel of name %s already exists.' % (name,))
    my_model.put()
    return my_model

  @MyModel.query_method(query_fields=('order',),
                        path='mymodels', name='mymodel.list')
  def MyModelList(self, query):
    return query


application = endpoints.api_server([MyApi], restricted=False)

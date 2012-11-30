import random

from google.appengine.ext import ndb
from protorpc import messages
from protorpc import remote

import endpoints

from endpoints_proto_datastore.ndb import EndpointsAliasProperty
from endpoints_proto_datastore.ndb import EndpointsModel


DEFAULT_ORDER = 'attr1,-attr2'


def RandomId():
  hex_digits = '0123456789ABCDEFG'
  return ''.join(random.choice(hex_digits) for _ in range(8))


class MyModel(EndpointsModel):
  _ordering = ('id', 'attr1', 'attr2', 'created')

  attr1 = ndb.StringProperty()
  attr2 = ndb.StringProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)

  def _IdSet(self, value):
    if not isinstance(value, basestring):
      raise TypeError('ID must be an string.')

    self._key = ndb.Key(self.__class__, value)
    entity = self._key.get()
    if entity is not None:
      self._CopyFromEntity(entity)
      self._from_datastore = True

  @EndpointsAliasProperty(property_type=messages.StringField,
                          setter=_IdSet, exempt=True)
  def id(self):
    if self._key is not None:
      return self._key.string_id()

  @EndpointsAliasProperty(setter=EndpointsModel._OrderSet,
                          default=DEFAULT_ORDER, exempt=True)
  def order(self):
    return super(MyModel, self).order


@endpoints.api(name='myapi', version='v1', description='My Little API')
class MyApi(remote.Service):

  @MyModel.method(path='mymodel', http_method='POST', name='mymodel.insert')
  def MyModelInsert(self, my_model):
    if my_model.key is None:
      my_model.key = ndb.Key(MyModel, RandomId())
    my_model.put()
    return my_model

  @MyModel.query_method(query_ordering=('order',),
                        path='mymodels', name='mymodel.list')
  def MyModelList(self, query):
    return query


application = endpoints.api_server([MyApi], restricted=False)

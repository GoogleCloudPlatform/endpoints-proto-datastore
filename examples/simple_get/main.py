from google.appengine.ext import ndb
from protorpc import remote

import endpoints

from endpoints_proto_datastore.ndb import EndpointsModel


class MyModel(EndpointsModel):
  _message_fields_schema = ('id', 'attr1', 'attr2', 'created')

  attr1 = ndb.StringProperty()
  attr2 = ndb.StringProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)


@endpoints.api(name='myapi', version='v1', description='My Little API')
class MyApi(remote.Service):

  @MyModel.method(path='mymodel', http_method='POST', name='mymodel.insert')
  def MyModelInsert(self, my_model):
    my_model.put()
    return my_model

  @MyModel.method(request_fields=('id',),
                  path='mymodel/{id}', http_method='GET', name='mymodel.get')
  def MyModelGet(self, my_model):
    if not my_model.from_datastore:
      raise endpoints.NotFoundException('MyModel not found.')

    return my_model

  @MyModel.query_method(path='mymodels', name='mymodel.list')
  def MyModelList(self, query):
    return query


application = endpoints.api_server([MyApi], restricted=False)

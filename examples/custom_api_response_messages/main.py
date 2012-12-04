import random

from google.appengine.ext import ndb
from protorpc import remote

import endpoints

from endpoints_proto_datastore.ndb import EndpointsModel


PHRASES = ['I', 'AM', 'RANDOM', 'AND', 'ARBITRARY']


class MyModel(EndpointsModel):
  attr1 = ndb.StringProperty()
  attr2 = ndb.StringProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)


@endpoints.api(name='myapi', version='v1', description='My Little API')
class MyApi(remote.Service):

  @MyModel.method(request_fields=('attr1',),
                  response_fields=('created',),
                  path='mymodel',
                  http_method='POST',
                  name='mymodel.insert')
  def MyModelInsert(self, my_model):
    my_model.attr2 = '%s-%s' % (my_model.attr1, random.choice(PHRASES))
    my_model.put()
    return my_model

  @MyModel.query_method(collection_fields=('attr2', 'created'),
                        path='mymodels', name='mymodel.list')
  def MyModelList(self, query):
    return query


application = endpoints.api_server([MyApi], restricted=False)

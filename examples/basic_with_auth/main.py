from google.appengine.ext import ndb
from protorpc import remote

import endpoints

from endpoints_proto_datastore.ndb import EndpointsModel


class MyModel(EndpointsModel):
  attr1 = ndb.StringProperty()
  attr2 = ndb.StringProperty()
  owner = ndb.UserProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)


@endpoints.api(name='myapi', version='v1', description='My Little API',
               audiences=[endpoints.API_EXPLORER_CLIENT_ID])
class MyApi(remote.Service):

  @MyModel.method(user_required=True,
                  path='mymodel', http_method='POST', name='mymodel.insert')
  def MyModelInsert(self, my_model):
    my_model.owner = endpoints.get_current_user()
    my_model.put()
    return my_model

  @MyModel.query_method(user_required=True,
                        path='mymodels', name='mymodel.list')
  def MyModelList(self, query):
    return query.filter(MyModel.owner == endpoints.get_current_user())


application = endpoints.api_server([MyApi], restricted=False)

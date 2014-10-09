import endpoints

from google.appengine.ext import ndb
from protorpc import remote

from endpoints_proto_datastore.ndb import EndpointsModel


class MyModel(EndpointsModel):
  attr1 = ndb.StringProperty()
  attr2 = ndb.StringProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)


@endpoints.api(name='myapi', version='v1', description='My Little API')
class MyApi(remote.Service):

  @MyModel.method(request_message=MyModel.ProtoCollection(),
                  response_message=MyModel.ProtoCollection(),
                  user_required=True,
                  path='mymodel_multi',
                  name='mymodel.insert_multi')
  def MyModelMultiInsert(self, items):
    entities = [MyModel.FromMessage(item_msg) for item_msg in items.items]
    ndb.put_multi(entities)
    items.items = [entity.ToMessage() for entity in entities]
    return items


application = endpoints.api_server([MyApi], restricted=False)

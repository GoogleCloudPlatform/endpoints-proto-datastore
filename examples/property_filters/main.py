# If you have not yet seen the source in paging/main.py, please take a look.

# In this sample we modify the query parameters in the MyModelList method to
# allow querying with simple equality filters.

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

  @MyModel.method(path='mymodel', http_method='POST', name='mymodel.insert')
  def MyModelInsert(self, my_model):
    my_model.put()
    return my_model

  # To add simple filters, we set the keyword argument query_fields in the
  # MyModel.query_method decorator. By specifying the fields "attr1" and "attr2"
  # as the query fields, we can filter for entities based on the values of the
  # NDB properties attr1 and/or attr2.

  # For example, a request /mymodels?attr1=cheese will return all entities with
  # attr1 equal to "cheese". The query parameters attr1 and attr2 can be used
  # individually, at the same time, or not at all.

  # An NDB property can only be used in query_fields to construct an equality
  # filter. For NDB properties which correspond to ProtoRPC message fields, such
  # as UserProperty or GeoPtProperty (see basic_with_auth/main.py), the values
  # of the property cannot be represented simply via /path?key=value. As a
  # result, such NDB properties are explicitly not allowed in query_fields and
  # if this is attempted a TypeError will be raised.
  @MyModel.query_method(query_fields=('attr1', 'attr2'),
                        path='mymodels', name='mymodel.list')
  def MyModelList(self, query):
    return query


application = endpoints.api_server([MyApi], restricted=False)

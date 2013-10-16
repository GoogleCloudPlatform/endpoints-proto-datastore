# If you have not yet seen the source in basic/main.py, please take a look.

# In this sample we override the ProtoRPC message schema of MyModel in both the
# request and response of MyModelInsert and in the response of MyModelList.

# This is used to randomly set the value of attr2 based on attr1.
import random

import endpoints

from google.appengine.ext import ndb
from protorpc import remote

from endpoints_proto_datastore.ndb import EndpointsModel


# These are used as extra phrases to randomly add to the value of attr1 when
# setting attr2.
PHRASES = ['I', 'AM', 'RANDOM', 'AND', 'ARBITRARY']


class MyModel(EndpointsModel):
  attr1 = ndb.StringProperty()
  attr2 = ndb.StringProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)


@endpoints.api(name='myapi', version='v1', description='My Little API')
class MyApi(remote.Service):

  # In addition to the arguments used in the MyModel.method decorator in
  # basic/main.py, we also use request_fields and response_fields to override
  # the schema of the ProtoRPC request message and response message,
  # respectively.

  # Since request_fields is ('attr1',), instead of the three string fields
  # attr1, attr2 and created, the request message schema will contain a single
  # string field corresponding to the NDB property attr1. Similarly, since
  # response_fields is ('created',), the response message schema will contain a
  # single string field corresponding to the NDB property created.
  @MyModel.method(request_fields=('attr1',),
                  response_fields=('created',),
                  path='mymodel',
                  http_method='POST',
                  name='mymodel.insert')
  def MyModelInsert(self, my_model):
    # We use a random value from PHRASES to set attr2 in terms of attr1. Since
    # the request message can only contain a value for attr1, we need to also
    # provide a value for attr2.
    my_model.attr2 = '%s-%s' % (my_model.attr1, random.choice(PHRASES))
    # As in basic/main.py, since created is auto_now_add, the entity gets a new
    # value for created and an ID after being persisted.
    my_model.put()
    return my_model

  # As above, in addition to the arguments used in the MyModel.query_method
  # decorator in basic/main.py, we also use collection_fields to override
  # the schema of the ProtoRPC messages that are listed in the "items" fields
  # of the query response. As in basic/main.py, there are no query arguments.
  # Since collection_fields is ('attr2', 'created'), each value in the "items"
  # list will contain the two string fields corresponding to the NDB properties
  # attr2 and created.
  @MyModel.query_method(collection_fields=('attr2', 'created'),
                        path='mymodels', name='mymodel.list')
  def MyModelList(self, query):
    # As in basic/main.py, no filters are applied.
    return query


application = endpoints.api_server([MyApi], restricted=False)

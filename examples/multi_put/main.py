# If you have not yet seen the source in basic_with_auth/main.py,
# please take a look.

# In this sample we expand on authenticated insertion of a single entity
# by showing how to insert a collection of entities at once while
# requiring that the user is authenticated.

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

  # In standard usage, there is no default way to use request_fields
  # to turn a method that accepts an EndpointsModel subtype into one
  # that accepts a collection of items of the same subtype.

  # However, EndpointsModel.method accepts an alternate keyword argument
  # which allows this: request_message.

  # By specifying request_message (and/or response_message), the protorpc
  # definition of the request can be directly provided to the method.

  # In order to get the protorpc definition for a collection, we use the
  # EndpointsModel.ProtoCollection utility which is used to form the
  # responses in EndpointsModel.query_method.
  @MyModel.method(request_message=MyModel.ProtoCollection(),
                  response_message=MyModel.ProtoCollection(),
                  user_required=True,
                  path='mymodel_multi',
                  name='mymodel.insert_multi')
  def MyModelMultiInsert(self, my_model_collection):
    # Convert the RPC messages into the corresponding ndb entities.
    # This is necessary because using request_fields makes the request
    # object a raw ProtoRPC message of the given type.
    entities = [MyModel.FromMessage(item_msg)
                for item_msg in my_model_collection.items]
    # Efficiently write the entities to datastore.
    ndb.put_multi(entities)
    # Since the response type is hardcoded as a ProtoRPC message type, the
    # ProtoRPC message must be directly returned. This is different than
    # the typical flow using response_fields since the current method
    # doesn't know how to convert the response from a native ndb.Model
    # into a protorpc message.
    response_items = [entity.ToMessage() for entity in entities]
    response_collection = MyModel.ProtoCollection()(items=response_items)
    return response_collection


application = endpoints.api_server([MyApi], restricted=False)

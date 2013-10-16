# If you have not yet seen the source in basic/main.py, please take a look.

# In this sample we add an additional method MyModelGet which allows a specific
# entity to be retrieved.

import endpoints

from google.appengine.ext import ndb
from protorpc import remote

from endpoints_proto_datastore.ndb import EndpointsModel


# In this model definition, we have included _message_fields_schema to define
# a custom ProtoRPC message schema for this model. To see a similar but
# different way to use custom fields, check out the samples in
# custom_api_response_messages/main.py and paging/main.py.
class MyModel(EndpointsModel):
  # This results in a ProtoRPC message definition with four fields, in the exact
  # order specified here: id, attr1, attr2, and created.
  # The fields corresponding to properties (attr1, attr2 and created) are string
  # fields as in basic/main.py. The field "id" will be an integer field
  # representing the ID of the entity in the datastore. For example if
  # my_entity.key is equal to ndb.Key(MyModel, 1), the id is the integer 1.

  # The property "id" is one of five helper properties provided by default to
  # help you perform common operations like this (retrieving by ID). In addition
  # there is an "entityKey" property which provides a base64 encoded version of
  # a datastore key and can be used in a similar fashion as "id", and three
  # properties used for queries -- limit, order, pageToken -- which are
  # described in more detail in paging/main.py.
  _message_fields_schema = ('id', 'attr1', 'attr2', 'created')

  attr1 = ndb.StringProperty()
  attr2 = ndb.StringProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)


@endpoints.api(name='myapi', version='v1', description='My Little API')
class MyApi(remote.Service):

  @MyModel.method(path='mymodel', http_method='POST', name='mymodel.insert')
  def MyModelInsert(self, my_model):
    # Here, since the schema includes an ID, it is possible that the entity
    # my_model has an ID, hence we could be specifying a new ID in the datastore
    # or overwriting an existing entity. If no ID is included in the ProtoRPC
    # request, then no key will be set in the model and the ID will be set after
    # the put completes, as in basic/main.py.

    # In either case, the datastore ID from the entity will be returned in the
    # ProtoRPC response message.
    my_model.put()
    return my_model

  # This method is not defined in any of the previous examples: it allows an
  # entity to be retrieved from it's ID. As in
  # custom_api_response_messages/main.py, we override the schema of the ProtoRPC
  # request message to limit to a single field: "id". Since "id" is one of
  # the helper methods provided by EndpointsModel, we may use it as one of our
  # request_fields. In general, other than these five, only properties you
  # define are allowed.
  @MyModel.method(request_fields=('id',),
                  path='mymodel/{id}', http_method='GET', name='mymodel.get')
  def MyModelGet(self, my_model):
    # Since the field "id" is included, when it is set from the ProtoRPC
    # message, the decorator attempts to retrieve the entity by its ID. If the
    # entity was retrieved, the boolean from_datastore on the entity will be
    # True, otherwise it will be False. In this case, if the entity we attempted
    # to retrieve was not found, we return an HTTP 404 Not Found.

    # For more details on the behavior of setting "id", see the sample
    # custom_alias_properties/main.py.
    if not my_model.from_datastore:
      raise endpoints.NotFoundException('MyModel not found.')
    return my_model

  # This is identical to the example in basic/main.py, however since the
  # ProtoRPC schema for the model now includes "id", all the values in "items"
  # will also contain an "id".
  @MyModel.query_method(path='mymodels', name='mymodel.list')
  def MyModelList(self, query):
    return query


application = endpoints.api_server([MyApi], restricted=False)

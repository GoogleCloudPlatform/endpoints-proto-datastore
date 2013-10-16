# If you have not yet seen the source in basic/main.py, please take a look.

import endpoints

from google.appengine.ext import ndb
from protorpc import remote

from endpoints_proto_datastore.ndb import EndpointsModel


# In this model definition, we have added an extra field "owner" to the model
# defined in basic/main.py. Since using auth, we will save the current user and
# query by the current user, so saving a user property on each entity will allow
# us to do this.
class MyModel(EndpointsModel):
  # By default, the ProtoRPC message schema corresponding to this model will
  # have four fields: attr1, attr2, created and owner
  # in an arbitrary order (the ordering of properties in a dictionary is not
  # guaranteed).
  attr1 = ndb.StringProperty()
  attr2 = ndb.StringProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)
  # The three properties above are represented by string fields, but the
  # UserProperty below is represented in the ProtoRPC message schema as a
  # message field -- a field whose value is itself a message. To hold a user
  # property, a custom ProtoRPC message class is defined in
  # endpoints_proto_datastore.utils and is used to convert to and from the NDB
  # property and the corresponding ProtoRPC field.
  owner = ndb.UserProperty()


# Since we are using auth, we want to test with the Google APIs Explorer:
# https://developers.google.com/apis-explorer/
# By default, if allowed_client_ids is not specified, this is enabled by
# default. If you specify allowed_client_ids, you'll need to include
# endpoints.API_EXPLORER_CLIENT_ID in this list. This is necessary for auth
# tokens obtained by the API Explorer (on behalf of users) to be considered
# valid by our API.
@endpoints.api(name='myapi', version='v1', description='My Little API')
class MyApi(remote.Service):

  # To specify that this method requires authentication, we can simply set the
  # keyword argument user_required to True in the MyModel.method decorator. The
  # remaining arguments to the decorator are the same as in basic/main.py. Once
  # user_required is set, the method will first determine if a user has been
  # detected from the token sent with the request (if any was sent it all) and
  # will return an HTTP 401 Unauthorized if no valid user is detected. In the
  # case of a 401, the method will not be executed. Conversely, if method
  # execution occurs, user_required=True will guarantee that the current user is
  # valid.
  @MyModel.method(user_required=True,
                  path='mymodel', http_method='POST', name='mymodel.insert')
  def MyModelInsert(self, my_model):
    # Since user_required is True, we know endpoints.get_current_user will
    # return a valid user.
    my_model.owner = endpoints.get_current_user()
    # Also note, since we don't override the default ProtoRPC message schema,
    # API users can send an owner object in the request, but we overwrite the
    # model property with the current user before the entity is inserted into
    # the datastore and this put operation will only occur if a valid token
    # identifying the user was sent in the Authorization header.
    my_model.put()
    return my_model

  # As above with MyModelInsert, we add user_required=True to the arguments
  # passed to the MyModel.query_method decorator in basic/main.py. Therefore,
  # only queries can be made by a valid user.
  @MyModel.query_method(user_required=True,
                        path='mymodels', name='mymodel.list')
  def MyModelList(self, query):
    # We only allow users to query the MyModel entities that they have created,
    # so query using owner equal to the current user. Since user_required is
    # set, we know get_current_user will return a valid user.
    return query.filter(MyModel.owner == endpoints.get_current_user())


application = endpoints.api_server([MyApi], restricted=False)

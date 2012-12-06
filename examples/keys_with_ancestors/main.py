from google.appengine.ext import ndb
from protorpc import messages
from protorpc import remote

import endpoints

from endpoints_proto_datastore.ndb import EndpointsAliasProperty
from endpoints_proto_datastore.ndb import EndpointsModel


class MyParent(EndpointsModel):
  _message_fields_schema = ('name',)

  updated = ndb.DateTimeProperty(auto_now=True)

  def NameSet(self, value):
    if not isinstance(value, basestring):
      raise TypeError('Name must be a string.')
    self.UpdateFromKey(ndb.Key(MyParent, value))

  @EndpointsAliasProperty(setter=NameSet, required=True,
                          property_type=messages.StringField)
  def name(self):
    if self.key is not None:
      return self.key.string_id()


class MyModel(EndpointsModel):
  _parent = None
  _id = None

  attr1 = ndb.StringProperty()
  attr2 = ndb.StringProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)

  def SetKey(self):
    # Can only set the key if both the parent and the child id are set
    if self._parent is not None and self._id is not None:
      key = ndb.Key(MyParent, self._parent, MyModel, self._id)
      self.UpdateFromKey(key)

  def SetParts(self):
    if self.key is not None:
      parent_pair, id_pair = self.key.pairs()
      self._parent = parent_pair[1]
      self._id = id_pair[1]

  def ParentSet(self, value):
    if not isinstance(value, basestring):
      raise TypeError('Parent name must be a string.')

    # Validate parent
    self._parent = value
    if ndb.Key(MyParent, value).get() is None:
      raise endpoints.NotFoundException('Parent %s does not exist.' % value)
    self.SetKey()

    # For query
    self._endpoints_query_info.ancestor = ndb.Key(MyParent, value)

  @EndpointsAliasProperty(setter=ParentSet, required=True,
                          property_type=messages.StringField)
  def parent(self):
    if self._parent is None:
      self.SetParts()
    return self._parent

  def IdSet(self, value):
    if not isinstance(value, basestring):
      raise TypeError('ID must be a string.')

    self._id = value
    self.SetKey()

  @EndpointsAliasProperty(setter=IdSet, required=True,
                          property_type=messages.StringField)
  def id(self):
    if self._id is None:
      self.SetParts()
    return self._id


@endpoints.api(name='myapi', version='v1', description='My Little API')
class MyApi(remote.Service):

  @MyParent.method(path='myparent', http_method='POST',
                   name='myparent.insert')
  def MyParentInsert(self, my_parent):
    my_parent.put()
    return my_parent

  @MyModel.method(path='mymodel/{parent}', http_method='POST',
                  name='mymodel.insert')
  def MyModelInsert(self, my_model):
    # This is not truly safe against duplicates. To do this, a datastore
    # transaction would be necessary
    if my_model.from_datastore:
      raise endpoints.BadRequestException(
          'MyModel %s with parent %s already exists.' %
          (my_model.id, my_model.parent))
    my_model.put()
    return my_model

  @MyModel.query_method(query_fields=('parent',),
                        path='mymodels/{parent}', name='mymodel.list')
  def MyModelList(self, query):
    return query


application = endpoints.api_server([MyApi], restricted=False)

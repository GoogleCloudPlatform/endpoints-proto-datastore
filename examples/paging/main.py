# If you have not yet seen the source in basic/main.py, please take a look.

# In this sample we modify the query parameters in the MyModelList method to
# allow paging through results.

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

  # To add paging functionality, we set the keyword argument query_fields in the
  # MyModel.query_method decorator. By specifying the fields "limit", "order"
  # and "pageToken" as the query fields, we can accept values specializing the
  # query before retrieving results from the datastore. Though "limit", "order"
  # and "pageToken" are not defined as properties on MyModel, they are included
  # as helper properties by the base class EndpointsModel.

  # The three helper properties we use here perform the following

  # - limit: Allows a limit to be set for the number of results retrieved by a
  #          query.

  # - order: This allows the result set to be ordered by properties. For
  #          example, if the value of order is "attr1", results of the query
  #          will be in ascending order, ordered by "attr1". Similarly, if the
  #          value of order is "-attr2", the results of the query will be in
  #          descending order, ordered by "attr2".

  #          Even more complex orders can be created, such as "attr1,-attr2",
  #          which will first order by attr1 and then within each value order by
  #          attr2. However, such queries are not possible in the datastore if
  #          no index has been built. See custom_alias_properties/main.py and
  #          matching_queries_to_indexes/main.py for examples of how to deal
  #          with complex queries.

  # - pageToken: This is used for paging within a result set. For example, if a
  #              limit of 10 is set, but there are 12 results, then the ProtoRPC
  #              response will have "items" with 10 values and a nextPageToken
  #              which contains a string cursor for the query. By using this
  #              value as pageToken in a subsequent query, the remaining 2
  #              results can be retrieved and the ProtoRPC response will not
  #              contain a nextPageToken since there are no more results.

  # For a bit more on the other helper properties provided by EndpointsModel,
  # see simple_get/main.py. To see how to define your own helper properties, see
  # custom_alias_properties/main.py, matching_queries_to_indexes/main.py and
  # keys_with_ancestors/main.py.

  # To see how query fields can be used to perform simple equality filters, see
  # property_filters/main.py.
  @MyModel.query_method(query_fields=('limit', 'order', 'pageToken'),
                        path='mymodels', name='mymodel.list')
  def MyModelList(self, query):
    return query


application = endpoints.api_server([MyApi], restricted=False)

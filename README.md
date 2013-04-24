# endpoints-proto-datastore

This library is intended to be used with the Python version of Google Cloud Endpoints.
If you'd like to learn more about Google Cloud Endpoints, please visit our
[documentation](https://developers.google.com/appengine/docs/python/endpoints/).
To run each of these samples, you should include the `endpoints_proto_datastore`
[folder](https://github.com/GoogleCloudPlatform/endpoints-proto-datastore/tree/master/endpoints_proto_datastore)
included with this project.

By extending the functionality provided by `ndb.Model` class and the `endpoints` library,
this library allows you to directly interact with model entities in your API methods
rather than ProtoRPC requests. For example, instead of:
```python
  @endpoints.method(MyModelMessage, MyModelMessage,
                    path='mymodel', http_method='POST',
                    name='mymodel.insert')
  def InsertModel(self, request):
    my_model = MyModel(attr1=request.attr1, attr2=request.attr2, ...)
    transformed_model = DoSomething(my_model)
    return MyModelMessage(attr1=transformed_model.attr1, 
                          attr2=transformed_model.attr2, ...)
```
we can directly use the entity in the request:
```python
  @MyModel.method(path='mymodel', http_method='POST',
                  name='mymodel.insert')
  def InsertModel(self, my_model):
    return TransformModel(my_model)
```
without ever even having to define a ProtoRPC message class!

Get started with the examples at:
http://endpoints-proto-datastore.appspot.com/

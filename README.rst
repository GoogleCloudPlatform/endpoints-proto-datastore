endpoints-proto-datastore
-------------------------

|pypi|

This library is intended to be used with the Python version of Google
Cloud Endpoints. If you'd like to learn more about Google Cloud
Endpoints, please visit our `documentation`_. To run each of these samples,
you should include the ``endpoints_proto_datastore`` `folder`_ included with
this project.

By extending the functionality provided by ``ndb.Model`` class and the
``endpoints`` library, this library allows you to directly interact with
model entities in your API methods rather than ProtoRPC requests. For
example, instead of:

.. code:: python

      @endpoints.method(MyModelMessage, MyModelMessage,
                        path='mymodel', http_method='POST',
                        name='mymodel.insert')
      def InsertModel(self, request):
        my_model = MyModel(attr1=request.attr1, attr2=request.attr2, ...)
        transformed_model = DoSomething(my_model)
        return MyModelMessage(attr1=transformed_model.attr1,
                              attr2=transformed_model.attr2, ...)

we can directly use the entity in the request:

.. code:: python

      @MyModel.method(path='mymodel', http_method='POST',
                      name='mymodel.insert')
      def InsertModel(self, my_model):
        return DoSomething(my_model)

without ever even having to define a ProtoRPC message class!

Get started with the `examples`_.

Project Setup, Installation, and Configuration
----------------------------------------------

To use this library in your App Engine application you can

-  Download the `endpoints_proto_datastore`_ library and unzip it in the root
   of your App Engine application. For example, on a Unix based machine:

   .. code:: bash

       (${GAE_PROJECT_ROOT})$ wget "https://github.com/GoogleCloudPlatform/"`
                                   `"endpoints-proto-datastore/blob/"`
                                   `"zipfile-branch/"`
                                   `"endpoints_proto_datastore.zip?raw=true" \
                              -O endpoints_proto_datastore.zip
       (${GAE_PROJECT_ROOT})$ unzip endpoints_proto_datastore.zip
       (${GAE_PROJECT_ROOT})$ rm endpoints_proto_datastore.zip

-  Alternatively you can stay up to date by adding this repository to
   your project as a ``git`` `submodule`_:

   .. code:: bash

       (${YOUR_GIT_ROOT})$ git submodule add https://github.com/GoogleCloudPlatform/endpoints-proto-datastore

   This will create the entire project in the ``endpoints-proto-datastore``
   folder in your project. Since `Python packages`_ require ``__init__.py``
   files for imports to work and the root of this project is not meant to be a
   Python package, you'll need to add ``endpoints-proto-datastore`` to your
   Python import path.

   The simplest way to do this is to add the following lines to your
   `appengine_config.py`_ file (or create the file if it doesn't yet exist):

   .. code:: python

       import os
       import sys

       ENDPOINTS_PROJECT_DIR = os.path.join(os.path.dirname(__file__),
                                            'endpoints-proto-datastore')
       sys.path.append(ENDPOINTS_PROJECT_DIR)

   **Note**: If the App Engine project stored in your ``git`` repository
   is not at the root, you may need to add a symlink to the
   ``endpoints-proto-datastore/endpoints_proto_datastore`` directory and
   put it at the root of your App Engine project.

To install App Engine visit the `Development Environment`_ page.

Features, Questions and Support
-------------------------------

-  To request a feature, report a bug, or request a new sample or piece
   of documentation; please `file an issue`_.
-  For troubleshooting issues or asking general questions, please
   `ask a question`_ on StackOverflow using the ``endpoints-proto-datastore``
   tag.

Testing
-------

All tests are wrapped into the `endpoints_proto_datastore_test_runner.py`_
module. To run the tests, simply execute

.. code:: bash

    $ python ${PATH_TO_TEST_RUNNER}/endpoints_proto_datastore_test_runner.py

This test runner assumes that you have App Engine SDK tools on your path
and will use the location of the ``dev_appserver.py`` script to
determine the location of the SDK. For example, on a Unix based system
it would be equivalent to:

.. code:: bash

    $ dirname `readlink \`which dev_appserver.py\``

Contributing changes
--------------------

-  See `CONTRIB.md`_
-  To create docs for a contributed example, use `pycco`_. For example:

   .. code:: bash

       $ pycco example_name/main.py

Licensing
---------

-  See `LICENSE`_
-  **Note**: The test runner includes some code from the Twisted
   project, which is `listed under terms other than Apache 2.0`_.

.. _documentation: https://developers.google.com/appengine/docs/python/endpoints/
.. _folder: https://github.com/GoogleCloudPlatform/endpoints-proto-datastore/tree/master/endpoints_proto_datastore
.. _examples: http://endpoints-proto-datastore.appspot.com/
.. _endpoints_proto_datastore: https://github.com/GoogleCloudPlatform/endpoints-proto-datastore/blob/zipfile-branch/endpoints_proto_datastore.zip?raw=true
.. _submodule: http://git-scm.com/book/en/Git-Tools-Submodules
.. _Python packages: http://docs.python.org/2/tutorial/modules.html#importing-from-a-package
.. _appengine_config.py: https://developers.google.com/appengine/docs/python/tools/appengineconfig
.. _Development Environment: https://developers.google.com/appengine/docs/python/gettingstartedpython27/devenvironment
.. _file an issue: https://github.com/GoogleCloudPlatform/endpoints-proto-datastore/issues/new
.. _ask a question: http://stackoverflow.com/questions/ask?tags=endpoints-proto-datastore
.. _endpoints_proto_datastore_test_runner.py: https://github.com/GoogleCloudPlatform/endpoints-proto-datastore/blob/master/endpoints_proto_datastore/endpoints_proto_datastore_test_runner.py
.. _CONTRIB.md: https://github.com/GoogleCloudPlatform/endpoints-proto-datastore/blob/master/CONTRIB.md
.. _pycco: http://fitzgen.github.io/pycco/
.. _LICENSE: https://github.com/GoogleCloudPlatform/endpoints-proto-datastore/blob/master/LICENSE
.. _listed under terms other than Apache 2.0: http://twistedmatrix.com/trac/browser/trunk/LICENSE

.. |pypi| image:: https://img.shields.io/pypi/v/endpoints-proto-datastore.svg
   :target: https://pypi.python.org/pypi/endpoints-proto-datastore

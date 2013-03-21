# Copyright 2013 Google Inc. All Rights Reserved.

"""Tests for utils.py."""


import os
import subprocess
import sys
import unittest

sys.modules.pop('google', None)
dev_appserver_on_path = subprocess.check_output(
    ['which', 'dev_appserver.py']).strip()
if not os.path.exists(dev_appserver_on_path):
  print >>sys.stderr, ('Dev Appserver path %r does not exist' %
                       (dev_appserver_on_path,))
  raise SystemExit(1)

real_path = os.path.realpath(dev_appserver_on_path)
sys.path.insert(0, os.path.dirname(real_path))
import dev_appserver
dev_appserver.fix_sys_path()

project_root = subprocess.check_output(
    ['git', 'rev-parse', '--show-toplevel']).strip()
sys.path.insert(0, project_root)

from protorpc import messages

from endpoints_proto_datastore import utils


class UtilsTests(unittest.TestCase):

  def testIsSubclass(self):
    self.assertTrue(utils.IsSubclass(int, int))

    self.assertTrue(utils.IsSubclass(bool, int))
    self.assertTrue(utils.IsSubclass(str, (str, basestring)))
    self.assertFalse(utils.IsSubclass(int, bool))

    # Make sure this does not fail
    self.assertFalse(utils.IsSubclass(int, None))

  def testDictToTuple(self):
    # pylint:disable-msg=W0212
    self.assertRaises(AttributeError, utils._DictToTuple, None)

    class Simple(object):
      items = None  # Not callable
    self.assertRaises(TypeError, utils._DictToTuple, Simple)

    single_value_dictionary = {1: 2}
    self.assertEqual((1,), utils._DictToTuple(single_value_dictionary))

    multiple_value_dictionary = {-5: 3, 1: 1, 3: 2}
    self.assertEqual((1, 3, -5), utils._DictToTuple(multiple_value_dictionary))
    # pylint:enable-msg=W0212

  def testGeoPtMessage(self):
    geo_pt_message = utils.GeoPtMessage(lat=1.0)
    self.assertEqual(geo_pt_message.lat, 1.0)
    self.assertEqual(geo_pt_message.lon, None)
    self.assertFalse(geo_pt_message.is_initialized())

    geo_pt_message.lon = 2.0
    self.assertEqual(geo_pt_message.lon, 2.0)
    self.assertTrue(geo_pt_message.is_initialized())

    self.assertRaises(messages.ValidationError,
                      utils.GeoPtMessage, lat='1', lon=2)

    self.assertRaises(TypeError, utils.GeoPtMessage, 1.0, 2.0)

    self.assertRaises(AttributeError, utils.GeoPtMessage,
                      lat=1.0, lon=2.0, other=3.0)

    geo_pt_message = utils.GeoPtMessage(lat=1.0, lon=2.0)
    self.assertTrue(geo_pt_message.is_initialized())


def main():
  unittest.main()


if __name__ == '__main__':
  main()

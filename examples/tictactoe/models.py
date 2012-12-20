# Copyright 2012 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import random
import re

from google.appengine.ext import ndb
from protorpc import messages

from endpoints_proto_datastore.ndb import EndpointsAliasProperty
from endpoints_proto_datastore.ndb import EndpointsModel
from endpoints_proto_datastore.ndb import EndpointsUserProperty


class Board(EndpointsModel):
  state = ndb.StringProperty(required=True)

  def MoveOpponent(self):
    free_indices = [match.start() for match in re.finditer('-', self.state)]
    random_index = random.choice(free_indices)
    result = list(self.state)  # Need a mutable object
    result[random_index] = 'O'
    self.state = ''.join(result)


class Order(messages.Enum):
  WHEN = 1
  TEXT = 2


class Score(EndpointsModel):
  _message_fields_schema = ('id', 'outcome', 'played', 'player')

  outcome = ndb.StringProperty(required=True)
  played = ndb.DateTimeProperty(auto_now_add=True)
  player = EndpointsUserProperty(required=True, raise_unauthorized=True)

  def OrderSet(self, value):
    if not isinstance(value, Order):
      raise TypeError('Expected an enum, received: %s.' % (value,))

    if value == Order.WHEN:
      super(Score, self).OrderSet('-played')
    elif value == Order.TEXT:
      super(Score, self).OrderSet('outcome')
    else:
      raise TypeError('Unexpected value of Order: %s.' % (value,))

  @EndpointsAliasProperty(setter=OrderSet, property_type=Order,
                          default=Order.WHEN)
  def order(self):
    return super(Score, self).order

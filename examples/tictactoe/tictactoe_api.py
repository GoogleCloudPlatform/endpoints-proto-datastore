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

from protorpc import remote

import endpoints

from models import Board
from models import Score


@endpoints.api(name='tictactoe', version='v1',
               description='Tic Tac Toe API',
               allowed_client_ids=['YOUR-CLIENT-ID',
                                   endpoints.API_EXPLORER_CLIENT_ID])
class TicTacToeApi(remote.Service):

  @Board.method(path='board', http_method='POST',
                name='board.getmove')
  def BoardGetMove(self, board):
    if not (len(board.state) == 9 and set(board.state) <= set('OX-')):
      raise endpoints.BadRequestException('Invalid board.')
    board.MoveOpponent()
    return board

  @Score.method(request_fields=('id',),
                path='scores/{id}', http_method='GET',
                name='scores.get')
  def ScoresGet(self, score):
    if not score.from_datastore:
      raise endpoints.NotFoundException('Score not found.')

    if score.player != endpoints.get_current_user():
      raise endpoints.ForbiddenException(
          'You do not have access to this score.')

    return score

  @Score.method(request_fields=('outcome',),
                path='scores', http_method='POST',
                name='scores.insert')
  def ScoresInsert(self, score):
    score.put()  # score.player already set since EndpointsUserProperty
    return score

  @Score.query_method(query_fields=('limit', 'order', 'pageToken'),
                      user_required=True,
                      path='scores', name='scores.list')
  def ScoresList(self, query):
    return query.filter(Score.player == endpoints.get_current_user())

import logging
import endpoints
import random
import gameutils
from models import Player, Game
from models import GameForm, StringMessage
from protorpc import remote, messages
from google.appengine.ext import ndb
import re


PLAYER_REQUEST = endpoints.ResourceContainer(player_name=messages.StringField(1),
                                           email=messages.StringField(2))

GAME_REQUESTS = endpoints.ResourceContainer(player_name=messages.StringField(1))



@endpoints.api(name='battleships', version='v1')
class BattleshipApi(remote.Service):
    @endpoints.method(request_message=PLAYER_REQUEST,
                      response_message=StringMessage,
                      path='player',
                      name='create_player',
                      http_method='POST')
    def create_player(self, request):
        """Create a User. Requires a unique playername"""
        if Player.query(Player.name == request.player_name).get():
            raise endpoints.ConflictException(
                'A User with that name already exists!')

        if gameutils.getRegex(request.email) == None:
            print(' ERROR - invalid email, please try again')
            raise endpoints.ConflictException(
                'invalid email, please try again!')

        player = Player(name=request.player_name, email=request.email, board=Player.create_empty_board())
        player.put()

        return StringMessage(message='Player created!'.format(request.player_name))

    @endpoints.method(request_message=GAME_REQUESTS,
                    response_message=GameForm,
                    path='game',
                    name='create_game',
                    http_method='POST')
    def create_game(self, request):
        """One of the players, creates the game and gets the game-id and gives that ID
        to the other player in order to play between each other"""
        player = Player.query(Player.name == request.player_name).get()
        if not player:
            raise endpoints.NotFoundException(
                'A Player with that name does not exist!, '
                'we need one player in order to create the game')
        try:
            game = Game.new_game(player)
        except ValueError:
            raise endpoints.BadRequestException('sarasa')

        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.

        return game.to_form('Game created!, we only need one player '
                            'to join in order to start the game')



api = endpoints.api_server([BattleshipApi])
import logging
import endpoints
import random
import gameutils
from models import Player, Game, Board
from models import GameForm, BoardForm, StringMessage
from protorpc import remote, messages
from google.appengine.ext import ndb
import re


PLAYER_REQUEST = endpoints.ResourceContainer(player_name=messages.StringField(1),
                                           email=messages.StringField(2))

GAME_REQUESTS = endpoints.ResourceContainer(player_name=messages.StringField(1))

JOIN_GAME_REQUEST = endpoints.ResourceContainer(player_name=messages.StringField(1),
                                                urlsafe_key=messages.StringField(2))

CREATE_EMPTY_BOARD_REQUEST = endpoints.ResourceContainer(player_name=messages.StringField(1),
                                                urlsafe_key=messages.StringField(2))


@endpoints.api(name='battleships', version='v1')
class BattleshipApi(remote.Service):
    @endpoints.method(request_message=PLAYER_REQUEST,
                      response_message=StringMessage,
                      path='player',
                      name='create_player',
                      http_method='POST')
    def create_player(self, request):
        """Create a User. Requires a unique playername"""
        if request.player_name:
            if Player.query(Player.name == request.player_name).get():
                raise endpoints.ConflictException(
                    'A User with that name already exists!')
        else:
            raise endpoints.BadRequestException('verify the name that you are sending in the request')
        if request.email:
            if gameutils.getRegex(request.email) == None:
                print(' ERROR - invalid email, please try again')
                raise endpoints.ConflictException(
                    'invalid email, please try again!')
        else:
            raise endpoints.BadRequestException('verify the email that you are sending in the request')

        player = Player(name=request.player_name, email=request.email)
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
                            'to join in order to start the game', player.name)


    @endpoints.method(request_message=JOIN_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='join_game',
                      http_method='put')
    def join_game(self, request):
        """One of the players, creates the game and gets the game-id and gives that ID
        to the other player in order to play between each other"""
        player = Player.query(Player.name == request.player_name).get()
        print player
        if not player:
            raise endpoints.NotFoundException(
                'A Player with that name does not exist!, '
                'we need a second player in order to join the game')
        try:
            game = gameutils.get_by_urlsafe(request.urlsafe_key, Game)
            game.player2 = player.key
            game.put()
        except ValueError:
            raise endpoints.BadRequestException('please verify the information '
                                                'of the second player')

        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.

        return game.to_form('Second Player Joined the Game, we are ready to start the game!', player.name)

    @endpoints.method(request_message=CREATE_EMPTY_BOARD_REQUEST,
                      response_message=BoardForm,
                      path='board',
                      name='create_board',
                      http_method='post')
    def create_board(self, request):
        """One of the players, creates the game and gets the game-id and gives that ID
        to the other player in order to play between each other"""
        player = Player.query(Player.name == request.player_name).get()
        game = gameutils.get_by_urlsafe(request.urlsafe_key, Game)
        print player
        if not player:
            raise endpoints.NotFoundException(
                'A Player with that name does not exist!, '
                'we need a second player in order to join the game')
        if not game:
            raise endpoints.NotFoundException(
                'Game not found in the DB, please start a new game')
        if not game.game_over == False:
            raise endpoints.ConflictException(
                'Game is over')
        try:
            board = Board.new_board(player,Board.create_empty_board(),game)
            board.put()
        except ValueError:
            raise endpoints.BadRequestException('please verify the information '
                                                'of the board')

        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.

        return board.to_form(player,board)


api = endpoints.api_server([BattleshipApi])

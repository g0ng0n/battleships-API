import logging
import endpoints
import random
import gameutils
from gameutils import SHIPS_IDS
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

ASSIGN_SHIP_ON_BOARD_REQUEST = endpoints.ResourceContainer(player_name=messages.StringField(1),
                                                           urlsafe_key=messages.StringField(2),
                                                           ship_id=messages.StringField(3),
                                                           orientation=messages.StringField(4),
                                                           start_x_position=messages.IntegerField(5),
                                                           start_y_position=messages.IntegerField(6))

GET_BOARD_REQUEST = endpoints.ResourceContainer(player_name=messages.StringField(1),
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
            if gameutils.get_regex(request.email) == None:
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

    @endpoints.method(request_message=GET_BOARD_REQUEST,
                      response_message=StringMessage,
                      path='board',
                      name='get_board',
                      http_method='get')
    def get_board(self, request):
        """One of the players, creates the game and gets the game-id and gives that ID
        to the other player in order to play between each other"""
        try:
            player = Player.query(Player.name == request.player_name).get()
            game = gameutils.get_by_urlsafe(request.urlsafe_key, Game)
            board = Board.query(Board.player == player.key and Board.game == game.key).get()

            if not board:
                raise endpoints.NotFoundException(
                    'The Players Board for the selected game is not found')
            gameutils.log_board_on_console(board)
        except ValueError:
            raise endpoints.BadRequestException('please verify the information '
                                                'of the second player')

        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.

        return StringMessage(message='Board Found and printed in the console'.format(request.player_name))


    @endpoints.method(request_message=CREATE_EMPTY_BOARD_REQUEST,
                      response_message=BoardForm,
                      path='board',
                      name='create_empty_board',
                      http_method='post')
    def create_empty_board(self, request):
        """One of the players, creates the game and gets the game-id and gives that ID
        to the other player in order to play between each other"""
        player = Player.query(Player.name == request.player_name).get()
        game = gameutils.get_by_urlsafe(request.urlsafe_key, Game)

        """ HERE WE START THE PROPER VALIDATIONS FOR THIS ENDPOINT"""
        """we validate that the player is in the Data Base"""
        if not player:
            raise endpoints.NotFoundException(
                'A Player with that name does not exist!, '
                'we need a second player in order to join the game')

        """we validate that the game where we want to create the board exists"""
        if not game:
            raise endpoints.NotFoundException(
                'Game not found in the DB, please start a new game')

        """we validate that the game where we want to create the board is not Over"""
        if not game.game_over == False:
            raise endpoints.ConflictException(
                'Game is over')

        """we validate that the board of the player is active, the player can't create
                    multiple boards for the same Game"""
        if player.board and player.board_active:
            raise endpoints.ConflictException(
                'This player has already an empty board have already a board')

        try:
            board = Board.new_board(player, Board.create_empty_board(), game)
            player.board_active = True
            player.board = board.key
            player.put()
            board.put()
        except ValueError:
            raise endpoints.BadRequestException('please verify the information '
                                                'of the board')

        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.

        return board.to_form("Board created", player.name, board.aircraft_carrier,
                             board.battleship, board.submarine, board.destroyer, board.patrol_boat)

    @endpoints.method(request_message=ASSIGN_SHIP_ON_BOARD_REQUEST,
                      response_message=StringMessage,
                      path='board',
                      name='assign_ship_on_board',
                      http_method='put')
    def assign_ship_on_board(self, request):
        """One of the players, tries to assing one boat to his board game"""

        player = Player.query(Player.name == request.player_name).get()

        """we validate that the player is in the Data Base"""
        if not player:
            raise endpoints.NotFoundException('player not found')

        game = gameutils.get_by_urlsafe(request.urlsafe_key, Game)
        """we validate that the game where we want to create the board exists"""
        if not game:
            raise endpoints.NotFoundException(
                'Game not found in the DB, please start a new game')

        board = Board.query(Board.key == player.board).get()
        """we validate that the board where we want to create the board exists"""
        if not board:
            raise endpoints.NotFoundException('board not found')

        """we validate that the board of the player is active, the player can't create
            multiple boards for the same Game"""
        if not player.board and not player.board_active:
            raise endpoints.ConflictException(
                'This player has already an empty board have already a board')

        if player.board != board.key:
            raise endpoints.ConflictException('the board for this player is not the proper')

        if gameutils.valid_positions(request.start_x_position,
                                     request.start_y_position,
                                     SHIPS_IDS[request.ship_id],
                                     request.orientation):
            raise endpoints.BadRequestException(
                'Please verify the position that you choose for the boat')

        """Here we check if the boat sent
        in the request is already active in the board"""
        if gameutils.check_if_boat_is_active(request.ship_id, board):
            raise endpoints.BadRequestException(
                'Please the selected boat that you sent '
                'in the request is already active in the board')

        if gameutils.place_boat_in_board(board, request.start_x_position,
                                         request.start_y_position,
                                         request.ship_id,
                                         request.orientation):
            raise endpoints.BadRequestException(
                'The place for the boat is not available, '
                'Please verify the position that you choose for the boat')

        try:
            gameutils.log_board_on_console(board)
            board.put()
        except ValueError:
            raise endpoints.BadRequestException('please verify the information ')

        return StringMessage(message='Boat Assigned!'.format(request.player_name))


api = endpoints.api_server([BattleshipApi])

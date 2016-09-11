import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb
import random

class Board(ndb.Model):
    board = ndb.PickleProperty(required=True, default=[])
    player = ndb.KeyProperty(required=True, kind='Player')
    game = ndb.KeyProperty(required=True, kind='Game')
    """this booleans flags serves as a switch
        to see if the battleships are active on the board
        If they are active the flags will be True.
        By default they will be all False, since the player has to
        add the ship into the board.
        """
    aircraft_carrier = ndb.BooleanProperty(required=True, default=False)
    battleship = ndb.BooleanProperty(required=True, default=False)
    submarine = ndb.BooleanProperty(required=True, default=False)
    destroyer = ndb.BooleanProperty(required=True, default=False)
    patrol_boat = ndb.BooleanProperty(required=True, default=False)
    active = ndb.BooleanProperty(required=True, default=False)

    @classmethod
    def create_empty_board(cls):
        grid = []
        for row in range(10):
            # Add an empty array that will hold each cell
            # in this row
            grid.append([])
            for column in range(10):
                grid[row].append("W")  # Append a cell

        return grid

    @classmethod
    def new_board(cls, player, empty_board,game):
        """Creates and returns a new game"""

        board = Board(player=player.key,
                    board=empty_board,
                      game=game.key)
        board.put()
        return board

    def to_form(self, message, player_name, aircraft_carrier,
                battleship, submarine, destroyer, patrol_boat):
        """Returns a GameForm representation of the Game"""
        form = BoardForm()
        form.player_name = player_name
        form.aircraft_carrier = aircraft_carrier
        form.battleship = battleship
        form.submarine = submarine
        form.destroyer = destroyer
        form.patrol_boat = patrol_boat
        form.message = message
        return form

class Player(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    board = ndb.KeyProperty(required=False, kind='Board')
    board_active = ndb.BooleanProperty(required=True, default=False)
    moves = ndb.IntegerProperty()




class Game(ndb.Model):
    """Game object"""
    history = ndb.PickleProperty(required=True, default=[])
    game_over = ndb.BooleanProperty(required=True, default=False)
    player1 = ndb.KeyProperty(required=True, kind='Player')
    player2 = ndb.KeyProperty(required=False, kind='Player')


    @classmethod
    def new_game(cls, player):
        """Creates and returns a new game"""

        game = Game(player1=player.key,
                    history=[],
                    game_over=False)
        game.put()
        return game

    @classmethod
    def join_game(cls, player):

        game = Game(player2=player.key,
                    game_over=False)
        game.put()
        return game


    def to_form(self, message, player_name):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.player_name = player_name
        form.game_over = self.game_over
        form.message = message
        return form

class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    game_over = messages.BooleanField(3, required=True)
    message = messages.StringField(4, required=True)
    player_name = messages.StringField(5, required=True)

class BoardForm(messages.Message):
    """BoardForm gives the Board for a certain Player"""
    player_name = messages.StringField(1, required=True)
    aircraft_carrier = messages.BooleanField(2,required=True)
    battleship = messages.BooleanField(3,required=True)
    submarine = messages.BooleanField(4,required=True)
    destroyer = messages.BooleanField(5,required=True)
    patrol_boat = messages.BooleanField(6,required=True)
    message = messages.StringField(7, required=True)



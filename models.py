import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb
import random

class Board(ndb.Model):
    board = ndb.PickleProperty(required=True, default=[])
    player = ndb.KeyProperty(required=True, kind='Player')
    game = ndb.KeyProperty(required=True, kind='Game')

    @classmethod
    def create_empty_board(cls):
        grid = []
        for row in range(10):
            # Add an empty array that will hold each cell
            # in this row
            grid.append([])
            for column in range(4):
                grid[row].append(False)  # Append a cell

        return grid

    @classmethod
    def new_board(cls, player, empty_board,game):
        """Creates and returns a new game"""

        board = Board(player1=player.key,
                    board=empty_board,
                      game=game.key)
        board.put()
        return board

    def to_form(self, message, player_name, board):
        """Returns a GameForm representation of the Game"""
        form = BoardForm()
        form.player_name = player_name
        form.board = board;
        form.message = message
        return form

class Player(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    board = ndb.KeyProperty(required=False, kind='Board')
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
    player_name = messages.StringField(5, required=True)
    board = messages.StringField(7,required=True)
    message = messages.StringField(4, required=True)



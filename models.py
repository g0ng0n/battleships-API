import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb
import random


class Player(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    board = ndb.PickleProperty(required=True, default=[])
    moves = ndb.IntegerProperty()

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


    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.player_name = self.player1.get().name
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
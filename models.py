import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb
import random

class Board(ndb.Model):
    board = ndb.PickleProperty(required=True, default=[])
    player = ndb.KeyProperty(required=True, kind='Player')
    game = ndb.KeyProperty(required=True, kind='Game')

    active = ndb.BooleanProperty(required=True, default=False)

    @classmethod
    def create_empty_board(cls):
        grid = []
        for row in range(10):
            # Add an empty array that will hold each cell
            # in this row
            grid.append([])
            for column in range(10):
                grid[row].append(False)  # Append a cell

        return grid


    @classmethod
    def deactivate(cls):
        cls.active = False
        cls.put()


    @classmethod
    def new_board(cls, player, empty_board,game):
        """Creates and returns a new game"""

        board = Board(player=player.key,
                    board=empty_board,
                      game=game.key)
        board.put()
        return board

    @classmethod
    def add_target(cls, x,y, result):
        """Creates and returns a new game"""
        cls.board[y,x] = result
        cls.put()

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

class Score(ndb.model):
    aircraft_carrier = ndb.PickleProperty(required=True, default=[])
    battleship = ndb.PickleProperty(required=True, default=[])
    submarine = ndb.PickleProperty(required=True, default=[])
    destroyer = ndb.PickleProperty(required=True, default=[])
    patrol_boat = ndb.PickleProperty(required=True, default=[])
    board = ndb.KeyProperty(required=False, kind='Board')
    player = ndb.KeyProperty(required=True, kind='Player')
    game = ndb.KeyProperty(required=True, kind='Game')

    @classmethod
    def new_score(cls, player, game):
        """Creates and returns a new game"""

        score = Score(player=player.key,
                      board=player.board,
                      game=game.key)
        score.put()
        return score

    def target_hitted(self, player, board, game, result):
        """Score the hit"""
        self.game = game
        self.player = player
        self.board = board
        message = self.check_boat(result)
        self.put()

        return message

    def check_if_win(self):
        if self.battleship.lenght == 4 and self.aircraft_carrier ==5 and self.destroyer == 3 and self.submarine ==3 and self.patrol_boat ==2:
            return True

    def check_boat(self, result):
        if result == "AC5":
            if self.aircraft_carrier.lenght == 4:
                self.aircraft_carrier.append(result)
                return "You sunk the Aircraft carrier"
            else:
                self.aircraft_carrier.append(result)
                return "Boat Hitted"

        elif result == "BS4":
            if self.battleship.lenght == 3:
                self.battleship.append(result)
                return "You sunk the Battleship"
            else:
                self.battleship.append(result)
                return "Boat Hitted"

        elif result == "SUB3":
            if self.submarine.lenght == 2:
                self.submarine.append(result)
                return "You sunk the Submarine"
            else:
                self.submarine.append(result)
                return "Boat Hitted"
        elif result == "DES3":
            if self.battleship.lenght == 2:
                self.battleship.append(result)
                return "You sunk the Destroye"
            else:
                self.battleship.append(result)
                return "Boat Hitted"

        elif result == "PB2":
            if self.patrol_boat.lenght == 1:
                self.patrol_boat.append(result)
                return "You sunk the Destroye"
            else:
                self.patrol_boat.append(result)
                return "Boat Hitted"
        else:
            print("There is no boat with that id")

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

    def add_move_to_history(self, x, y, player):
        move = x + " " + y + " " + player
        self.history.append(move)
        self.put()

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



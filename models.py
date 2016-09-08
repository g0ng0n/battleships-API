import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb
import random


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()
    board = ndb.PickleProperty(required=True, default=[])

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

class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
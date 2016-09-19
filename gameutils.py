import logging
from google.appengine.ext import ndb
import re
import endpoints


SHIPS_IDS = {"AC5": 5,
             "BS4": 4,
             "SUB3": 3,
             "DES3": 3,
             "PB2": 2}

def get_regex(email):
    return re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',email)


def get_by_urlsafe(urlsafe, model):
    """Returns an ndb.Model entity that the urlsafe key points to. Checks
        that the type of entity returned is of the correct kind. Raises an
        error if the key String is malformed or the entity is of the incorrect
        kind
    Args:
        urlsafe: A urlsafe key string
        model: The expected entity kind
    Returns:
        The entity that the urlsafe Key string points to or None if no entity
        exists.
    Raises:
        ValueError:"""
    try:
        key = ndb.Key(urlsafe=urlsafe)
    except TypeError:
        raise endpoints.BadRequestException('Invalid Key')
    except Exception, e:
        if e.__class__.__name__ == 'ProtocolBufferDecodeError':
            raise endpoints.BadRequestException('Invalid Key')
        else:
            raise

    entity = key.get()
    if not entity:
        return None
    if not isinstance(entity, model):
        raise ValueError('Incorrect Kind')
    return entity


def valid_positions(start_x_position, start_y_position, ship,orientation):
    """We check here if the position that the user sent is valid to assign in the board Game"""
    not_valid = False

    """We check if the start_x_position of the boat is not less than 0
        and don't over pass the limits of the board (10)
        """
    if orientation == "vertical" and (start_x_position < 0 or start_x_position + ship > 10):
        return True
    elif orientation == "horizontal" and (start_y_position < 0 or start_y_position + ship > 10):
        return True

    return not_valid


def place_boat_in_board(board, start_x_position, start_y_position, ship, orientation):
    """We place the board in the game and activate the board"""
    not_valid = False

    if orientation == "horizontal":

        j = start_x_position - 1
        y = start_y_position - 1
        end_j = start_x_position + (SHIPS_IDS[ship] - 1)
        while j < end_j:
            print "position"
            print "x" + str(j) + "y" + str(y)
            if board.board[y][j] != "B":
                board.board[y][j] = "B"
                j = j + 1
            else:
                return True

    elif orientation == "vertical":
        j = start_x_position - 1
        y = start_y_position - 1
        end_j = start_x_position + (SHIPS_IDS[ship] - 1)
        while j < end_j:
            if board.board[j][y] != "B":
                board.board[j][y] = "B"
                j = j + 1
            else:
                return True

    print ("llega a activar")

    activate_boat_on_board(ship, board)
    return not_valid

def check_if_boat_on_pos(board, x, y):

    hitted = False
    j = x - 1
    y = y - 1

    if board.board[y][j] == "B":
        hitterd = True

    return hitted

def check_if_boat_is_active(ship, board):
    is_active = False

    if ship == "AC5" and board.aircraft_carrier:
        is_active = True

    elif ship == "BS4" and board.battleship:
        is_active = True

    elif ship == "SUB3" and board.submarine:
        is_active = True

    elif ship == "DES3" and board.destroyer:
        is_active = True

    elif ship == "PB2" and board.patrol_boat:
        is_active = True

    return is_active


def activate_boat_on_board(ship, board):
    """After we assign the boat into the board we activate that boat
    in the board"""
    if ship == "AC5" and not board.aircraft_carrier:
        board.aircraft_carrier = True
    elif ship == "BS4" and not board.battleship:
        board.battleship = True

    elif ship == "SUB3" and not board.submarine:
        board.submarine = True

    elif ship == "DES3" and not board.destroyer:
        board.destroyer = True

    elif ship == "PB2" and not board.patrol_boat:
        board.patrol_boat = True


def log_board_on_console(board):
    for row in board.board:
        print row
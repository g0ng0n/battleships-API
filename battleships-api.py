import logging
import endpoints
import random
import gameutils
from models import User, StringMessage
from protorpc import remote, messages
from google.appengine.ext import ndb
import re


USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))



@endpoints.api(name='battleships', version='v1')
class BattleshipApi(remote.Service):
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                'A User with that name already exists!')

        if gameutils.getRegex(request.email) == None:
            print(' ERROR - invalid email, please try again')
            raise endpoints.ConflictException(
                'invalid email, please try again!')

        user = User(name=request.user_name, email=request.email, board=User.create_empty_board())
        user.put()

        return StringMessage(message='User created!'.format(
            request.user_name))


api = endpoints.api_server([BattleshipApi])
# import random
# import string
# from django_url_framework import ActionController
#
# __author__ = 'zeraien'
#
# class GoogleLoginController(ActionController):
#
#     def _create_state_token(self, request):
#         # Create a state token to prevent request forgery.
#         # Store it in the session for later validation.
#         state = ''.join(random.choice(string.ascii_uppercase + string.digits)
#                       for x in xrange(32))
#         request.session['state'] = state
#         # Set the client ID, token state, and application name in the HTML while
#         # serving it.
#         response = make_response(
#           render_template('index.html',
#                           CLIENT_ID=CLIENT_ID,
#                           STATE=state,
#                           APPLICATION_NAME=APPLICATION_NAME))
#
#     def index(self, request):
#         self._create_state_token(request)
#         return {}
#     def start(self, request):
# https://accounts.google.com/o/oauth2/auth?
#  client_id=424911365001.apps.googleusercontent.com&
#  response_type=code&
#  scope=openid%20email&
#  redirect_uri=https://oa2cb.example.com/&
#  state=security_token%3D138r5719ru3e1%26url%3Dhttps://oa2cb.example.com/myHome&
#  login_hint=jsmith@example.com&
#  openid.realm=example.com&
#  hd=example.com

"""
  gae_console
  ~~~~~~~~~~~~~~~~~~~

  Connects to an App Engine remote api endpoint, by configuring the SDK's
  remote_api_stub.

  Convenience tool to help working with the remote_api. Importing this package
  imports appengine api modules, application db models, and application config
  files.

  :copyright: (c) 2012 by gregorynicholas.
  :license: MIT, see LICENSE for more details.
"""
import sys
from os import path
from os import environ

__all__ = ['remote', 'config_console', 'config_history', 'enable_pdb']


DEFAULT_ENDPOINT_PATH = "/_ah/remote_api"
DEFAULT_ENDPOINT_HOST = 'localhost:8080'


def remote(app_id, hostname, path, email=None, password=None):
  '''
  Attaches to the app_id instance at address (default: <app_id>.appspot.com).

    :param app_id: Required. the app_id of the application to connect to.
    :param path: path to remote_api handler. defaults to: /_ah/remote_api
    :param hostname: defaults to: localhost:8080
    :param email: if you don't specify an email, you will be prompted.
    :param password: if you don't specify a password, you will be prompted.

  if email and password are not specified you will be prompted on
  connection, if needed.

  NOTE: https://code.google.com/p/googleappengine/issues/detail?id=3258
  remote_api does not work with Federated Login/OpenID. in order to use with
  a custom domain, you must set the login method to Google Accounts API.
  '''
  if not hostname:
    address = DEFAULT_ENDPOINT_HOST

  def _auth_input():
    '''Prompts user for credentials.'''
    from getpass import getpass
    return raw_input("Email: "), getpass("Password: ")

  def _auth():
    def _raw(value, *a):
      '''Monkeypatches stdin.'''
      from StringIO import StringIO
      sys.stdin = StringIO(value)
      return ''
    if email and password:
      return (_raw(email), _raw(password))
    elif address == DEFAULT_ENDPOINT_HOST:
      return (_raw(''), _raw(''))
    else:
      return _auth_input()

  from google.appengine.tools import appengine_rpc
  from google.appengine.ext.remote_api import remote_api_stub
  remote_api_stub.ConfigureRemoteApi(
      app_id, path, _auth, hostname,
      rpc_server_factory=appengine_rpc.HttpRpcServer)

  # remote_api_stub.MaybeInvokeAuthentication()
  environ["SERVER_SOFTWARE"] = "Development (remote_api)/1"


# helper methods for configuring the shell..
# --------------------------------------------------------------------------- #

def config_console():
  '''
  Enables tab completion.

  see: http://www.doughellmann.com/PyMOTW/rlcompleter/index.html
  '''
  import rlcompleter, readline
  readline.parse_and_bind('bind ^I rl_complete')

def config_history():
  '''
  Configures bash history.

  see: http://dotfiles.org/~remote/.pythonrc.py
  '''
  import atexit, readline
  histfile = path.join(environ["HOME"], ".remoteapi_history")
  try:
   readline.read_history_file(histfile)
  except IOError:
   pass
  atexit.register(readline.write_history_file, histfile)
  del histfile

def enable_pdb():
  '''
  Enables interactive debugging via python's pdb module.
  '''
  def debugger(type, value, tb):
    import traceback, pdb
    traceback.print_exception(type, value, tb)
    pdb.pm()
  sys.excepthook = debugger


"""
  gae_console
  ~~~~~~~~~~~~~~~~~~~

  Connects to an App Engine remote api endpoint, by configuring the SDK's
  remote_api_stub.

  Convenience tool to help working with the remote_api. Importing this package
  imports appengine api modules, application db models, and application config
  files.
"""
import sys
from os import path
from os import environ
from google.appengine.ext.remote_api import remote_api_stub

__all__ = ['connect_to_app', 'config_console', 'config_history', 'enable_pdb']

_DEFAULT_ENDPOINT_PATH = "/_ah/remote_api"

def connect_to_app(app_id, user=None, password=None, path=None, address=None):
  '''Attaches to the app_id instance at address (default: <app_id>.appspot.com).

    :param app_id: Required. the app_id of the application to connect to.
    :param user: if you don't specify a user you will be prompted.
    :param password: if you don't specify a password you will be prompted.
    :param path: path to remote_api handler. defaults to: /_ah/remote_api
    :param address: defaults to: <app_id>.appspot.com
  '''
  _path = path or _DEFAULT_ENDPOINT_PATH
  if not address:
    address = '{}.appspot.com'.format(app_id)
  _init_remote_api(app_id, _path, address, user, password)

def _auth_input():
  '''Function to prompt user for credentials.'''
  from getpass import getpass
  return raw_input("Email: "), getpass("Password: ")

def _init_remote_api(app_id, path, address, user=None, password=None):
  '''Generic wrapper to initialize the remote_api_stub for a given path.

    :param app_id: Required. the app_id of the application to connect to.
    :param user: if you don't specify a user you will be prompted.
    :param password: if you don't specify a password you will be prompted.
    :param path: the path to the remote_api handler ex: /_ah/remote_api.
    :param address: server to connect to, ex: <app_id>.appspot.com.

  if user and password are not specified you will be prompted on
  connection, if needed.'''
  _auth = _auth_input
  if user and password:
    def _auth():
      return (user, password)
  remote_api_stub.ConfigureRemoteApi(app_id, path, _auth, address)
  remote_api_stub.MaybeInvokeAuthentication()
  environ["SERVER_SOFTWARE"] = "Development (remote_api)/1"


# helper methods for configuring the shell..
# --------------------------------------------------------------------------- #

def config_console():
  '''Enables tab completion.
  # from http://www.doughellmann.com/PyMOTW/rlcompleter/index.html'''
  import rlcompleter, readline
  readline.parse_and_bind('bind ^I rl_complete')

def config_history():
  '''Configures bash history.
  see: http://dotfiles.org/~remote/.pythonrc.py'''
  import atexit, readline
  histfile = path.join(environ["HOME"], ".remoteapi_history")
  try:
   readline.read_history_file(histfile)
  except IOError:
   pass
  atexit.register(readline.write_history_file, histfile)
  del histfile

def enable_pdb():
  '''Enables interactive pdb debugging.'''
  def info(type, value, tb):
    import traceback, pdb
    traceback.print_exception(type, value, tb)
    pdb.pm()
  sys.excepthook = info

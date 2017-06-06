"""In memory model datastore"""

import db_helpers as helpers

def follow_path(obj, path, create_missing=False):
  """Given a dict and a '/' separated path, follow that path and return the
  value at that location.

  Examples:
    obj={ a: { b: { c: { d: 'foo' } } } }
    path="/a/b"
    returns obj['a']['b']

  Arguments:
    obj: the object to look in
    path: the path to follow. Trailing '/' characters are ignored
    create_missing: If true, create any objects along the way needed to
        complete the traversal

  Returns: a reference to the value at the given path. If the path is
  '/' or '', obj is returned.
  """
  if path.endswith('/'):
    path = path[:-1]
  path_parts = path.split('/')[1:]
  for path_part in path_parts:
    if not path_part in obj:
      if create_missing:
        obj[path_part] = {}
      else:
        return None
    obj = obj[path_part]
  return obj

def join_paths(path, suffix):
  """Joins a path and a suffix into a single path.
  Resolves leading and trailing '/'. The suffix can be null.

  Examples:
    join_paths('abc/def/', '/hij') => 'abc/def/hij'
    join_paths('a', 'b/c/d') => 'a/b/c/d'
    join_paths('abc/def', None) => 'abc/def/'
  """
  if not path.endswith('/'):
    path = path + '/'
  if suffix.startswith('/'):
    suffix = suffix[1:]
  if suffix is None:
    suffix = ''
  return '%s%s' % (path, suffix)

def drop_last(path):
  """Returns a path with the last "part" dropped.

  Examples:
    drop_last('abc/def/ghi') => 'abc/def'
    drop_last('abc') => ''
    drop_last('') => ''
  """
  if '/' not in path:
    return ''
  return '/'.join(path.split('/')[:-1])

def last(path):
  """Returns a last "part" of a path.

  Examples:
    last('abc/def/ghi') => 'ghi'
    last('abc') => 'abc'
    last('') => ''
  """
  if '/' not in path:
    return path
  return path.split('/')[-1]

class InMemoryStore:
  """An in memory version of the data in firebase. Mutations applied to the
  store will also apply to the remote version of the data.
  Getting data from the store will return the same results as getting data
  from the remote firebase store.

  CAVEAT:
  Getting data during a transactional mutation (with several mutations)
  locally will return data as if the current mutations in the transaction have
  already been applied (because they have been). Getting data remotely will
  return data as if none of the current mutations have been applied.
  """
  def __init__(self):
    self.instance = None
    self.firebase = None

  def maybe_load(self, firebase):
    """Load the firebase model from the remote source if a local copy
    doesn't exist.
    """
    if self.instance is None and self.firebase is None:
      print '*************** LOADING INSTANCE FROM FIREBASE *******************'
      self.instance = firebase.get('/', None)
      self.firebase = firebase

  def get(self, path, id, params=None, local_instance=False):
    """Get data from the model. Getting data from the local instance and the
    remove instance is the same with some exceptions:
    - Remote fetches don't have mutations from an unclosed transaction,
      local fetches do.
    - params don't do anything in the local instance

    Arguments:
      path: The path to get
      id: The id of the value to get at the path
      params: Filtering and sorting params
      local_instance: If true, gets the data from the local copy,
          if false, gets the data from the remote copy.

    TODO(yuhao93): Make params work locally
    """
    if not local_instance:
      return self.firebase.get(path, id, params)
    obj = follow_path(self.instance, path)
    if obj is None:
      return None
    return obj.get(id)

  def delete(self, path, id):
    """Convenience wrapper for a transaction consisting of only a deletion"""
    transaction = self.transaction()
    transaction.delete(path, id)
    transaction.commit()

  def put(self, path, id, data):
    """Convenience wrapper for a transaction consisting of only a put"""
    transaction = self.transaction()
    transaction.put(path, id, data)
    transaction.commit()

  def patch(self, path, data):
    """Convenience wrapper for a transaction consisting of only a patch"""
    transaction = self.transaction()
    transaction.patch(path, data)
    transaction.commit()

  def transaction(self):
    """Open a transaction for this model."""
    return Transaction(self.firebase, self.instance)

class Transaction:
  """A transaction is an atomic list of mutations that can be applied to the
  model. The mutation set is applied to the remote model only when the
  transaction is committed. All mutations are applied immediately to the
  local model."""
  def __init__(self, firebase, instance):
    self.instance = instance
    self.firebase = firebase
    self.batch_mutation = {}
    self.committed = False

  def delete(self, path, id):
    """Delete a value at a given path and id. If the path/id combo doesn't
    exist, nothing happens.

    Example:
      model = {'abc': { 'def': { 'hij': { 'hello': 'world' } } } }
      delete('abc/def', 'hij')
      model == {'abc': { 'def': { } }

    Arguments:
      path: The path to the location of the value
      id: The id of the value to delete
    """
    if self.committed:
      raise ServerError("Tried to apply mutation to closed transaction")
    self.batch_mutation[join_paths(path, id)] = None
    obj = follow_path(self.instance, path)
    if obj is not None and id in obj:
      del obj[id]

  def put(self, path, id, data):
    """Put a value at a given path and id. If the path/id combo doesn't
    exist, the path is created.

    Example:
      model = {'abc': { } }
      put('abc/def', 'hij', {'hello': 'world'})
      model == {'abc': { 'def': { 'hij': { 'hello': 'world' } } } }

    Arguments:
      path: The path to the location of the value
      id: The key of the value to insert
      data: The value to insert
    """
    if self.committed:
      raise ServerError("Tried to apply mutation to closed transaction")
    self.batch_mutation[join_paths(path, id)] = data
    obj = follow_path(self.instance, path, create_missing=True)
    obj[id] = data

  def patch(self, path, data):
    """Patches a list of changes at a path. If the path/id combo doesn't
    exist, the path is created.

    Example:
      model = {'abc': { 'def': { 'foo': 'bar' } } }
      patch('abc/def', {'hij': {'hello': 'world'}, 'klm': 'mno'})
      model == {'abc':
        { 'def': { 'foo': 'bar', hij': { 'hello': 'world' }, 'klm': 'mno' } } }

    Arguments:
      path: The path at which to apply the patches
      data: The values to insert. A dict of ids(or sub paths) to values
    """
    if self.committed:
      raise ServerError("Tried to apply mutation to closed transaction")
    for key, value in data.iteritems():
      self.batch_mutation[join_paths(path, key)] = value
      obj = follow_path(self.instance, join_paths(path, drop_last(key)), create_missing=True)
      obj[last(key)] = value

  def commit(self):
    """Applies all mutations in the transaction to the remote model.
    Must be called for every transaction opened. Deleting a transaction without
    calling commit will throw an error.

    TODO(yuhao93): Currently, transactions that have mutations which touch
    upon the same path may result in incorrect states. Fix that.
    """
    self.firebase.patch('/', self.batch_mutation)
    self.committed = True

  def __del__(self):
    """Require transactions to be committed before they are deleted."""
    if not self.committed:
      raise helpers.ServerError(
          "Transaction was deleted with uncommitted changes remaining.")

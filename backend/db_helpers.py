"""DB helper methods."""

import constants

# ID entity types
ENTITY_TYPES = (
    'chatRoomId', 'gameId', 'groupId', 'gunId', 'messageId',
    'missionId', 'playerId', 'rewardCategoryId', 'rewardId', 'userId',
    'notificationId')

# Map all expected args to an entity type
KEY_TO_ENTITY = {a: a for a in ENTITY_TYPES}
KEY_TO_ENTITY.update({
  'adminUserId': 'userId', 'otherPlayerId': 'playerId',
  'ownerPlayerId': 'playerId'
})


# Mapping from a key name to where in Firebase it can be found
# along with a specific value that can be used to validate existance.
ENTITY_PATH = {
  'gameId': ['/games/%s', 'name'],
  'userId': ['/users/%s', 'name'],
  'groupId': ['/groups/%s', 'gameId'],
  'playerId': ['/players/%s', 'userId'],
  'gunId': ['/guns/%s', 'a'],
  'missionId': ['/missions/%s', 'name'],
  'chatRoomId': ['/chatRooms/%s', 'name'],
  'rewardCategoryId': ['/rewardCategories/%s', 'name'],
  'rewardId': ['/rewards/%s', 'a'],
  'notificationId': ['/notifications/%s', None],
}


class InvalidInputError(Exception):
  """Error used when the inputs fail to pass validation."""
  pass


def EntityExists(firebase, key, value):
  path, item = ENTITY_PATH[KEY_TO_ENTITY[key]]
  return (firebase.get(path % value, item) is not None)


def ValidateInputs(request, firebase, required, valid):
  """Validate args.

  Keys in valid starting with a '!' are testing to ensure they do *not* exist.
  Any request item ending with Id eg 'fooId' must have a value starting 'foo-'

  Args:
    required: These args must be present in the request.
    valid: These args must already exist in the DB.

  Raises: InvalidInputError if validation does not pass.
  """
  if request is None:
    request = {}

  r_keys = set()
  for key in required:
    if key[0] == '!':
      key = key[1:]
    r_keys.add(key)
  supplied = set(request.keys())

  if r_keys - supplied:
    raise InvalidInputError('Missing required input.\n Missing: %s.\n Required: %s' % (
        ', '.join(r_keys - supplied), ', '.join(required)))

  # Any keys fooId must start "foo-XXX"
  for key in request:
    if key.endswith('Id'):
      if key in KEY_TO_ENTITY:
        entity = KEY_TO_ENTITY[key]
        if not request[key].startswith('%s-' % entity[:-2]):
          raise InvalidInputError('Id %s="%s" must start with "%s-".' % (
              key, request[key], entity[:-2]))
      else:
        raise InvalidInputError('Key %s looks like an undefined entity.' % key)


  for key in valid:
    negate = False
    if key[0] == '!':
      negate = True
      key = key[1:]
    if key not in request:
      continue
    data = request[key]

    if key in KEY_TO_ENTITY and KEY_TO_ENTITY[key] in ENTITY_PATH:
      exists = EntityExists(firebase, key, data)
      if negate and exists:
        raise InvalidInputError('%s %s must not exist but was found.' % (key, data))
      elif not negate and not exists:
        raise InvalidInputError('%s %s is not valid.' % (key, data))
    elif key in ('allegiance', 'allegianceFilter'):
      if data not in constants.ALLEGIANCES:
        raise InvalidInputError('Allegiance %s is not valid.' % data)
    else:
      raise InvalidInputError('Unhandled arg validation: "%s"' % key)


def GroupToGame(firebase, group):
  """Map a group to a game."""
  return firebase.get('/groups/%s' % group, 'gameId')


def GroupToEntity(firebase, group, entity):
  rooms = firebase.get(
      '/', entity, {'orderBy': '"groupId"', 'equalTo': '"%s"' % group})
  if rooms:
    return rooms.keys()
  return []


def GroupToMissions(firebase, group):
  return GroupToEntity(firebase, group, 'missions')


def GroupToChats(firebase, group):
  return GroupToEntity(firebase, group, 'chatRooms')


def PlayerToGame(firebase, player):
  """Map a player to a game."""
  return firebase.get('/players/%s' % player, 'gameId')


def PlayerAllegiance(firebase, player):
  """Map a player to an allegiance."""
  game = PlayerToGame(firebase, player)
  return firebase.get('/games/%s/players/%s' % (game, player), 'allegiance')


def ChatToGroup(firebase, chat):
  """Map a chat to a group."""
  return firebase.get('/chatRooms/%s' % chat, 'groupId')


def ChatToGame(firebase, chat):
  """Map a chat to a group."""
  group = ChatToGroup(firebase, chat)
  if group is None:
    return None
  return GroupToGame(group)



from ucollections import OrderedDict, deque

from . import webapp
from . import state_filter
from utilities import config, timestamp, ids


# eid -> str, float | int | str | bool
_STATE = OrderedDict()

_TOTAL_UPDATES = 0
_SENT_UPDATES = 0


def stats():
    return (_TOTAL_UPDATES, _SENT_UPDATES)


class EntityValue:

    _state_filters = None
    
    def __init__(self, did: str, aid: str):
        self._value = None

        # setup configuration for this entity
        self._entity_config = entity_config = config.get_entity_config(did, aid)
        self._transform = entity_config.get('transform')
        self._unit = entity_config.get('unit', '')
        history = entity_config.get('history', 0)
        self._history = deque((), history) if history > 0 else None

        # filters
        if not self._state_filters:
            # dict of all available filters { 'lpf': LpfFilter, ... }
            self._state_filters = { f.lower()[:-6]: eval(f"state_filter.{f}") for f in dir(state_filter) if f.endswith('Filter') }
        # list of filters for this entity
        spec = [ next(iter(f.items())) if isinstance(f, dict) else (f, None) for f in entity_config.get('filter') ]
        try:
            self._filters = [ self._state_filters[f[0]](f[1]) for f in spec ]
        except KeyError:
            self._filters = [ state_filter.DuplicateFilter(None) ]
        
    @property
    def value(self) -> float | int | str | bool:
        return self._value
    
    @property
    def history(self) -> list:
        h = self._history
        data = []
        # non-destructively coax data out of micropython deque
        for i in range(len(h)):
            x = h.popleft()
            h.append(x)
            data.append(x)
        return data
        
    async def update(self, value: float | int | str | bool ) -> float | int | str | bool | None:
        """Update entity value.
        :return: New value or None, if change filtered.
        """
        # apply filters
        for f in self._filters:
            try:
                value = f.filter(value)
            except Exception as e:
                await webapp.error(f"Error in {f}.filter({value}): {e}")
            if value == None:
                # update filtered out
                return None
            
        # update state
        self._value = value
        if self._history != None: 
            self._history.append((timestamp(), value))

        return value
    
    def __str__(self):
        return f"{self.value}, history = {self.history}"
    

async def update(did: str, aid: str, value: float | int | str | bool):
    """Update device state.
    :param did:     ID of device to update.
    :param aid:     ID of attribute to update.
    :param value:   new value
    """
    global _STATE, _TOTAL_UPDATES, _SENT_UPDATES
    _TOTAL_UPDATES += 1

    if config.get('devices', did, 'entities', aid) == None:
        # record the attribute in config.json
        config.set('devices', did, 'entities', aid, {})

    # update local state
    eid = ids.eid(did, aid)
    try:
        ev = _STATE[eid]
    except KeyError:
        # define new entity
        ev = EntityValue(did, aid)
        _STATE[eid] = ev

    new_value = await ev.update(value)

    if  new_value != None:
        _SENT_UPDATES += 1
        await webapp.send_all({ 'tag': 'state_update', 'eid': eid, 'value': new_value }) 


async def send_current_state(webapp):
    """Send the current state to channel."""
    global _STATE
    # put this in an at least semi-ordered state ...
    _STATE = OrderedDict(sorted(_STATE.items()))
    for eid, ev in _STATE.items():
        update = { 'tag': 'state_update', 'eid': eid, 'value': ev.value, 'all': True }
        await webapp.send(update)


def get(did, aid) -> EntityValue:
    global _STATE
    return _STATE.get((did, aid))


def get_current_state() -> dict:
    # pointer to state table - 
    # debugging only - don't modify
    global _STATE
    return _STATE
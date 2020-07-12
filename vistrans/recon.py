"""
A Proposal for reconciliation graph and reconciliation interface.
"""
from abc import ABC  # Abstract Base Classes
from typing import List, Dict
from enum import Enum

__all__ = ['MappingNode', 'EventType', 'Event', 'Cospeciation', 'Duplication', 'Transfer', 'Loss',
           'TipTip', 'Reconciliation', 'ReconGraph']

class MappingNode:
    """
    MappingNode is a node in the reconciliation graph that maps
    a parasite to a host.
    """
    def __init__(self, parasite_vertex: str, host_vertex: str):
        self._parasite = parasite_vertex
        self._host = host_vertex

    @property
    def parasite(self) -> str:
        return self._parasite

    @property
    def host(self) -> str:
        return self._host
    
    def __eq__(self, other):
        if type(self) == type(other):
            return self._parasite == other.parasite and self._host == other.host
        return False
    
    def __hash__(self):
        return hash((self._parasite, self._host))
    
    def __repr__(self):
        return "%s(%s, %s)" % (type(self).__name__, self._parasite, self._host)

class EventType(Enum):
    """
    EventType is the type of event node.
    """
    COSPECIATION = 1
    DUPLICATION = 2
    TRANSFER = 3
    LOSS = 4
    TIPTIP = 5

class Event(ABC):
    """
    Base Class for events.
    """
    def __init__(self, freq: float = None):
        self._freq = freq

    @property
    def freq(self) -> float:
        return self._freq

    @property
    def event_type(self) -> EventType:
        """
        Returns the event type of this event.
        """
        raise NotImplementedError("Event is an abstract base class")

class TwoChildrenEvent(Event, ABC):
    """
    Base Class for events with two children.
    """
    def __init__(self, left: MappingNode, right: MappingNode, freq=None):
        """
        Creates a Cospeciation, Duplication, or Transfer event. The event node
        has two children MappingNodes called left and right.
        """
        super().__init__(freq)
        self._left: MappingNode = left
        self._right: MappingNode = right

    @property
    def left(self) -> MappingNode:
        return self._left

    @property
    def right(self) -> MappingNode:
        return self._right
    
    def __eq__(self, other):
        if type(self) == type(other):
            return self._left == other.left and self._right == other.right
        return False
    
    def __hash__(self):
        return hash((self._left, self._right))
    
    def __repr__(self):
        return "%s(%s, %s)" % (type(self).__name__, self._left, self._right)

class Cospeciation(TwoChildrenEvent):
    """
    Cospeciation is an event where two children of the parasite vertex
    maps to the two children of the host vertex. Cospeciation event has
    two child MappingNode named left and right.
    """

    @property
    def event_type(self) -> EventType:
        return EventType.COSPECIATION

class Duplication(TwoChildrenEvent):
    """
    Duplication is an event where two children of the parasite vertex
    maps to the same host vertex as their parent. Cospeciation event has
    two child MappingNode named left and right.
    """

    @property
    def event_type(self) -> EventType:
        return EventType.DUPLICATION

class Transfer(TwoChildrenEvent):
    """
    Transfer is an event where one child of the parasite vertex
    maps to the same host vertex as its parent, while the other child maps 
    to a host vertex not ancestrally related to the first one. Transfer event 
    has two child MappingNode named left and right. The right child is always
    the child that gets transferred.
    """

    @property
    def event_type(self) -> EventType:
        return EventType.TRANSFER

class Loss(Event):
    """
    Loss is an event where the parasite vertex goes down to only one of 
    the lineage of the host vertex when the host vertex speciates. Loss event
    has one child MappingNode called child. The parasite of the child MappingNode
    (self.child.parasite) is the same as the parasite of the MappingNode that
    incurs the lost.
    """

    def __init__(self, child: MappingNode, freq=None):
        """
        Creates a Loss event. The lost event has one child MappingNode
        called child.
        """
        super().__init__(freq)
        self._child = child

    @property
    def child(self) -> MappingNode:
        return self._child
    
    def __eq__(self, other):
        return type(self) == type(other) and self._child == other.child
    
    def __hash__(self):
        return hash(self._child)
    
    def __repr__(self):
        return "%s(%s)" % (type(self).__name__, self._child)

    @property
    def event_type(self) -> EventType:
        return EventType.LOSS

class TipTip(Event):
    """
    TipTip (tip mapping) is an event where both the parasite and the host are 
    leaves. Biologically, this means the parasite and the host lives together
    at present time. The TipTip event is the sink of the reconciliation graph and
    has no children.
    """

    def __init__(self, freq: float = None):
        """
        Creates a TipTip (tip to tip mapping) event. The TipTip event has 
        no children mapping nodes.
        """
        super().__init__(freq)

    def __repr__(self):
        return "%s()" % type(self).__name__

    @property
    def event_type(self) -> EventType:
        return EventType.TIPTIP

class Reconciliation:
    """
    Reconciliation is a tree that represents an edge-to-edge mapping from 
    a parasite tree to a host tree. The Reconciliation starts with source
    MappingNode where the parasite first enters the host. Each MappingNode
    has one corresponding Event. Each event has up to two children MappingNode
    depending on its type. The leaves of the tree are the TipTip events which
    have no children MappingNode.
    """
    def __init__(self, source: MappingNode, initial_map: Dict[MappingNode, Event] = {}):
        """
        Creates a Reconciliation tree. The Reconciliation starts with source
        MappingNode where the parasite first enters the host.
        """
        self.source = source
        self._map = initial_map
        self._parasite_map: Dict[str, MappingNode] = {}
    
    def __eq__(self, other):
        return type(self) == type(other) and self._map == other._map
    
    def __repr__(self):
        return "%s(source=%s, %s)" % (type(self).__name__, self.source, self._map)
    
    def set_event(self, mapping: MappingNode, event: Event):
        """
        Set the event corresponding to mapping.
        """
        if event.event_type is not EventType.LOSS:
            self._parasite_map[mapping.parasite] = mapping
        self._map[mapping] = event
    
    def event_of(self, mapping: MappingNode) -> Event:
        """
        Get the event corresponding to mapping.
        """
        return self._map[mapping]

    def mapping_of(self, parasite: str) -> MappingNode:
        """
        Returns the MappingNode of the parasite vertex. This is where that
        parasite vertex maps to. Never returns a mapping node that corresponds
        to a loss event.
        """
        return self._parasite_map[parasite]
    
    def is_sink(self, mapping: MappingNode) -> bool:
        """
        Whether the host and the parasite of the mapping are leaves of its
        phylogenic tree with a tip mapping.
        """
        return self._map[mapping].event_type is EventType.TIPTIP
    
    def save(self, path: str, metadata: Dict[str, str] = {}):
        """
        Save the Reconciliation to path, e.g. ``recon.save('./reconname')``
        This will save the Reconciliation along with the metadata if metadata
        is specified, e.g. ``recon.save('./reconname', {'created_at': 'Noon'})``.
        The metadata is only for book-keeping purposes and is not read when load.
        """
        raise NotImplementedError
    
    @staticmethod
    def load(path) -> 'Reconciliation':
        """
        Load a Reconciliation from path, e.g. ``Reconciliation.load('./reconname')``.
        """
        raise NotImplementedError

class ReconGraph:
    """
    ReconGraph is a directed acyclic graph that compactlyrepresent multiple 
    Reconciliations. The Reconciliation starts with a list of source MappingNode
    where the parasite first enters the host. Each MappingNode has a list of 
    corresponding Event. Each event has up to two children MappingNode
    depending on its type. The sinks of this graph are the TipTip events which
    have no children MappingNode.
    """
    def __init__(self, sources: List[MappingNode], initial_map: Dict[MappingNode, List[Event]] = {}):
        """
        Creates a ReconGraph. The ReconGraph starts with source
        MappingNode where the parasite first enters the host.
        """
        self.sources = sources
        self._map = initial_map
    
    def __eq__(self, other):
        return type(self) == type(other) and self._map == other._map
    
    def __repr__(self):
        return "%s(sources=%s, %s)" % (type(self).__name__, self.sources, self._map)
    
    def add_event(self, mapping: MappingNode, event: Event):
        """
        Add an event corresponding to mapping.
        """
        if mapping not in self._map:
            self._map[mapping] = []
        self._map[mapping].append(event)

    def set_events(self, mapping: MappingNode, events: List[Event]):
        """
        Set a mapping to correspond to a list of events.
        """
        self._map[mapping] = events
    
    def events_of(self, mapping: MappingNode) -> List[Event]:
        """
        Get a list of events corresponding to mapping.
        """
        return self._map[mapping].copy()
    
    def is_sink(self, mapping: MappingNode) -> bool:
        """
        Whether the host and the parasite of the mapping are leaves of its
        phylogenic tree with a tip mapping.
        """
        return len(self._map[mapping]) == 1 and self._map[mapping][0].event_type is EventType.TIPTIP
    
    def enumerate(self) -> List[Reconciliation]:
        """
        Returns all Reconciliation represented in this ReconGraph.
        """
        raise NotImplementedError

    def save(self, path: str, metadata: Dict[str, str] = {}):
        """
        Save the ReconGraph to path, e.g. ``recon.save('./reconname')``
        This will save the reconciliation graph along with the metadata if metadata
        is specified, e.g. ``recon.save('./reconname', {'created_at': 'Noon'})``.
        The metadata is only for book-keeping purposes and is not read when load.
        """
        raise NotImplementedError
    
    @staticmethod
    def load(path) -> 'ReconGraph':
        """
        Load a Reconciliation from path, e.g. ``Reconciliation.load('./reconname')``.
        """
        raise NotImplementedError

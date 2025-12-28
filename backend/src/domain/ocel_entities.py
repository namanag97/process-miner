"""OCEL Domain Entities - Object-Centric Event Log entities.

These entities support OCEL 2.0 standard for Object-Centric Process Mining (OCPM).
Unlike traditional event logs where events belong to a single case,
OCEL allows events to be linked to multiple object types.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any
from uuid import UUID, uuid4


@dataclass
class ObjectType:
    """An object type in an OCEL log (e.g., 'Order', 'Item', 'Package').
    
    Object types define the categories of objects that events can relate to.
    Each object type can have its own set of attributes.
    """
    id: UUID
    name: str
    attributes: dict[str, str] = field(default_factory=dict)  # attr_name -> data_type
    
    @classmethod
    def create(cls, name: str, **attributes: str) -> "ObjectType":
        """Factory method to create an ObjectType."""
        return cls(id=uuid4(), name=name, attributes=attributes)


@dataclass
class ObjectInstance:
    """A specific object instance (e.g., Order-123, Item-456).
    
    Represents a concrete object of a given type with its attributes.
    """
    id: UUID
    object_type: str
    object_id: str  # Business identifier (e.g., "ORD-123")
    attributes: dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(cls, object_type: str, object_id: str, **attributes) -> "ObjectInstance":
        """Factory method to create an ObjectInstance."""
        return cls(
            id=uuid4(),
            object_type=object_type,
            object_id=object_id,
            attributes=attributes
        )


@dataclass
class ObjectCentricEvent:
    """An event linked to multiple objects.
    
    Unlike traditional process events that belong to a single case,
    object-centric events can be related to multiple objects of different types.
    For example, a "pick item" event might relate to both an Order and an Item.
    """
    id: UUID
    activity: str
    timestamp: datetime
    object_ids: list[str] = field(default_factory=list)  # List of object business IDs
    attributes: dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        activity: str,
        timestamp: datetime,
        object_ids: Optional[list[str]] = None,
        **attributes
    ) -> "ObjectCentricEvent":
        """Factory method to create an ObjectCentricEvent."""
        return cls(
            id=uuid4(),
            activity=activity,
            timestamp=timestamp,
            object_ids=object_ids or [],
            attributes=attributes
        )


@dataclass
class ObjectRelationship:
    """Relationship between two objects.
    
    Represents object-to-object relationships (e.g., Order contains Items).
    """
    id: UUID
    source_object_id: str
    target_object_id: str
    relationship_type: str
    
    @classmethod
    def create(
        cls,
        source_object_id: str,
        target_object_id: str,
        relationship_type: str
    ) -> "ObjectRelationship":
        """Factory method to create an ObjectRelationship."""
        return cls(
            id=uuid4(),
            source_object_id=source_object_id,
            target_object_id=target_object_id,
            relationship_type=relationship_type
        )


@dataclass
class ObjectCentricEventLog:
    """OCEL log containing events linked to multiple object types.
    
    This is the main data structure for Object-Centric Process Mining.
    It contains:
    - Object types: Categories of objects (e.g., Order, Item)
    - Objects: Individual object instances
    - Events: Activities linked to one or more objects
    - Relationships: Object-to-object relationships
    """
    id: UUID
    name: str
    source_file: Optional[str] = None
    source_format: str = "jsonocel"
    object_types: list[ObjectType] = field(default_factory=list)
    objects: list[ObjectInstance] = field(default_factory=list)
    events: list[ObjectCentricEvent] = field(default_factory=list)
    relationships: list[ObjectRelationship] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def total_events(self) -> int:
        """Get total number of events."""
        return len(self.events)
    
    @property
    def total_objects(self) -> int:
        """Get total number of objects."""
        return len(self.objects)
    
    @property
    def total_object_types(self) -> int:
        """Get total number of object types."""
        return len(self.object_types)
    
    @property
    def activities(self) -> set[str]:
        """Get all unique activities."""
        return {event.activity for event in self.events}
    
    def get_objects_by_type(self, object_type: str) -> list[ObjectInstance]:
        """Get all objects of a specific type."""
        return [obj for obj in self.objects if obj.object_type == object_type]
    
    def get_events_for_object(self, object_id: str) -> list[ObjectCentricEvent]:
        """Get all events related to a specific object."""
        return [event for event in self.events if object_id in event.object_ids]
    
    @classmethod
    def create(
        cls,
        name: str,
        source_file: Optional[str] = None,
        source_format: str = "jsonocel"
    ) -> "ObjectCentricEventLog":
        """Factory method to create an ObjectCentricEventLog."""
        return cls(
            id=uuid4(),
            name=name,
            source_file=source_file,
            source_format=source_format
        )
    
    def add_object_type(self, object_type: ObjectType) -> None:
        """Add an object type to the log."""
        self.object_types.append(object_type)
    
    def add_object(self, obj: ObjectInstance) -> None:
        """Add an object instance to the log."""
        self.objects.append(obj)
    
    def add_event(self, event: ObjectCentricEvent) -> None:
        """Add an event to the log."""
        self.events.append(event)
    
    def add_relationship(self, relationship: ObjectRelationship) -> None:
        """Add an object relationship to the log."""
        self.relationships.append(relationship)

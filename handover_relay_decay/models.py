"""Core data model for the handover relay simulation.

A patient carries a structured item set into the relay chain. Each item
has a type, a label drawn from a synthetic pool, and a criticality flag.
Criticality is a property of the item as seeded: allergies and active
infusions are always critical; pending results and watch items are
critical only when flagged; routine notes are never critical.
"""

ITEM_TYPES = (
    "allergy",
    "pending_result",
    "active_infusion",
    "watch_item",
    "routine_note",
)

ALWAYS_CRITICAL = ("allergy", "active_infusion")

# Per-relay survival probability of an item under the reference
# (free-text) policy, before any policy modifier is applied. These are
# declared simulation parameters, seeded by design, not measured from
# real handovers.
BASE_SURVIVAL = {
    "allergy": 0.94,
    "pending_result": 0.89,
    "active_infusion": 0.96,
    "watch_item": 0.86,
    "routine_note": 0.80,
}


class Item(object):
    """One structured handover item."""

    def __init__(self, item_id, item_type, label, critical):
        if item_type not in ITEM_TYPES:
            raise ValueError("unknown item type: %s" % item_type)
        self.item_id = item_id
        self.item_type = item_type
        self.label = label
        self.critical = bool(critical)

    def to_dict(self):
        return {
            "item_id": self.item_id,
            "item_type": self.item_type,
            "label": self.label,
            "critical": self.critical,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["item_id"],
            data["item_type"],
            data["label"],
            data["critical"],
        )

    def __repr__(self):
        return "Item(%s, %s, critical=%s)" % (
            self.item_id, self.item_type, self.critical)


class Patient(object):
    """A synthetic patient entering the relay chain with an item set."""

    def __init__(self, patient_id, items):
        self.patient_id = patient_id
        self.items = list(items)

    def critical_items(self):
        return [item for item in self.items if item.critical]

    def items_of_type(self, item_type):
        return [item for item in self.items if item.item_type == item_type]

    def to_dict(self):
        return {
            "patient_id": self.patient_id,
            "items": [item.to_dict() for item in self.items],
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["patient_id"],
            [Item.from_dict(raw) for raw in data["items"]],
        )

    def __repr__(self):
        return "Patient(%s, %d items)" % (self.patient_id, len(self.items))

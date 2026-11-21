"""Handover compression policies and repair interventions.

A policy acts on the per-relay loss rate (1 - base survival):

- loss_scale multiplies the loss. Structured formats (SBAR, checklist)
  lose less per relay than a free-text summary.
- pin_critical carries critical items in a pinned section that is never
  compressed: their loss is multiplied by PIN_LOSS_SCALE instead.
- readback_recovery is the probability that an item dropped at a relay
  is caught and restored when the receiver reads the handover back.
"""

PIN_LOSS_SCALE = 0.08


class Policy(object):
    def __init__(self, name, loss_scale, readback_recovery=0.0,
                 pin_critical=False, description=""):
        self.name = name
        self.loss_scale = float(loss_scale)
        self.readback_recovery = float(readback_recovery)
        self.pin_critical = bool(pin_critical)
        self.description = description

    def to_dict(self):
        return {
            "name": self.name,
            "loss_scale": self.loss_scale,
            "readback_recovery": self.readback_recovery,
            "pin_critical": self.pin_critical,
            "description": self.description,
        }

    def __repr__(self):
        return "Policy(%s)" % self.name


POLICIES = {
    "free_text": Policy(
        "free_text", loss_scale=1.0,
        description="Free-text summary, no structure enforced."),
    "sbar": Policy(
        "sbar", loss_scale=0.78,
        description="SBAR-structured handover (Situation, Background, "
                    "Assessment, Recommendation)."),
    "checklist": Policy(
        "checklist", loss_scale=0.58,
        description="Checklist-forced handover: every item class must "
                    "be explicitly carried or struck through."),
    "checklist_readback": Policy(
        "checklist_readback", loss_scale=0.58, readback_recovery=0.45,
        description="Checklist plus read-back: the receiver repeats the "
                    "items back and dropped items can be recovered."),
    "checklist_pinning": Policy(
        "checklist_pinning", loss_scale=0.58, pin_critical=True,
        description="Checklist plus critical-item pinning: critical "
                    "items travel in a pinned section that is never "
                    "compressed away."),
    "checklist_pinning_readback": Policy(
        "checklist_pinning_readback", loss_scale=0.58,
        readback_recovery=0.45, pin_critical=True,
        description="Checklist plus pinning plus read-back: both repair "
                    "interventions combined."),
}

POLICY_ORDER = (
    "free_text",
    "sbar",
    "checklist",
    "checklist_readback",
    "checklist_pinning",
    "checklist_pinning_readback",
)


def get_policy(name):
    if name not in POLICIES:
        raise ValueError("unknown policy: %s" % name)
    return POLICIES[name]

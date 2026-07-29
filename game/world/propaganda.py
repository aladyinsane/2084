"""
The propaganda engine (v0.25, ADR 0017): giving the district alert level a
voice.

`watch.get_alert()` already exists and already drives patrol density
(typeclasses/scripts.py's PatrolManagerScript) -- that reactivity is real,
it's just silent. This module doesn't invent a new mechanic; it narrates
one that already runs. A small rolling tally of sabotage/courier activity
*since the last bulletin* (reset every time one fires, never a lifetime
count) plus the existing alert level decide which tier of headline the
PropagandaScript broadcasts, if any -- aggregate and anonymous only, never
naming a citizen.
"""

import random

from evennia.server.models import ServerConfig

from world import tuning

REGISTRY_KEY = "sector9_propaganda_tally"

QUIET_BULLETINS = [
    "|=mThe loudspeakers deliver a routine bulletin: production figures, "
    "unremarkable, met with the usual silence.|n",
    "|=mSomewhere, a loudspeaker clears its throat, has nothing urgent to "
    "say, and says it anyway.|n",
]

LOW_BULLETINS = [
    "|=mThe loudspeakers note \"isolated incidents, promptly addressed\" "
    "and move on to production figures.|n",
    "|=mA bulletin mentions \"routine irregularities\" in a tone that "
    "discourages asking which.|n",
]

ELEVATED_BULLETINS = [
    "|yThe loudspeakers report \"foreign-directed sabotage\" in Sector 9, "
    "\"isolated, and already contained.\"|n Isolated is doing a lot of "
    "work in that sentence.",
    "|yA bulletin credits \"vigilant citizens\" with a string of recent "
    "recoveries the Watch would rather you didn't ask about directly.|n",
]

HIGH_BULLETINS = [
    "|rThe loudspeakers escalate: \"a coordinated campaign of sabotage\" "
    "is underway, and \"additional patrols are a precaution, not a "
    "response.\"|n You have, by now, seen the patrols.",
    "|rThe bulletin's tone changes register entirely: \"heightened "
    "vigilance\" is asked of every citizen, twice, in case the first "
    "time didn't land.|n The grey uniforms on the street already agree.",
]


def _registry():
    return ServerConfig.objects.conf(REGISTRY_KEY, default={"sabotage": 0, "courier": 0}) or {
        "sabotage": 0,
        "courier": 0,
    }


def _save_registry(reg):
    ServerConfig.objects.conf(REGISTRY_KEY, value=reg)


def record(event_type):
    """Tally one qualifying event since the last bulletin fired."""
    reg = _registry()
    reg[event_type] = reg.get(event_type, 0) + 1
    _save_registry(reg)


def pick_bulletin():
    """
    Consume the rolling tally and the current alert level, and return one
    bulletin line, or None for a tick that stays silent. Always resets the
    tally -- called only when there's someone online to hear the result
    (see PropagandaScript), so a tally built up while nobody was connected
    is preserved for whenever someone next returns.
    """
    from world import watch

    reg = _registry()
    total = reg.get("sabotage", 0) + reg.get("courier", 0)
    alert = watch.get_alert()
    _save_registry({"sabotage": 0, "courier": 0})

    if alert >= tuning.ALERT_MAX or total >= tuning.PROPAGANDA_HIGH_THRESHOLD:
        return random.choice(HIGH_BULLETINS)
    if alert >= 1 or total >= tuning.PROPAGANDA_ELEVATED_THRESHOLD:
        return random.choice(ELEVATED_BULLETINS)
    if total >= 1:
        return random.choice(LOW_BULLETINS)
    if random.random() < tuning.PROPAGANDA_QUIET_CHANCE:
        return random.choice(QUIET_BULLETINS)
    return None

"""
The Grid hears you (v0.14): what happens when a command doesn't exist.

The ten-persona playtest found Evennia's default no-match reply failing all
three of its jobs at once: it suggested the unsanctioned curriculum
(`sabotage`, `stash`) to brand-new citizens, it suggested engine verbs
(`charcreate`, `setdesc`) no citizen should ever see, and it answered the
commonest newbie error — a direction with no exit — with noise.

This module replaces it. Three layers, checked in order:

1. **Directions.** A compass word with no exit answers with what actually
   leads out. `go <exit>` walks it.
2. **Instinct verbs.** The things players predictably type at a game
   (kill, hide, talk, cast, where...) each get a bespoke line in the
   world's voice, with a mechanical pointer where one exists. The "no
   combat" thesis gets to speak the first time someone types `kill`.
3. **Filtered suggestions.** Everything else fuzzy-matches against the
   sanctioned surface only — never the chalk's verbs, never the engine's.
"""

from evennia import Command
from evennia.commands.cmdhandler import CMD_NOMATCH
from evennia.utils.utils import string_suggestions

_DIRECTIONS = {
    "north": "north", "n": "north",
    "south": "south", "s": "south",
    "east": "east", "e": "east",
    "west": "west", "w": "west",
    "up": "up", "u": "up",
    "down": "down", "d": "down",
    "northeast": "northeast", "ne": "northeast",
    "northwest": "northwest", "nw": "northwest",
    "southeast": "southeast", "se": "southeast",
    "southwest": "southwest", "sw": "southwest",
}

# What a wrong guess is allowed to be corrected *to*: the sanctioned
# surface plus the basics. The chalk's verbs are learned in the dark or
# not at all; the engine's verbs are nobody's business.
_SUGGESTABLE = (
    "look", "map", "dossier", "grade", "errands", "next", "help",
    "report", "work", "observe", "listen", "petition", "apply",
    "list", "buy", "wear", "remove", "say", "who", "inventory",
    "get", "drop", "give", "quit",
)

# Talked-at NPCs answer in their own voice if they have one (round-two
# playtest finding 6, from round one's finding 2) — checked before the
# generic instinct line below, which stays as the fallback for empty
# rooms and NPCs nobody's written a brush-off for yet.
_TALK_TRIGGERS = ("talk", "ask", "greet", "hello", "chat")

# (trigger words) -> the world's answer. First match wins; {exits} and
# {room} are filled in. Checked against the first word of the input.
_INSTINCTS = (
    (
        ("kill", "attack", "fight", "murder", "strike", "stab", "shoot",
         "punch", "hit"),
        "Your hands remember an older grammar. Nothing in Sector 9 answers "
        "to it: nobody here dies of violence — they die of paperwork, and "
        "paperwork is a thing you can learn. |=m(Conflict on the Grid is "
        "waged in files, standing, and trust. |chelp the grid|=m is where "
        "it starts.)|n"
    ),
    (
        ("flee", "run", "escape"),
        "Running only draws the eye; walking is still legal everywhere. "
        "|=m(The ways out of {room}: {exits}.)|n"
    ),
    (
        ("cast", "spell", "enchant", "pray"),
        "You mouth the old words. The loudspeakers do not pause. Nothing "
        "has answered on that channel in a very long time."
    ),
    (
        ("hide", "sneak", "stealth", "lurk"),
        "There is no hiding, citizen; there are only places nothing "
        "watches. |=m(Dark rooms are their own concealment — |chelp "
        "visibility|=m. The map knows which is which: |cmap|=m.)|n"
    ),
    (
        _TALK_TRIGGERS,
        "Citizens speak with |csay|n; most of Sector 9 has learned not to "
        "answer. |=m(Those with uses for you show them when you |clook|=m "
        "at them, or through |cerrands|=m.)|n"
    ),
    (
        ("where",),
        "You are at {room}. |=m(Your own recollection of the sector: "
        "|cmap|=m.)|n"
    ),
    (
        ("read",),
        "Reading is |clook|ning, citizen, and it is still legal. Rooms, "
        "placards, marks on walls: |clook|n at them."
    ),
    (
        ("stats", "status", "score"),
        "Your figures are kept for you, as everything is kept for you: "
        "|cdossier|n for the file, |cgrade|n for the ladder."
    ),
    (
        ("steal", "rob", "pickpocket", "loot"),
        "Property crime, citizen? The Grid confiscated everything worth "
        "stealing before you were registered. What changes hands here "
        "changes hands quietly, between people who trust each other. "
        "Learn what that costs."
    ),
)


class CmdNoMatch(Command):
    """
    Fires when nothing else matches the input. `self.args` is the raw line.
    """

    key = CMD_NOMATCH
    locks = "cmd:all()"
    auto_help = False

    def _exits(self):
        location = self.caller.location
        if not location:
            return []
        return [ex.key for ex in location.exits]

    def _npc_deflection(self, words):
        """
        A talked-at NPC's own brush-off, if the room has one with a line
        written for it. `words` is the input minus the trigger verb; a
        named target ("ask clerk", "talk to the archivist") is matched
        first, falling back to the room's only deflecting NPC if there's
        exactly one and nothing else narrows it down.
        """
        location = self.caller.location
        if not location:
            return None
        speakers = [
            obj for obj in location.contents
            if obj is not self.caller and obj.attributes.has("deflection")
        ]
        if not speakers:
            return None
        target_words = [w for w in words if w not in ("to", "at", "about", "the")]
        if target_words:
            target = target_words[0]
            for npc in speakers:
                names = [npc.key.lower()] + [
                    alias.lower() for alias in npc.aliases.all()
                ]
                if any(target in name for name in names):
                    return npc.db.deflection
        if len(speakers) == 1:
            return speakers[0].db.deflection
        return None

    def _fill(self, template):
        location = self.caller.location
        exits = self._exits()
        return template.format(
            room=location.key if location else "nowhere on record",
            exits=", ".join(exits) if exits else "not currently posted",
        )

    def func(self):
        caller = self.caller
        raw = (self.args or "").strip()
        words = raw.lower().split()
        if not words:
            return
        first = words[0]

        # `go <exit>` walks it if it exists; otherwise falls through to
        # the direction answer below.
        if first == "go" and len(words) > 1:
            target = words[1]
            for ex in caller.location.exits if caller.location else []:
                if target == ex.key.lower() or target in [
                    alias.lower() for alias in ex.aliases.all()
                ]:
                    caller.execute_cmd(ex.key)
                    return
            first = target

        if first in _DIRECTIONS:
            direction = _DIRECTIONS[first]
            caller.msg(
                self._fill(
                    f"Nothing leads {direction} from here. The Grid built "
                    "the ways it wanted: |w{exits}|n."
                )
            )
            return

        if first in _TALK_TRIGGERS:
            deflection = self._npc_deflection(words[1:])
            if deflection:
                caller.msg(deflection)
                return

        for triggers, answer in _INSTINCTS:
            if first in triggers:
                caller.msg(self._fill(answer))
                return

        reply = f"'{raw}' is not a permitted form."
        suggestions = string_suggestions(
            raw, _SUGGESTABLE, cutoff=0.7, maxnum=3
        )
        if suggestions:
            joined = ", ".join(f"|c{s}|n" for s in suggestions)
            reply += f" Perhaps: {joined}."
        else:
            reply += (
                " |=mThe permitted forms of assistance: |chelp|=m.|n"
            )
        caller.msg(reply)

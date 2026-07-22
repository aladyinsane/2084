"""
The map (v0.8): the parked feature, un-parked.

Built on the `ingame_map_display` contrib (the parking lot's default choice
— no coordinates, no migration; it derives everything from the room/exit
graph that ADR 0007 kept compass-consistent since v0.1).

The 2084 twist: each room renders as its |wvisibility digit|n, so the map is
not a convenience — it is a planning tool for staying dark. Routes become
legible as risk gradients. This is also why the map needs no gating: it
shows only what a resident of Sector 9 would know by heart, and it repeats
the honeypot's lie faithfully (the Bolt-Hole maps as 0, because the room
*says* 0 — the map is your knowledge, not the truth).

Exits you cannot traverse are not drawn past (the contrib checks traverse
access), so the Spire lobby simply isn't on your map until you hold C-1 —
the Grid above your clearance is rumor.
"""

from evennia.contrib.grid.ingame_map_display.ingame_map_display import (
    Map,
    CmdMap as ContribCmdMap,
)

from world.colors import VIS_COLORS as _VIS_COLORS


class GridMap(Map):
    """The contrib's mapper, rendering rooms as visibility digits."""

    def render_room(self, room, x, y, p1="[", p2="]", here=None):
        # The contrib signals up/down exits via `here` ("^" or "v") or, when
        # a room has both, via p1="^", p2="v". We keep the visibility digit
        # in the middle and move the shaft markers onto the brackets:
        # `[0^` has a way up, `v1]` a way down, `v1^` both.
        has_up = here == "^" or p1 == "^"
        has_down = here == "v" or p2 == "v"

        vis = getattr(room, "visibility", None)
        if room == self.caller.location:
            middle = "|g@|n"
        elif vis is None:
            middle = " "
        else:
            middle = f"{_VIS_COLORS.get(vis, '|w')}{vis}|n"

        left = "v" if has_down else "["
        right = "^" if has_up else "]"
        self.grid[x][y] = f"|=m{left}|n{middle}|=m{right}|n"


class CmdMap(ContribCmdMap):
    """
    Walk Sector 9 in your head.

    Usage:
      map [size]

    No map of Sector 9 is issued, sold, or acknowledged to exist. This is
    yours: the streets as you know them, each place marked with how watched
    it is (0 dark through 5 blinding — see |chelp visibility|n). |g@|n is
    you. |w[0^|n has a way up; |wv0]|n a way down. Places beyond your
    clearance are not on it, because as far as you are concerned they are
    not anywhere.
    """

    key = "map"
    locks = "cmd:all()"
    help_category = "sector 9"

    def func(self):
        from django.conf import settings as dj_settings

        size = getattr(dj_settings, "BASIC_MAP_SIZE", 3)
        max_size = getattr(dj_settings, "MAX_MAP_SIZE", 10)
        if self.args.isnumeric():
            size = min(max_size, int(self.args))

        map_here = GridMap(self.caller, size=size).show_map()
        self.caller.msg(
            (
                "You close your eyes and walk it: Sector 9, as much of it "
                "as is yours to know.\n\n"
                f"{map_here}\n"
                "|=mDigits are how watched each place is; low is dark. "
                "|g@|n|=m is you. ^ up, v down.|n",
                {"type": "map"},
            )
        )
        from world.onboarding import acknowledge_first_use

        acknowledge_first_use(self.caller, "map")

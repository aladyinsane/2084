"""
Gear verbs (v0.10): the MUD-conventional set — wear, remove, list, buy —
per the command-surface audit (ride expectations, don't mint).

Shops are NPCs tagged `vendor` (category "grid") carrying a `db.stock`
list of catalog keys. The broker's second shelf only exists for citizens
the underground already knows.
"""

from evennia import Command

from world import tuning

# The catalog: key -> (name, slot, gear_kind, desc, pitch)
CATALOG = {
    "badge": (
        "a laminated function badge",
        "wrist",
        "badge",
        "Your name, your function, your sector, and a photograph in which "
        "you look guilty of nothing yet. The lamination is Ministry-grade; "
        "the lanyard is grey.",
        "identifies you to every clerk (better pay at the counter) and to "
        "everything else (warmer in watched rooms)",
    ),
    "cuff": (
        "a wellness monitor",
        "wrist",
        "cuff",
        "A smooth grey cuff that counts your steps, your pulse, and — the "
        "leaflet does not mention this part — your whereabouts. It hums "
        "very slightly, like something content.",
        "the Ministry worries less about citizens it can hear (heat fades "
        "twice as fast; your movements log twice as easily)",
    ),
    "dampener": (
        "a coat with foil-lined seams",
        "coat",
        "dampener",
        "An ordinary worker's coat, heavier than it looks. The seams "
        "crinkle if you know what to listen for. Wearing it feels like "
        "being slightly further away from everything.",
        "watched rooms read you a little less (entry heat shaved); clerks "
        "distrust a coat like that (worse pay at the counter)",
    ),
    "pocket": (
        "a dead-man pocket",
        "pocket",
        "pocket",
        "A false pocket with a spring seam, sewn to give up its contents "
        "to gravity and take them back later. Single-use: once it has "
        "eaten one search, the seam is done.",
        "the next search that would find your cargo, doesn't (one use)",
    ),
}


def _vendors_here(room):
    if not room:
        return []
    return [
        obj for obj in room.contents if obj.tags.get("vendor", category="grid")
    ]


def _stock_for(vendor, caller):
    stock = list(vendor.db.stock or [])
    # The broker's shelf is only for people the underground knows.
    if vendor.db.stock_underground:
        if (caller.db.influence or {}).get(tuning.UNDERGROUND, 0) > 0:
            stock += list(vendor.db.stock_underground)
    return stock


class CmdList(Command):
    """
    See what's for sale, where selling happens.

    Usage:
      list

    The Grid's commerce is mostly queues, but a few counters and coats
    carry stock: state issue at the Assignment Hall, and other
    arrangements for citizens the right people know.
    """

    key = "list"
    aliases = ["wares", "browse"]
    locks = "cmd:all()"
    help_category = "the grid"

    def func(self):
        caller = self.caller
        vendors = _vendors_here(caller.location)
        if not vendors:
            caller.msg("Nobody here is selling anything, officially or otherwise.")
            return
        lines = []
        for vendor in vendors:
            stock = _stock_for(vendor, caller)
            if not stock:
                continue
            lines.append(f"|c{vendor.get_display_name(caller)}|n can provide:")
            for key in stock:
                name, slot, _, _, pitch = CATALOG[key]
                faction, price = tuning.GEAR_PRICES[key]
                lines.append(
                    f" - |w{name}|n (|c buy {key}|n) — {price} standing "
                    f"with {faction}, worn on the {slot}.\n"
                    f"   |=m{pitch}.|n"
                )
        caller.msg(
            "\n".join(lines)
            if lines
            else "Whatever is sold here, it is not sold to you yet."
        )


class CmdBuy(Command):
    """
    Buy from a vendor.

    Usage:
      buy <item>

    Prices are in standing — the only currency Sector 9 has ever printed.
    State issue goes in your file; the other kind goes in nobody's.
    """

    key = "buy"
    locks = "cmd:all()"
    help_category = "the grid"

    def func(self):
        from evennia import create_object

        from world import records

        caller = self.caller
        key = (self.args or "").strip().lower()
        vendors = _vendors_here(caller.location)
        vendor = next(
            (v for v in vendors if key in _stock_for(v, caller)), None
        )
        if not vendor or key not in CATALOG:
            caller.msg("Nobody here sells that. Possibly nobody anywhere does.")
            return
        name, slot, kind, desc, _ = CATALOG[key]
        faction, price = tuning.GEAR_PRICES[key]
        if any(g.db.gear_kind == kind for g in caller.contents):
            caller.msg("You already have one. Sector 9 is not a place of spares.")
            return
        if not caller.spend_influence(faction, price):
            caller.msg(
                f"The price is {price} standing with {faction}, and yours "
                "does not stretch. Standing is earned the way everything "
                "here is earned: visibly, or not at all."
            )
            return
        item = create_object("typeclasses.gear.Gear", key=name, location=caller)
        # The catalog key is the alias the buy message advertises ("wear
        # cuff") — playtest caught it missing.
        item.aliases.add(key)
        item.db.slot = slot
        item.db.gear_kind = kind
        item.db.desc = desc
        if faction != tuning.UNDERGROUND:
            records.add_record(
                caller,
                f"Issued: {name}",
                author="Ministry of Commerce",
                kind="observation",
            )
            caller.msg(
                f"{vendor.get_display_name(caller)} logs the issue, stamps "
                f"twice, and hands over {name}. The issue is, of course, "
                "recorded.\n|=mWear it with |cwear "
                f"{key}|n|=m.|n"
            )
        else:
            caller.msg(
                f"{name.capitalize()} changes hands inside a handshake. "
                "No ledger anywhere grows heavier.\n"
                f"|=mWear it with |cwear {key}|n|=m.|n"
            )


class CmdWear(Command):
    """
    Wear something you carry.

    Usage:
      wear <item>

    One item per place it's worn — a wrist has room for a badge or a
    cuff, not both. What you wear changes how the Grid reads you, in
    both directions.
    """

    key = "wear"
    locks = "cmd:all()"
    help_category = "the grid"

    def func(self):
        from typeclasses.gear import Gear, worn_gear

        caller = self.caller
        target = caller.search(
            (self.args or "").strip(), candidates=caller.contents
        )
        if not target:
            return
        if not isinstance(target, Gear):
            caller.msg(f"{target.key} is not something you wear.")
            return
        if target.db.worn:
            caller.msg("It is already on you.")
            return
        blocking = [
            g for g in worn_gear(caller) if g.db.slot == target.db.slot
        ]
        if blocking:
            caller.msg(
                f"Your {target.db.slot} is taken by {blocking[0].key}. "
                "Remove it first; layers are for people with nothing to "
                "choose."
            )
            return
        target.db.worn = True
        caller.msg(f"You put on {target.key}.")


class CmdRemoveGear(Command):
    """
    Take off something you wear.

    Usage:
      remove <item>
    """

    key = "remove"
    locks = "cmd:all()"
    help_category = "the grid"

    def func(self):
        from typeclasses.gear import worn_gear

        caller = self.caller
        target = caller.search(
            (self.args or "").strip(), candidates=worn_gear(caller)
        )
        if not target:
            return
        target.db.worn = False
        caller.msg(f"You take off {target.key}.")

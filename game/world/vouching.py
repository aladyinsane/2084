"""
Vouching (v0.22, ADR 0014; resource choice added ADR 0023): a small,
sanctioned stake on someone else's name.

Trust-machine backlog item 4 -- the gap circles and circle projects don't
fill: a citizen who isn't ready to form or join a circle yet still has no
trust-game participation at all. Vouching is that on-ramp. Unlike the
underground verbs, it needs no dead zone -- reachable in a new player's
first few minutes.

ADR 0023 let the voucher choose what they risk: Credits (spent now,
refunded on |cunvouch|n, lost outright on the backed citizen's Section C --
identical in shape to the original ADR 0014 mechanic, just renamed onto the
new spendable pool) or Standing with the Ministry of Records (nothing taken
now; only the confessor's Section C actually costs it, via
`Character.forfeit_standing` -- a real, permanent trust loss, the one
deliberate exception to "spending never demotes your grade"). Credits is
the default: the low-stakes, reachable-in-minutes option ADR 0014 was
built for.

State is plain `char.db` Attributes on both sides of the pair, not a
ServerConfig registry: vouching is strictly pairwise, never shared across a
group the way a circle is.
"""

import time

from world import tuning

VOUCH_FACTION = "Ministry of Records"


def current(char):
    """The voucher's own active vouch state, or None."""
    return char.db.vouch or None


def backers_of(char):
    """Every citizen currently backing `char`."""
    return list(char.db.vouched_by or [])


def vouch(voucher, target, resource="credits"):
    """
    Stake VOUCH_STAKE on `target`, in Credits or Standing (ADR 0023).
    Returns an error string, or None on success. One active vouch per
    voucher, same "one at a time" idiom as char.db.errand/the stash/circle
    projects.
    """
    if target is voucher:
        return "You are not in a position to vouch for yourself."
    if current(voucher):
        return (
            "You already have your name against someone else's. "
            "|cunvouch|n first, if you mean to move it."
        )
    if resource == "credits":
        if not voucher.spend_credits(tuning.VOUCH_STAKE):
            return (
                f"The price is {tuning.VOUCH_STAKE} credits, and you do "
                "not have it. A character reference costs something, or "
                "it would mean nothing."
            )
    else:
        # Nothing is taken now -- staking Standing only costs anything if
        # the backed citizen's own Section C forfeits it later.
        pass
    voucher.db.vouch = {
        "target": target,
        "resource": resource,
        "faction": VOUCH_FACTION,
        "amount": tuning.VOUCH_STAKE,
        "started": time.time(),
    }
    target.db.vouched_by = backers_of(target) + [voucher]
    return None


def unvouch(voucher):
    """
    Withdraw an active vouch. A credits stake is returned in full; a
    standing stake was never taken, so withdrawing is a pure no-op on the
    ledger. Error or None.
    """
    state = current(voucher)
    if not state:
        return "You have no one's name against yours to take back."
    target = state["target"]
    if state["resource"] == "credits":
        voucher.gain_credits(state["amount"])
    voucher.db.vouch = None
    target.db.vouched_by = [b for b in backers_of(target) if b is not voucher]
    return None


def forfeit_all(confessor):
    """
    A completed Section C confession costs every backer their stake --
    the confessor's own choice to name others, not what happens to them,
    is what forfeits it (being named in someone ELSE's confession does
    not trigger this). Called from circles.betray(). Returns the backers
    forfeited, for messaging.

    A credits stake was already spent at vouch time, so forfeiture there
    is silent (it just never comes back). A standing stake was never
    taken -- forfeiture is the one moment it actually costs the backer
    anything, a real Standing loss via `forfeit_standing` (ADR 0023).
    """
    backers = backers_of(confessor)
    for backer in backers:
        state = backer.db.vouch or {}
        if state.get("resource") == "standing":
            backer.forfeit_standing(
                state.get("faction", VOUCH_FACTION), state.get("amount", 0)
            )
        backer.db.vouch = None
    confessor.db.vouched_by = None
    return backers


def has_backers(char):
    """Does this citizen currently carry at least one active vouch?"""
    return bool(backers_of(char))

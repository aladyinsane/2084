"""
Vouching (v0.22, ADR 0014): a small, sanctioned stake on someone else's name.

Trust-machine backlog item 4 -- the gap circles and circle projects don't
fill: a citizen who isn't ready to form or join a circle yet still has no
trust-game participation at all. Vouching is that on-ramp. Unlike the
underground verbs, it costs *sanctioned* standing (Ministry of Records,
earned by `work`, the safest action in the game) and needs no dead zone --
reachable in a new player's first few minutes.

State is plain `char.db` Attributes on both sides of the pair, not a
ServerConfig registry: vouching is strictly pairwise, never shared across a
group the way a circle is.
"""

import time

from world import tuning


def current(char):
    """The voucher's own active vouch state, or None."""
    return char.db.vouch or None


def backers_of(char):
    """Every citizen currently backing `char`."""
    return list(char.db.vouched_by or [])


def vouch(voucher, target):
    """
    Stake VOUCH_STAKE Ministry of Records standing on `target`. Returns an
    error string, or None on success. One active vouch per voucher, same
    "one at a time" idiom as char.db.errand/the stash/circle projects.
    """
    if target is voucher:
        return "You are not in a position to vouch for yourself."
    if current(voucher):
        return (
            "You already have your name against someone else's. "
            "|cunvouch|n first, if you mean to move it."
        )
    if not voucher.spend_influence("Ministry of Records", tuning.VOUCH_STAKE):
        return (
            f"The price is {tuning.VOUCH_STAKE} standing with the Ministry "
            "of Records, and you do not have it. A character reference "
            "costs something, or it would mean nothing."
        )
    voucher.db.vouch = {
        "target": target,
        "amount": tuning.VOUCH_STAKE,
        "started": time.time(),
    }
    target.db.vouched_by = backers_of(target) + [voucher]
    return None


def unvouch(voucher):
    """Withdraw an active vouch, returning the stake in full. Error or None."""
    state = current(voucher)
    if not state:
        return "You have no one's name against yours to take back."
    target = state["target"]
    voucher.gain_influence("Ministry of Records", state["amount"])
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
    """
    backers = backers_of(confessor)
    for backer in backers:
        backer.db.vouch = None
    confessor.db.vouched_by = None
    return backers


def has_backers(char):
    """Does this citizen currently carry at least one active vouch?"""
    return bool(backers_of(char))

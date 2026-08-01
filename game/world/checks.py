"""
Opposed checks (ADR 0019): a shared, obstacle-driven resolution for
`observe`'s concealment gate, `forge`, and `sabotage`. Skill and obstacle
difficulty are both normalized to roughly the same 0-10 band on purpose, so
they balance against each other from one place instead of three independent
formulas.
"""

import random

from world import tuning


def _roll():
    return random.randint(1, tuning.CHECK_DIE_SIDES)


def opposed_check(actor, skill_name, obstacle_difficulty):
    """
    Both sides roll a die; the actor adds a skill modifier, the obstacle
    adds its difficulty directly. Ties favor the obstacle -- the world is
    the antagonist (principle 1), not a fair fight.
    """
    actor_total = _roll() + actor.skill(skill_name) // tuning.CHECK_SKILL_DIVISOR
    obstacle_total = _roll() + obstacle_difficulty
    return actor_total > obstacle_total

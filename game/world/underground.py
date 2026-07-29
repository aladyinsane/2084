"""
The underground economy (v0.6, ADR 0008): the grind loops and their ledger.

Sabotage and couriering both pay standing with "the underground" — the first
faction in the game that is not a Ministry, and the only one whose ledger the
Grid cannot read. Contraband parcels are real objects; seizure happens through
the surveillance systems that already exist (papers checks, detainment,
scanner gates) rather than through any courier-specific policing, because the
Watch does not know you are a courier. It only knows what it finds.
"""

import random
import time

from evennia import create_object
from evennia.utils import logger

from world import tuning

CONTRABAND_TAG = "contraband"
CONTRABAND_CATEGORY = "item"


# --- courier runs -----------------------------------------------------------


def current_job(char):
    """The tier key of the run this citizen is on, or None."""
    return char.db.courier_job or None


def carried_parcels(char):
    return [
        obj
        for obj in char.contents
        if obj.tags.get(CONTRABAND_TAG, category=CONTRABAND_CATEGORY)
    ]


def accept_job(char, tier):
    """Take a parcel from the broker. One run at a time."""
    spec = tuning.COURIER_JOBS.get(tier)
    if not spec:
        return None
    dest_key, pay, drop_desc = spec
    parcel = create_object(
        "typeclasses.objects.Object",
        key="a paper-wrapped parcel",
        aliases=["parcel", "package"],
        location=char,
    )
    parcel.tags.add(CONTRABAND_TAG, category=CONTRABAND_CATEGORY)
    parcel.db.desc = (
        "Brown paper, twine, no writing. It weighs exactly enough to be "
        "something. The wrapping has been done by someone who wraps a lot "
        "of parcels and has never once been asked what is in them."
    )
    char.db.courier_job = tier
    logger.log_info(f"watchlog: (unknown to the Watch) courier run '{tier}' by {char.key}")
    return dest_key, pay, drop_desc


def deliver(char):
    """
    Hand the parcel over at the destination. Returns (pay, jackpot) on
    success, or an error string.
    """
    tier = current_job(char)
    if not tier:
        return "You are not carrying for anyone. The queue knows who to ask."
    dest_key, pay, drop_desc = tuning.COURIER_JOBS[tier]
    if not char.location or char.location.key != dest_key:
        return (
            f"Not here. The drop is at {dest_key}: {drop_desc}. "
            "Parcels do not deliver themselves to more convenient rooms."
        )
    parcels = carried_parcels(char)
    if not parcels:
        return (
            "You reach for the parcel and find the absence of it. No parcel, "
            "no delivery, no pay. The queue will hear how this went."
        )
    for parcel in parcels:
        parcel.delete()
    char.db.courier_job = None
    jackpot = random.random() < tuning.COURIER_JACKPOT_CHANCE
    total = pay + (tuning.COURIER_JACKPOT_BONUS if jackpot else 0)
    char.gain_influence(tuning.UNDERGROUND, total)
    char.improve_skill("couriering")
    if char.db.errand:
        from world import errands

        errands.check(char, "deliver", tier=tier)
    from world import circle_projects, propaganda

    circle_projects.check(char, "deliver")
    propaganda.record("courier")
    return total, jackpot


def abandon_job(char):
    """Clear the run without pay (used after seizure)."""
    char.db.courier_job = None


def seize_contraband(char, found_by="an officer of the Watch"):
    """
    The run's death: whatever unregistered goods the citizen carries are
    found, taken, and written down. Called from papers checks, detainment,
    and scanner gates — the Watch doesn't hunt couriers; it just finds them.
    Returns True if anything was seized.
    """
    from world import records

    parcels = carried_parcels(char)
    if not parcels:
        return False
    # A dead-man pocket eats exactly one search (v0.10). The seam is
    # single-use; the incident never happens; the officer finds a pocket
    # containing pocket.
    from typeclasses.gear import worn_kind

    pocket = worn_kind(char, "pocket")
    if pocket:
        pocket.delete()
        char.msg(
            "|gGloved hands find the pocket, and the pocket, with one "
            "soft click of its seam, gives them its emptiness.|n The "
            "search moves on. Your cargo settles back against your ribs. "
            "The seam hangs slack now, spent."
        )
        logger.log_info(f"watchlog: dead-man pocket ate a search ({char.key})")
        return False
    for parcel in parcels:
        parcel.delete()
    abandon_job(char)
    records.add_record(
        char, "Found in possession of unregistered goods; goods confiscated"
    )
    char.msg(
        "|rGloved hands find the parcel on the second pat.|n It goes into an "
        "evidence bag with a receipt nobody offers you. Whatever it was, it "
        "is the Ministry's now, and so is the fact that you had it."
    )
    logger.log_info(f"watchlog: contraband seized from {char.key} ({found_by})")
    return True


# --- clean papers (the first sink) ------------------------------------------


def buy_papers(char):
    """Underground standing for exposure relief. Returns error string or None."""
    if not char.spend_influence(tuning.UNDERGROUND, tuning.PAPERS_COST):
        return (
            f"The price is {tuning.PAPERS_COST} standing with people who "
            "don't write ledgers down. Run more errands first."
        )
    char.gain_exposure(-tuning.PAPERS_RELIEF)
    return None


# --- sabotage ---------------------------------------------------------------


def sabotage_targets(room, skill_concealed):
    """Live devices in the room this citizen is able to find."""
    return [
        obj
        for obj in room.contents
        if hasattr(obj, "sensitivity")
        and not obj.destination
        and obj.db.active
        and (not obj.db.concealed or skill_concealed >= tuning.OBSERVE_TIER_CONCEALED)
    ]


def do_sabotage(char, sensor):
    """
    One attempt on one live device. Returns (success, room_dark, pay).
    Failure writes the incident and the heat itself.
    """
    from world import records

    skill = char.skill("sabotage")
    chance = tuning.SABOTAGE_BASE_CHANCE + skill * tuning.SABOTAGE_SKILL_BONUS
    char.improve_skill("sabotage")
    if random.random() >= chance:
        records.add_record(
            char, "Suspected interference with municipal equipment"
        )
        char.gain_exposure(tuning.SABOTAGE_FAIL_EXPOSURE)
        logger.log_info(
            f"watchlog: sabotage FAILED by {char.key} on {sensor.key}"
        )
        return False, False, 0

    sensor.db.active = False
    sensor.db.sabotaged_at = time.time()
    room = char.location
    room_dark = room is not None and room.exposure_gain() == 0
    pay = tuning.SABOTAGE_INFLUENCE + (
        tuning.SABOTAGE_DARK_BONUS if room_dark else 0
    )
    char.gain_influence(tuning.UNDERGROUND, pay)
    logger.log_info(
        f"watchlog: (unknown to the Watch) {sensor.key} sabotaged by "
        f"{char.key}{' — room dark' if room_dark else ''}"
    )
    return True, room_dark, pay


def oldest_sabotaged_sensor():
    """The maintenance crew works the backlog oldest-first."""
    from typeclasses.objects import Sensor

    broken = [
        s for s in Sensor.objects.all() if s.db.sabotaged_at and not s.db.active
    ]
    broken.sort(key=lambda s: s.db.sabotaged_at)
    return broken[0] if broken else None


# --- the shadow ladder (ADR 0009) --------------------------------------------


def shadow_standing(char):
    """
    (standing, current tier, next tier, standing needed for it) — or
    (standing, tier, None, None) at the top tier. Pure function of
    `db.influence`, same shape as `grades.next_review`; nothing here is
    stored or cached, and none of it touches the sanctioned ledger.
    """
    standing = (char.db.influence or {}).get(tuning.UNDERGROUND, 0)
    thresholds = sorted(tuning.SHADOW_TIERS)
    current = thresholds[0]
    for threshold in thresholds:
        if standing >= threshold:
            current = threshold
        else:
            return standing, tuning.SHADOW_TIERS[current], tuning.SHADOW_TIERS[threshold], threshold
    return standing, tuning.SHADOW_TIERS[current], None, None

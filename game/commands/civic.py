"""
Civic verbs: the v0.3 skill-by-use loops (ADR 0002/0003) and the two routes —
sanctioned and not — to a cleaner file (ADR 0005).

work     — clerking, paid in standing with the Ministry of Records
observe  — read the apparatus back; skill sharpens what you see
listen   — the ration queue knows things (asynchronous traces, principle 8)
petition — the lawful way to edit your file: costly, polite, noticed
forge    — the other way: free, dangerous, and only where nothing watches
"""

import random
import time

from evennia import Command

from world import tuning


def _room_tagged(room, tag):
    return bool(room and room.tags.get(tag, category="grid"))


def _compactable_type_by_label(token):
    """ADR 0011 §5: the keyword a player types to target a summarized
    routine-incident type in petition/forge, since it has no number."""
    token = token.strip().lower()
    for type_key, spec in tuning.COMPACTABLE_INCIDENT_TYPES.items():
        if spec["label"] == token:
            return type_key
    return None


# ADR 0022: land/water records are a second kind of thing petition/forge can
# target, addressed by keyword the same way a compacted routine-incident type
# already is -- reusing that idiom rather than inventing a second syntax.
LAND_RECORD_KINDS = ("survey", "allotment")


def _owned_parcel(caller, kind):
    """The Parcel of the given kind whose db.owner is caller, if any (ADR
    0022's actor/subject split: standing over the land, not over yourself)."""
    from typeclasses.land import Parcel

    for parcel in Parcel.objects.all():
        if parcel.db.parcel_kind == kind and parcel.db.owner is caller:
            return parcel
    return None


class CmdReport(Command):
    """
    Report to the Assignment Hall counter for your function.

    Usage:
      report

    The Grid does not ask what you would like to be. It reads your file:
    your recorded aptitudes are your application, whether or not you meant
    them as one, and stamps a function on you. Citizens with a function
    work their own post for better standing. Functions can be reassigned by
    reporting again, and are suspended by, for example, being detained.
    """

    key = "report"
    locks = "cmd:all()"
    help_category = "sector 9"

    def func(self):
        from world import functions, records

        caller = self.caller
        if not _room_tagged(caller.location, "workplace"):
            caller.msg(
                "Functions are assigned at the Assignment Hall counter, "
                "which is where the name comes from."
            )
            return
        old_key, _ = functions.current_function(caller)
        key, spec = functions.assign_function(caller)
        records.add_record(
            caller,
            f"Assigned function: {spec['title']}",
            author="Ministry of Order",
            kind="observation",
        )
        if key == old_key:
            caller.msg(
                "The clerk consults your file, consults a rubric, and "
                f"stamps: |w{spec['title']}|n, your existing designation. "
                "The stamp comes down anyway. Stamps are not for you; they "
                "are for the file."
            )
        else:
            caller.msg(
                "The clerk reads your file with the expression of someone "
                "weighing produce, selects a stamp, and brings it down.\n"
                f"|wFUNCTION: {spec['title'].upper()}|n\n"
                f"Your post is {spec['workplace_desc']}; report there and "
                "|cwork|n. The Grid thanks you in advance, in writing, "
                "in triplicate."
            )
        from world.onboarding import acknowledge_first_use

        acknowledge_first_use(caller, "report")

        # Round-two playtest finding 4: `db.oriented` was only ever set by
        # walking the Demonstration Corridor, so a citizen who deliberately
        # skipped the Wing stayed on the beginner-abridged `help` card
        # forever, contradicting CmdHelpStaged's own "nothing is ever
        # locked" promise. Taking a function is the other unambiguous
        # "I'm playing for real now" milestone, so it earns the same flag.
        caller.db.oriented = True


class CmdWork(Command):
    """
    Work.

    Usage:
      work

    With a function: work your assigned post, for standing with your
    ministry. Without one: casual clerical labor is accepted at the
    Assignment Hall counter, at casual rates. Either way, nothing reassures
    the Grid like visible usefulness: working takes a little heat off you.
    """

    key = "work"
    locks = "cmd:all()"
    help_category = "sector 9"

    CASUAL_SHIFTS = [
        "You stamp permits until the stamp needs re-inking. Form 12-C, "
        "approved. Form 12-C, approved. Form 12-C, a hesitation, approved.",
        "You alphabetize a drawer of citizens. Two of the folders are empty "
        "with the names scratched out. You file them under the scratches.",
        "You transcribe a ledger of ration allocations. The arithmetic is "
        "wrong in the Ministry's favor; you transcribe it faithfully.",
        "You countersign forms already countersigned by someone whose "
        "signature is a printed facsimile of a signature.",
    ]

    # Off-cooldown texture (playtest finding, never triaged until now: the
    # dead seconds between shifts had one static line and no sense of when
    # the next one opens). Same idiom as the sweep's near-miss telegraphy
    # (scripts.py's NEAR_MISSES) -- proximity read through prose tiers, not
    # a raw countdown; nothing in this codebase shows a player a literal
    # number of seconds to wait, and a digital countdown would be the first.
    OFF_COOLDOWN_FAR = [
        "You are waved off before you have finished offering. Eagerness "
        "is also noted.",
        "\"Already been,\" the counter says, without checking. It has "
        "not, quite. It will not be argued with.",
    ]
    OFF_COOLDOWN_NEAR = [
        "You are waved off, but the pen is already reaching for a fresh "
        "form. Not yet. Nearly.",
        "\"Give it a moment,\" the counter says, not unkindly, already "
        "turning the next form face-up.",
    ]

    def func(self):
        from world import functions

        caller = self.caller
        key, spec = functions.current_function(caller)

        if key:
            if not spec["works_here"](caller.location):
                caller.msg(
                    f"Your function is {spec['title']}; your post is "
                    f"{spec['workplace_desc']}. Work performed elsewhere "
                    "is not work, administratively speaking."
                )
                return
            shifts = spec["shifts"]
            faction = spec["faction"]
            pay = tuning.FUNCTION_WORK_INFLUENCE
            skill_name = spec["skill"]
        else:
            if not _room_tagged(caller.location, "workplace"):
                caller.msg(
                    "No one here will pay for your usefulness. Casual labor "
                    "is taken at the Assignment Hall counter, or |creport|n "
                    "there to be assigned a function of your own."
                )
                return
            shifts = self.CASUAL_SHIFTS
            faction = "Ministry of Records"
            pay = tuning.WORK_INFLUENCE
            skill_name = "clerking"

        now = time.time()
        elapsed = now - (caller.db.last_work or 0)
        if elapsed < tuning.WORK_COOLDOWN:
            near = elapsed >= tuning.WORK_COOLDOWN * tuning.WORK_NEAR_COOLDOWN_FRACTION
            lines = self.OFF_COOLDOWN_NEAR if near else self.OFF_COOLDOWN_FAR
            caller.msg(random.choice(lines))
            return
        caller.db.last_work = now
        caller.msg(random.choice(shifts))
        skill = caller.improve_skill(skill_name)
        # What you wear changes what the counter pays (v0.10): a badge
        # legitimizes; a foil-lined coat gets looked at twice.
        from typeclasses.gear import worn_kind

        if worn_kind(caller, "badge"):
            pay += tuning.BADGE_WORK_BONUS
        if worn_kind(caller, "dampener"):
            pay = max(1, pay - tuning.DAMPENER_WORK_PENALTY)
        total = caller.gain_influence(faction, pay)
        caller.gain_exposure(-tuning.WORK_EXPOSURE_RELIEF)
        caller.msg(
            f"|=m{skill_name.capitalize()} {skill}. Standing with the "
            f"{faction} {total}. Visible usefulness is its own kind of "
            "cover.|n"
        )
        caller.send_prompt()
        if caller.db.errand:
            from world import errands

            errands.check(caller, "shift")
        from world.onboarding import acknowledge_first_use

        acknowledge_first_use(caller, "work")


class CmdObserve(Command):
    """
    Study the room the way the room studies you.

    Usage:
      observe

    Counting the cameras is a skill. It improves the way any skill improves.
    """

    key = "observe"
    locks = "cmd:all()"
    help_category = "sector 9"

    def func(self):
        caller = self.caller
        room = caller.location
        if not room:
            return
        from world import checks

        skill = caller.skill("observation")
        sensors = [
            obj
            for obj in room.contents
            if hasattr(obj, "sensitivity") and not obj.destination
            and hasattr(obj, "db") and obj.db.active is not None
            # Concealed devices (v0.5) roll an opposed check against their
            # own concealment (ADR 0019) -- never a guarantee, even at skill
            # cap, which is what makes a honeypot a honeypot.
            and (
                not obj.db.concealment
                or checks.opposed_check(caller, "observation", obj.db.concealment)
            )
        ]
        vis = getattr(room, "visibility", 0)

        lines = [
            f"You take the room in slowly, the way you'd read a form. "
            f"Ambient visibility here feels like a {vis} out of 5."
        ]
        if not sensors:
            lines.append(
                "You find no fixed devices at all. Either nothing watches "
                "here, or what watches doesn't need fixtures."
            )
        elif skill < tuning.OBSERVE_TIER_STATUS:
            lines.append(
                f"You count {len(sensors)} fixed device"
                f"{'s' if len(sensors) != 1 else ''}. You are not confident "
                "you counted all of them, and you can't tell which are live."
            )
        else:
            for sensor in sensors:
                status = "|glive|n" if sensor.db.active else "|rdead|n"
                hidden = "|r(concealed)|n " if sensor.db.concealment else ""
                if skill >= tuning.OBSERVE_TIER_DETAIL and sensor.db.active:
                    lines.append(
                        f" - {hidden}{sensor.key}: {status}, sharpness "
                        f"{sensor.db.sensitivity}"
                    )
                else:
                    lines.append(f" - {hidden}{sensor.key}: {status}")
        caller.msg("\n".join(lines))
        new_skill = caller.improve_skill("observation")
        if new_skill in (tuning.OBSERVE_TIER_STATUS, tuning.OBSERVE_TIER_DETAIL):
            caller.msg(
                "|=mSomething settles in the way you look at rooms. You will "
                "see more from now on.|n"
            )
        if caller.db.errand:
            from world import errands

            errands.check(caller, "observe", room=room)
        from world.onboarding import acknowledge_first_use

        acknowledge_first_use(caller, "observe")


class CmdListen(Command):
    """
    Listen to the queue.

    Usage:
      listen

    Gossip travels down the ration line faster than the line itself, and more
    reliably than the newsfeeds. Names come up. Yours might, someday.
    """

    key = "listen"
    locks = "cmd:all()"
    help_category = "sector 9"

    def func(self):
        from world import records

        caller = self.caller
        if not _room_tagged(caller.location, "gossip_spot"):
            caller.msg(
                "Nobody here is saying anything worth overhearing. The "
                "ration queue is where Sector 9 talks."
            )
            return
        incidents = records.recent_incidents(
            exclude_subject=caller, limit=tuning.GOSSIP_LIMIT
        )
        if not incidents:
            caller.msg(
                "The line shuffles forward. Weather, rations, the smell of "
                "the recyclers, nothing with a name in it today."
            )
            return
        lines = ["You let the queue's murmur wash over you, and pick out:"]
        for rec in incidents:
            subject = rec.db.subject.key if rec.db.subject else "someone"
            lines.append(
                f' - "…{subject}, they say. {rec.db.content.rstrip(".")}. '
                'Anyway. Keep your head down…"'
            )
        caller.msg("\n".join(lines))

        from world.onboarding import acknowledge_first_use

        acknowledge_first_use(caller, "listen")


class CmdPetition(Command):
    """
    Petition the Records Annex about your file.

    Usage:
      petition amend <entry> = <corrected text>
      petition redact <entry>
      petition redact <routine-incident keyword>
      petition amend survey = <corrected text>
      petition redact allotment

    Entry numbers are as shown in your dossier. Routine incidents old enough
    to have folded into a lifetime count (ADR 0011) have no number anymore:
    redact those by the keyword shown next to them instead, one off the
    count per petition. A landholder's survey or water allotment (ADR 0022)
    petitions the same way, by the keyword |wsurvey|n or |wallotment|n, and
    only for land actually held. Amendments and redactions are services of
    the Ministry of Records, payable in standing with the Ministry of
    Records, which is the sort of arrangement the Ministry finds elegant.
    The request itself is, of course, noted.
    """

    key = "petition"
    locks = "cmd:all()"
    help_category = "sector 9"

    def _archivist(self):
        room = self.caller.location
        if not room:
            return None
        for obj in room.contents:
            if obj.tags.get("records_service", category="grid"):
                return obj
        return None

    def func(self):
        from world import records

        caller = self.caller
        archivist = self._archivist()
        if not archivist:
            caller.msg(
                "File petitions are heard at the Archive Annex, by the "
                "archivist, during such hours as the archivist exists."
            )
            return

        args = (self.args or "").strip()
        action, _, rest = args.partition(" ")
        action = action.lower()
        if action not in ("amend", "redact"):
            caller.msg("Usage: petition amend <entry> = <text>, or petition redact <entry>.")
            return

        if action == "amend":
            num_part, sep, new_text = rest.partition("=")
            new_text = new_text.strip()
            if not sep or not new_text:
                caller.msg("Usage: petition amend <entry> = <corrected text>")
                return
        else:
            num_part = rest

        type_key = _compactable_type_by_label(num_part)
        if type_key:
            if action == "amend":
                caller.msg(
                    f"{archivist.key} looks at you as if you'd asked to "
                    "rewrite a tally mark. \"There is no single entry there "
                    'to correct. You may petition it redacted, one at a '
                    'time, or not at all."'
                )
                return
            spec = tuning.COMPACTABLE_INCIDENT_TYPES[type_key]
            if not caller.spend_influence("Ministry of Records", tuning.REDACT_COST):
                caller.msg(
                    f'{archivist.key} names the consideration: '
                    f"{tuning.REDACT_COST} standing with the Ministry of "
                    "Records. You do not have it. The file closes with a "
                    "sound like a small door."
                )
                return
            if not records.redact_summary(caller, type_key):
                caller.msg(
                    f'{archivist.key} checks the tally. "There is nothing '
                    f'left to strike from {spec["label"]}."'
                )
                return
            caller.msg(
                f"{archivist.key} produces a stamp, and the tally for "
                f'"{spec["display"]}" reads one lower. The old total, the '
                "archivist remarks, is nobody's business."
            )
            caller.gain_exposure(tuning.SERVICE_EXPOSURE)
            caller.msg(
                "|=mRequests of this kind are themselves noted. You feel "
                "the note being made.|n"
            )
            caller.send_prompt()
            return

        land_kind = num_part.strip().lower()
        if land_kind in LAND_RECORD_KINDS:
            parcel = _owned_parcel(caller, land_kind)
            if not parcel:
                caller.msg(
                    f'{archivist.key} checks a ledger you don\'t appear in. '
                    f'"Nothing of that kind is filed to your name."'
                )
                return
            if action == "amend" and not new_text:
                caller.msg(f"Usage: petition amend {land_kind} = <corrected text>")
                return
            open_records = [
                rec
                for rec in records.records_for(parcel, kind=land_kind)
                if not rec.db.redacted
            ]
            if not open_records:
                caller.msg(
                    f'{archivist.key} finds nothing of that kind still on '
                    "file."
                )
                return
            record = open_records[-1]
            cost = tuning.AMEND_COST if action == "amend" else tuning.REDACT_COST
            if not caller.spend_influence("Ministry of Records", cost):
                caller.msg(
                    f'{archivist.key} names the consideration: {cost} '
                    "standing with the Ministry of Records. You do not "
                    "have it. The file closes with a sound like a small "
                    "door."
                )
                return
            if action == "amend":
                records.amend(record, new_text, actor=caller, authorized=True)
                caller.msg(
                    f"{archivist.key} unscrews a pen with terrible ceremony "
                    f"and makes the correction. The {land_kind} now reads "
                    "as it has, of course, always read."
                )
            else:
                records.redact(record, actor=caller, authorized=True)
                caller.msg(
                    f"{archivist.key} produces a stamp, and the {land_kind} "
                    "ceases to have been. The ledger, the archivist "
                    "remarks, is nobody's business."
                )
            caller.gain_exposure(tuning.SERVICE_EXPOSURE)
            caller.msg(
                "|=mRequests of this kind are themselves noted. You feel "
                "the note being made.|n"
            )
            caller.send_prompt()
            return

        try:
            number = int(num_part.strip())
        except ValueError:
            caller.msg(
                "Which entry? Use the number from your dossier, or a "
                "routine-incident keyword shown there."
            )
            return

        record = records.incident_by_number(caller, number)
        if not record or record.db.redacted:
            caller.msg(
                f'{archivist.key} runs a finger down your file. "There is no '
                f'entry {number}." The finger stops. "There is no entry '
                f'{number}."'
            )
            return

        cost = tuning.AMEND_COST if action == "amend" else tuning.REDACT_COST
        if not caller.spend_influence("Ministry of Records", cost):
            caller.msg(
                f'{archivist.key} names the consideration: {cost} standing '
                "with the Ministry of Records. You do not have it. The file "
                "closes with a sound like a small door."
            )
            return

        if action == "amend":
            records.amend(record, new_text, actor=caller, authorized=True)
            caller.msg(
                f'{archivist.key} unscrews a pen with terrible ceremony and '
                f"makes the correction. Entry {number} now reads as it has, "
                "of course, always read."
            )
        else:
            records.redact(record, actor=caller, authorized=True)
            caller.msg(
                f"{archivist.key} produces a stamp, and entry {number} "
                "ceases to have been. The numbering, the archivist remarks, "
                "is nobody's business."
            )
        caller.gain_exposure(tuning.SERVICE_EXPOSURE)
        caller.msg(
            "|=mRequests of this kind are themselves noted. You feel the "
            "note being made.|n"
        )
        caller.send_prompt()

        from world.onboarding import acknowledge_first_use

        acknowledge_first_use(caller, "petition")


class CmdResearch(Command):
    """
    Research the archive.

    Usage:
      research

    The Annex's public terminals hold decades of what the Ministry decided
    was worth keeping. Most of it is exactly as dull as it looks, and the
    archivist logs who reads what. Sometimes a page doesn't belong.
    """

    key = "research"
    locks = "cmd:all()"
    help_category = "sector 9"

    FAR_LINES = [
        "The terminal is still loading the last thing you asked it. "
        "Patience is a filing skill.",
        '"One record at a time," the archivist says, not looking up.',
    ]
    NEAR_LINES = [
        "The terminal's cursor blinks, nearly ready to be asked again.",
        "The archivist checks the clock, then you, then the clock again.",
    ]

    def _archivist(self):
        room = self.caller.location
        if not room:
            return None
        for obj in room.contents:
            if obj.tags.get("records_service", category="grid"):
                return obj
        return None

    def func(self):
        from world import archaeology

        caller = self.caller
        if not self._archivist():
            caller.msg(
                "The archive is consulted at the Archive Annex, under the "
                "archivist's eye, or not at all."
            )
            return

        now = time.time()
        elapsed = now - (caller.db.last_research or 0)
        if elapsed < tuning.RESEARCH_COOLDOWN:
            near = (
                elapsed
                >= tuning.RESEARCH_COOLDOWN * tuning.WORK_NEAR_COOLDOWN_FRACTION
            )
            lines = self.NEAR_LINES if near else self.FAR_LINES
            caller.msg(random.choice(lines))
            return
        caller.db.last_research = now
        archaeology.research(caller)

        from world.onboarding import acknowledge_first_use

        acknowledge_first_use(caller, "research")


class CmdForge(Command):
    """
    Rewrite an entry in your file without asking anyone.

    Usage:
      forge <entry> = <new text>
      forge <routine-incident keyword>
      forge survey = <new text>
      forge allotment = <new text>

    Possible only somewhere nothing watches at all. Done well, the file
    simply says something else now. Done badly, the file gains a page. A
    routine incident old enough to have folded into a lifetime count (ADR
    0011) has no text left to rewrite: forging it just tries to strike one
    off the tally instead, same success chance, same risk of getting caught.
    A landholder can forge their own survey or water allotment (ADR 0022)
    the same way, standing on the land itself, in a place nothing watches.
    """

    key = "forge"
    locks = "cmd:all()"
    help_category = "the underground"

    def func(self):
        from world import checks, records, watch

        caller = self.caller
        room = caller.location
        # is_dead_zone is the single source of truth on "truly unwatched"
        # (v0.5): a hidden live device makes this refuse — which is the one
        # honest tell a honeypot gives you.
        if not room or not getattr(room, "is_dead_zone", lambda: False)():
            caller.msg(
                "Not here. Whatever you're considering, it wants a place "
                "with no eyes in it at all."
            )
            return

        args = (self.args or "").strip()
        num_part, sep, new_text = args.partition("=")
        new_text = new_text.strip()

        type_key = _compactable_type_by_label(num_part)
        if type_key:
            spec = tuning.COMPACTABLE_INCIDENT_TYPES[type_key]
            caller.improve_skill("forgery")
            difficulty = tuning.FORGE_BASE_DIFFICULTY + (
                caller.db.exposure or 0
            ) // tuning.FORGE_EXPOSURE_DIFFICULTY_DIVISOR
            if checks.opposed_check(caller, "forgery", difficulty):
                if records.redact_summary(caller, type_key):
                    caller.msg(
                        "Chalk, patience, and a borrowed terminal jacked "
                        "into a dead junction box. The tally for "
                        f'"{spec["display"]}" reads one lower now, and '
                        "nothing else changed."
                    )
                else:
                    caller.msg(
                        f'There is nothing left on the {spec["label"]} '
                        "tally to strike."
                    )
            else:
                watch.add_record_note(
                    caller,
                    "Suspected document tampering; forensic review pending",
                )
                caller.gain_exposure(tuning.FORGE_FAIL_EXPOSURE)
                caller.msg(
                    "|rSomething upstream notices the edit and un-happens "
                    "it.|n The terminal goes politely dead in your hands. "
                    "Somewhere, a form about you begins to fill itself in."
                )
                caller.send_prompt()
            return

        land_kind = num_part.strip().lower()
        if land_kind in LAND_RECORD_KINDS:
            parcel = _owned_parcel(caller, land_kind)
            if not parcel:
                caller.msg("Nothing here is yours to rewrite.")
                return
            if not sep or not new_text:
                caller.msg(f"Usage: forge {land_kind} = <new text>")
                return
            open_records = [
                rec
                for rec in records.records_for(parcel, kind=land_kind)
                if not rec.db.redacted
            ]
            if not open_records:
                caller.msg("There is no such record on file here to rewrite.")
                return
            record = open_records[-1]
            caller.improve_skill("forgery")
            difficulty = tuning.FORGE_BASE_DIFFICULTY + (
                caller.db.exposure or 0
            ) // tuning.FORGE_EXPOSURE_DIFFICULTY_DIVISOR
            if checks.opposed_check(caller, "forgery", difficulty):
                records.amend(record, new_text, actor=caller, authorized=False)
                caller.msg(
                    "A borrowed pen and a number nobody out here checks "
                    f"twice. The {land_kind} reads differently now, and "
                    "nothing else changed."
                )
            else:
                watch.add_record_note(
                    caller,
                    "Suspected document tampering; forensic review pending",
                )
                caller.gain_exposure(tuning.FORGE_FAIL_EXPOSURE)
                caller.msg(
                    "|rSomewhere, a surveyor's tally stops matching the "
                    "land.|n The correction doesn't take. A form about you "
                    "begins to fill itself in."
                )
                caller.send_prompt()
            return

        try:
            number = int(num_part.strip())
        except ValueError:
            caller.msg("Usage: forge <entry> = <new text>")
            return
        if not sep or not new_text:
            caller.msg("Usage: forge <entry> = <new text>")
            return

        record = records.incident_by_number(caller, number)
        if not record or record.db.redacted:
            caller.msg("Your file has no such entry to improve.")
            return

        caller.improve_skill("forgery")
        difficulty = tuning.FORGE_BASE_DIFFICULTY + (
            caller.db.exposure or 0
        ) // tuning.FORGE_EXPOSURE_DIFFICULTY_DIVISOR
        if checks.opposed_check(caller, "forgery", difficulty):
            records.amend(record, new_text, actor=caller, authorized=False)
            caller.msg(
                "Chalk, patience, and a borrowed terminal jacked into a dead "
                "junction box. The Records net accepts the correction "
                "without appetite or suspicion, the way it accepts "
                f"everything.\n|=mEntry {number} now reads: {new_text}|n"
            )
        else:
            watch.add_record_note(
                caller,
                "Suspected document tampering; forensic review pending",
            )
            caller.gain_exposure(tuning.FORGE_FAIL_EXPOSURE)
            caller.msg(
                "|rSomething upstream notices the edit and un-happens it.|n "
                "The terminal goes politely dead in your hands. Somewhere, "
                "a form about you begins to fill itself in."
            )
            caller.send_prompt()


class CmdApply(Command):
    """
    Apply for elevated clearance (Form C-1, then Form C-2).

    Usage:
      apply

    Heard at the Archive Annex, where the archivist keeps the forms. The
    Ministry always hears the next form you're eligible for: Grade C-1
    admits you to the Central Spire lobby; Grade C-2, filed the same way
    once C-1 is held, admits you past it. The Ministry will read your file,
    your function, and your ledger, in that order, and only the versions
    of them it has.
    """

    key = "apply"
    locks = "cmd:all()"
    help_category = "sector 9"

    def func(self):
        from evennia.utils.evmenu import EvMenu

        caller = self.caller
        room = caller.location
        has_archivist = room and any(
            obj.tags.get("records_service", category="grid")
            for obj in room.contents
        )
        if not has_archivist:
            caller.msg(
                "Applications are heard at the Archive Annex, by the "
                "archivist, who keeps the forms and the opinions about them."
            )
            return

        from world.functions import clearance_level

        # ADR 0021: the same command routes to whichever form is next --
        # C-1 for the unelevated, C-2 for C-1 holders. Nothing past C-2
        # exists yet (only floor C-2 is built), so C-2-and-above get turned
        # away rather than routed to a form that isn't there.
        level = clearance_level(caller)
        if level >= 2:
            caller.msg(
                "The archivist checks a drawer that, for you, is currently "
                "empty. \"Nothing further is being taken at this time,\" "
                "they say, without elaborating on whether that's a policy "
                "or a prediction."
            )
            return

        menu_module = "world.form_c2" if level == 1 else "world.form_c1"
        EvMenu(
            caller,
            menu_module,
            startnode="node_start",
            cmd_on_exit=None,
        )

        from world.onboarding import acknowledge_first_use

        acknowledge_first_use(caller, "apply")


def _citizen_here(caller, name):
    from typeclasses.characters import Character

    target = caller.search(name, quiet=True)
    target = target[0] if target else None
    if not target or target is caller or not isinstance(target, Character):
        return None
    return target


class CmdVouch(Command):
    """
    Stake a little of your standing on someone else's name.

    Usage:
      vouch <citizen>

    A character reference, and nothing more official than that: no form,
    no dead zone, no consent required of the one you name. It costs a
    little Ministry of Records standing, returned to you in full if you
    change your mind (|cunvouch|n) or take back if the citizen you named
    ever completes Section C themselves. One name against yours at a time.
    """

    key = "vouch"
    locks = "cmd:all()"
    help_category = "sector 9"

    def func(self):
        from world import vouching

        caller = self.caller
        name = (self.args or "").strip()
        if not name:
            caller.msg("Usage: vouch <citizen>")
            return
        target = _citizen_here(caller, name)
        if not target:
            caller.msg("Nobody here answers to that, worth the risk or not.")
            return
        err = vouching.vouch(caller, target)
        if err:
            caller.msg(err)
            return
        caller.msg(
            f"You put your name behind {target.key}'s, quietly, where the "
            "Ministry can read it if it ever looks. |=mIf they ever "
            "complete Section C, your word goes with theirs.|n"
        )

        from world.onboarding import acknowledge_first_use

        acknowledge_first_use(caller, "vouch")


class CmdUnvouch(Command):
    """
    Take your name back.

    Usage:
      unvouch

    Withdraws your active vouch and returns the standing you staked, in
    full, no penalty. Whatever you told them, or didn't, that's between
    you.
    """

    key = "unvouch"
    locks = "cmd:all()"
    help_category = "sector 9"

    def func(self):
        from world import vouching

        caller = self.caller
        err = vouching.unvouch(caller)
        if err:
            caller.msg(err)
            return
        caller.msg("You take your name back. Nothing was ever written down.")

        from world.onboarding import acknowledge_first_use

        acknowledge_first_use(caller, "unvouch")

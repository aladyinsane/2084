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


class CmdReport(Command):
    """
    Report to the Assignment Hall counter for your function.

    Usage:
      report

    The Grid does not ask what you would like to be. It reads your file —
    your recorded aptitudes are your application, whether or not you meant
    them as one — and stamps a function on you. Citizens with a function
    work their own post for better standing. Functions can be reassigned by
    reporting again, and are suspended by, for example, being detained.
    """

    key = "report"
    locks = "cmd:all()"
    help_category = "the grid"

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
                f"stamps: |w{spec['title']}|n — your existing designation. "
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


class CmdWork(Command):
    """
    Work.

    Usage:
      work

    With a function: work your assigned post, for standing with your
    ministry. Without one: casual clerical labor is accepted at the
    Assignment Hall counter, at casual rates. Either way, nothing reassures
    the Grid like visible usefulness — working takes a little heat off you.
    """

    key = "work"
    locks = "cmd:all()"
    help_category = "the grid"

    CASUAL_SHIFTS = [
        "You stamp permits until the stamp needs re-inking. Form 12-C, "
        "approved. Form 12-C, approved. Form 12-C — a hesitation — approved.",
        "You alphabetize a drawer of citizens. Two of the folders are empty "
        "with the names scratched out. You file them under the scratches.",
        "You transcribe a ledger of ration allocations. The arithmetic is "
        "wrong in the Ministry's favor; you transcribe it faithfully.",
        "You countersign forms already countersigned by someone whose "
        "signature is a printed facsimile of a signature.",
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
                    "is taken at the Assignment Hall counter — or |creport|n "
                    "there to be assigned a function of your own."
                )
                return
            shifts = self.CASUAL_SHIFTS
            faction = "Ministry of Records"
            pay = tuning.WORK_INFLUENCE
            skill_name = "clerking"

        now = time.time()
        if now - (caller.db.last_work or 0) < tuning.WORK_COOLDOWN:
            caller.msg(
                "You are waved off without a glance: the next shift isn't "
                "yours yet. Eagerness is also noted."
            )
            return
        caller.db.last_work = now
        caller.msg(random.choice(shifts))
        skill = caller.improve_skill(skill_name)
        total = caller.gain_influence(faction, pay)
        caller.gain_exposure(-tuning.WORK_EXPOSURE_RELIEF)
        caller.msg(
            f"|=m{skill_name.capitalize()} {skill}. Standing with the "
            f"{faction} {total}. Visible usefulness is its own kind of "
            "cover.|n"
        )
        caller.send_prompt()


class CmdObserve(Command):
    """
    Study the room the way the room studies you.

    Usage:
      observe

    Counting the cameras is a skill. It improves the way any skill improves.
    """

    key = "observe"
    locks = "cmd:all()"
    help_category = "the grid"

    def func(self):
        caller = self.caller
        room = caller.location
        if not room:
            return
        sensors = [
            obj
            for obj in room.contents
            if hasattr(obj, "sensitivity") and not obj.destination
            and hasattr(obj, "db") and obj.db.active is not None
        ]
        skill = caller.skill("observation")
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
                if skill >= tuning.OBSERVE_TIER_DETAIL and sensor.db.active:
                    lines.append(
                        f" - {sensor.key}: {status}, sharpness "
                        f"{sensor.db.sensitivity}"
                    )
                else:
                    lines.append(f" - {sensor.key}: {status}")
        caller.msg("\n".join(lines))
        new_skill = caller.improve_skill("observation")
        if new_skill in (tuning.OBSERVE_TIER_STATUS, tuning.OBSERVE_TIER_DETAIL):
            caller.msg(
                "|=mSomething settles in the way you look at rooms. You will "
                "see more from now on.|n"
            )


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
    help_category = "the grid"

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
                "the recyclers — nothing with a name in it today."
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


class CmdPetition(Command):
    """
    Petition the Records Annex about your file.

    Usage:
      petition amend <entry> = <corrected text>
      petition redact <entry>

    Entry numbers are as shown in your dossier. Amendments and redactions are
    services of the Ministry of Records, payable in standing with the
    Ministry of Records, which is the sort of arrangement the Ministry finds
    elegant. The request itself is, of course, noted.
    """

    key = "petition"
    locks = "cmd:all()"
    help_category = "the grid"

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
        try:
            number = int(num_part.strip())
        except ValueError:
            caller.msg("Which entry? Use the number from your dossier.")
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


class CmdForge(Command):
    """
    Rewrite an entry in your file without asking anyone.

    Usage:
      forge <entry> = <new text>

    Possible only somewhere nothing watches at all. Done well, the file
    simply says something else now. Done badly, the file gains a page.
    """

    key = "forge"
    locks = "cmd:all()"
    help_category = "the grid"

    def func(self):
        from world import records, watch

        caller = self.caller
        room = caller.location
        if getattr(room, "visibility", 1) != 0 or room.exposure_gain() > 0:
            caller.msg(
                "Not here. Whatever you're considering, it wants a place "
                "with no eyes in it at all."
            )
            return

        num_part, sep, new_text = (self.args or "").partition("=")
        new_text = new_text.strip()
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

        skill = caller.skill("forgery")
        chance = tuning.FORGE_BASE_CHANCE + skill * tuning.FORGE_SKILL_BONUS
        caller.improve_skill("forgery")
        if random.random() < chance:
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
    Apply for elevated clearance (Form C-1).

    Usage:
      apply

    Heard at the Archive Annex, where the archivist keeps the forms. Grade
    C-1 clearance admits you to the Central Spire lobby. The Ministry will
    read your file, your function, and your ledger — in that order, and
    only the versions of them it has.
    """

    key = "apply"
    locks = "cmd:all()"
    help_category = "the grid"

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
        EvMenu(
            caller,
            "world.form_c1",
            startnode="node_start",
            cmd_on_exit=None,
        )

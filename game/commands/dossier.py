"""
The dossier: what the state's file says about you.

v2 (ADR 0005): a view over Record objects — the *record layer*. What actually
happened may differ; the audit trail beneath is not shown here, because the
Ministry does not show you that, because officially it does not exist.

Redacted entries vanish from the file but keep their numbers, so a careful
reader can see the gaps. The Ministry considers the numbering scheme to be
nobody's business.
"""

from evennia import Command


def _incident_lines(visible):
    """
    One line per incident, except runs of *consecutive* identical entries
    collapse into one line with a number range and a count (the assembly-
    absence farm is the case this exists for: 35 duplicate lines in a row,
    round-two playtest finding 7). Non-consecutive repeats stay separate —
    collapsing across the whole file, not just a run, would erase exactly
    the numbering the redaction gap depends on to be visible.
    """
    lines = []
    i = 0
    while i < len(visible):
        number, rec = visible[i]
        content = rec.db.content
        j = i + 1
        while j < len(visible) and visible[j][1].db.content == content:
            j += 1
        run = visible[i:j]
        if len(run) == 1:
            lines.append(f"   {number}. {content}")
        else:
            lines.append(f"   {number}-{run[-1][0]}. {content} ({len(run)})")
        i = j
    return lines


class CmdDossier(Command):
    """
    Request your own citizen file from the Ministry of Records.

    Usage:
      dossier

    The Ministry is required to show you your file. The Ministry is not
    required to make it accurate.
    """

    key = "dossier"
    # "score" is what thirty years of MUD muscle memory will type for
    # "show me my character" — it should land somewhere useful (v0.7).
    aliases = ["file", "record", "score"]
    locks = "cmd:all()"
    help_category = "sector 9"

    def func(self):
        from world import grades, records, tuning

        caller = self.caller
        # The file contains what the Ministry observed, and only that: the
        # skills you learned off the books and the ledger the Grid cannot
        # read are not in it. Your absence of paperwork is your own.
        skills = {
            name: value
            for name, value in (caller.db.skills or {}).items()
            if name not in tuning.UNSANCTIONED_SKILLS
        }
        standing = caller.db.standing or {}
        influence = {
            faction: value
            for faction, value in (caller.db.influence or {}).items()
            if faction not in tuning.UNSANCTIONED_FACTIONS
        }

        width = 52
        lines = [
            "|=k" + "=" * width + "|n",
            "|w MINISTRY OF RECORDS — CITIZEN FILE|n",
            "|=k" + "-" * width + "|n",
            f" Subject:   {caller.key}",
            f" Grade:     Citizen, Grade {grades.grade_of(caller)}",
            f" Function:  {standing.get('function', '|=munassigned|n')}",
            f" Clearance: {standing.get('clearance', 'none on record')}",
            f" Exposure:  {caller.exposure}",
        ]
        points, nxt, threshold = grades.next_review(caller)
        if nxt:
            lines.append(
                f" Merit on record: {points}. Review threshold for "
                f"Grade {nxt}: {threshold}."
            )
        else:
            lines.append(
                f" Merit on record: {points}. |=mNo further elevation is "
                "contemplated.|n"
            )
        if skills:
            lines.append(" Recorded aptitudes:")
            lines.extend(
                f"   {name}: {value}" for name, value in sorted(skills.items())
            )
        else:
            lines.append(" Recorded aptitudes: |=mnone observed|n")
        if influence:
            lines.append(" Standing with institutions:")
            lines.extend(
                f"   {faction}: {value}" for faction, value in sorted(influence.items())
            )
        else:
            # Round-two playtest finding 2: a new citizen had no way to
            # even learn "standing" is a concept until they'd already
            # earned some. Naming it here, at zero, is the fix; `help
            # standing` explains what it is and how it moves.
            lines.append(" Standing with institutions: |=mnone recorded yet|n")

        incidents = records.records_for(caller, kind="incident")
        visible = [
            (rec.db.number, rec) for rec in incidents if not rec.db.redacted
        ]
        if visible:
            lines.append(" Incidents on record:")
            lines.extend(_incident_lines(visible))
        elif incidents:
            # Everything redacted: the file is clean in the way a scrubbed
            # floor is clean.
            lines.append(" Incidents on record: |=mnone|n")
        else:
            lines.append(" Incidents on record: |=mnone|n")

        movements = records.records_for(caller, kind="observation")
        if movements:
            lines.append(" Movements on file (most recent):")
            lines.extend(f"   - {rec.db.content}" for rec in movements[-3:])

        lines.append("|=k" + "-" * width + "|n")
        lines.append("|=m This file is accurate. This file has always been accurate.|n")
        lines.append("|=k" + "=" * width + "|n")
        caller.msg("\n".join(lines))

        from world.onboarding import acknowledge_first_use

        acknowledge_first_use(caller, "dossier")

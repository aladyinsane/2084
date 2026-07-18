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


class CmdDossier(Command):
    """
    Request your own citizen file from the Ministry of Records.

    Usage:
      dossier

    The Ministry is required to show you your file. The Ministry is not
    required to make it accurate.
    """

    key = "dossier"
    aliases = ["file", "record"]
    locks = "cmd:all()"
    help_category = "the grid"

    def func(self):
        from world import records

        caller = self.caller
        skills = caller.db.skills or {}
        standing = caller.db.standing or {}
        influence = caller.db.influence or {}

        width = 52
        lines = [
            "|=k" + "=" * width + "|n",
            "|w MINISTRY OF RECORDS — CITIZEN FILE|n",
            "|=k" + "-" * width + "|n",
            f" Subject:   {caller.key}",
            f" Function:  {standing.get('function', '|=munassigned|n')}",
            f" Clearance: {standing.get('clearance', 'none on record')}",
            f" Exposure:  {caller.exposure}",
        ]
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

        incidents = records.records_for(caller, kind="incident")
        visible = [
            (number, rec)
            for number, rec in enumerate(incidents, 1)
            if not rec.db.redacted
        ]
        if visible:
            lines.append(" Incidents on record:")
            lines.extend(
                f"   {number}. {rec.db.content}" for number, rec in visible
            )
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

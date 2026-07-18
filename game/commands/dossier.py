"""
The dossier: what the state's file says about you.

v0.1 stub — a view over plain attributes. Replaced in v0.3 by real record
objects with the record/truth split (ADR 0005); the calcification risk of this
stub is named in that ADR.
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
        lines.append("|=k" + "-" * width + "|n")
        lines.append("|=m This file is accurate. This file has always been accurate.|n")
        lines.append("|=k" + "=" * width + "|n")
        caller.msg("\n".join(lines))

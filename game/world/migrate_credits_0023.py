"""
One-time data migration for ADR 0023 (docs/decisions/0023-credits-split-
from-standing.md): splits the old `db.influence` ledger into `db.standing`
(trust, per faction, from the old `db.influence_earned`) and `db.credits`
(a single fungible pool, summed from whatever spendable balance was left
in `db.influence` across every faction, sanctioned and Underground alike).
Also renames the old civic-status `db.standing` (function/clearance) to
`db.civic_status`, freeing the name for the trust ledger.

Not an Evennia/Django schema migration — Attributes aren't schema-backed,
so this is a plain data pass over every Character. Run once, from the game
directory, against a real or test database:

    evennia shell < world/migrate_credits_0023.py

Idempotent: a character with no `db.influence` and no old-shaped
`db.standing` left is skipped, so running this twice is harmless.
"""

from evennia.objects.models import ObjectDB


def run():
    migrated = 0
    skipped = 0
    for obj in ObjectDB.objects.all():
        has_old_influence = obj.attributes.has("influence")
        has_old_earned = obj.attributes.has("influence_earned")
        old_standing = obj.attributes.get("standing", default=None)
        # The old civic-status dict only ever held these two keys; the new
        # trust ledger is keyed by faction names instead. That shape
        # difference is how we tell which "standing" attribute this is,
        # for a character caught mid-migration or partially hand-edited.
        is_old_civic_shape = isinstance(old_standing, dict) and (
            "function" in old_standing
            or "function_key" in old_standing
            or "clearance" in old_standing
        )
        if not (has_old_influence or has_old_earned or is_old_civic_shape):
            skipped += 1
            continue

        earned = obj.attributes.get("influence_earned", default={}) or {}
        new_standing = dict(earned)

        influence = obj.attributes.get("influence", default={}) or {}
        credits_total = sum(influence.values())

        if is_old_civic_shape:
            obj.attributes.add("civic_status", old_standing)

        obj.attributes.add("standing", new_standing)
        obj.attributes.add("credits", (obj.attributes.get("credits", default=0) or 0) + credits_total)

        obj.attributes.remove("influence")
        obj.attributes.remove("influence_earned")

        migrated += 1

    print(f"ADR 0023 migration: {migrated} character(s) migrated, {skipped} already clean.")


run()

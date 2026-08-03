"""

Lockfuncs

Lock functions are functions available when defining lock strings,
which in turn limits access to various game systems.

All functions defined globally in this module are assumed to be
available for use in lockstrings to determine access. See the
Evennia documentation for more info on locks.

A lock function is always called with two arguments, accessing_obj and
accessed_obj, followed by any number of arguments. All possible
arguments should be handled with *args, **kwargs. The lock function
should handle all eventual tracebacks by logging the error and
returning False.

Lock functions in this module extend (and will overload same-named)
lock functions from evennia.locks.lockfuncs.

"""

# def myfalse(accessing_obj, accessed_obj, *args, **kwargs):
#    """
#    called in lockstring with myfalse().
#    A simple logger that always returns false. Prints to stdout
#    for simplicity, should use utils.logger for real operation.
#    """
#    print "%s tried to access %s. Access denied." % (accessing_obj, accessed_obj)
#    return False


def clearance(accessing_obj, accessed_obj, *args, **kwargs):
    """
    Usage: clearance(N) — passes if the accessor holds clearance grade C-N
    or better. Clearance is institutional standing (ADR 0002/0003): granted
    by paperwork, revocable by the same.
    """
    from world import functions

    try:
        required = int(args[0])
    except (IndexError, ValueError):
        return False
    return functions.clearance_level(accessing_obj) >= required


def shadow_standing(accessing_obj, accessed_obj, *args, **kwargs):
    """
    Usage: shadow_standing(N) — passes if the accessor's underground
    standing (the same number `word` reads, ADR 0009) is at least N. The
    inverse gate of clearance(): unsanctioned standing, not institutional
    (ADR 0022).
    """
    from world import tuning

    try:
        required = int(args[0])
    except (IndexError, ValueError):
        return False
    standing = (accessing_obj.db.influence or {}).get(tuning.UNDERGROUND, 0)
    return standing >= required

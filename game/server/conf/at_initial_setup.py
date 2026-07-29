"""
At_initial_setup module template

Custom at_initial_setup method. This allows you to hook special
modifications to the initial server startup process. Note that this
will only be run once - when the server starts up for the very first
time! It is called last in the startup process and can thus be used to
overload things that happened before it.

The module must contain a global function at_initial_setup().  This
will be called without arguments. Note that tracebacks in this module
will be QUIETLY ignored, so make sure to check it well to make sure it
does what you expect it to.

"""

from evennia import create_script
from evennia.utils import logger


def at_initial_setup():
    # Tracebacks here are quietly swallowed by Evennia (see docstring above),
    # so everything is wrapped and logged explicitly.
    try:
        from world import build

        build.build()
        create_script("typeclasses.scripts.ExposureDecayScript")
        create_script("typeclasses.scripts.WatchSweepScript")
        create_script("typeclasses.scripts.PatrolManagerScript")
        create_script("typeclasses.scripts.AssemblyScript")
        create_script("typeclasses.scripts.MaintenanceScript")
        create_script("typeclasses.scripts.AmbienceScript")
        create_script("typeclasses.scripts.RecordCompactionScript")
        create_script("typeclasses.scripts.PropagandaScript")

        # (The gridwide channel is defined in settings.DEFAULT_CHANNELS, so
        # citizens are auto-subscribed at registration.)
        logger.log_info("2084: initial setup complete (world + watch scripts).")
    except Exception:
        logger.log_trace("2084: INITIAL SETUP FAILED")

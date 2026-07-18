# -*- coding: utf-8 -*-
"""
Connection screen

This is the text to show the user when they first connect to the game (before
they log in).

To change the login screen in this module, do one of the following:

- Define a function `connection_screen()`, taking no arguments. This will be
  called first and must return the full string to act as the connection screen.
  This can be used to produce more dynamic screens.
- Alternatively, define a string variable in the outermost scope of this module
  with the connection string that should be displayed. If more than one such
  variable is given, Evennia will pick one of them at random.

The commands available to the user when the connection screen is shown
are defined in evennia.default_cmds.UnloggedinCmdSet. The parsing and display
of the screen is done by the unlogged-in "look" command.

"""

from django.conf import settings

# Principle 9: no magic-missile moments — the first thing a player sees is
# already the Grid, not the engine. (Evennia version deliberately absent; the
# Ministry does not disclose its internals.)
CONNECTION_SCREEN = """
|=k________________________________________________________________|n

                          |w2 0 8 4|n

              MUNICIPAL ACCESS TERMINAL — SECTOR 9
          Ministry of Records — Citizen Interface v{}

   This terminal is provided for your security and convenience.
   Sessions are monitored. Sessions have always been monitored.

   Returning citizens, identify yourselves:
        |wconnect <name> <password>|n

   New arrivals, report for registration:
        |wcreate <name> <password>|n

   (Names containing spaces go in quotes. Type |whelp|n for the
   permitted forms of assistance.)
|=k________________________________________________________________|n""".format(
    settings.SERVERNAME
)

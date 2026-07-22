# Mobile web client

Prompted by Lauren (2026-07-21): a simple, mobile-friendly way to play 2084 in a
phone browser. Engineering research: what the current web client is built on, why it
doesn't work on a phone, and the plan for a purpose-built alternative. Verified against
the Evennia install in this repo (`.venv/Lib/site-packages/evennia`).

## What exists today

The web client at `webclient/` is 100% stock Evennia — `game/web/webclient/` has no
game-specific override beyond an empty `urls.py`. Concretely, that means:

- **GoldenLayout** for the pane layout (`webclient.html`/`base.html`): a draggable,
  resizable multi-pane window manager loaded from a CDN. Built for desktop; it has no
  small-screen mode. Panes are meant to be dragged into place, not stacked.
- **jQuery 3.2.1 + Bootstrap 4 + Popper**, all from CDNs — the UI chrome (toolbar,
  popups, options menu) is built on these.
- **`evennia.js`**: the actual game-protocol layer — opens the websocket, sends input,
  routes incoming messages by type (text, prompt, map, etc.) to whichever pane wants
  them. This part is engine plumbing, not GoldenLayout-specific, and everything below
  keeps using it.
- A plugin stack (`webclient_gui.js` + `plugins/*.js`) that wires GoldenLayout panes to
  `evennia.js` message types — `text2html.js` already converts the server's ANSI/color
  markup to HTML, which is exactly what a new client also needs.

None of this was customized for 2084 — no game-specific CSS, no mobile breakpoints,
nothing. It's the Evennia quickstart, unchanged.

## Why "responsive CSS on the existing client" doesn't work

GoldenLayout's whole interaction model — drag a tab to split the window, resize by
dragging borders — assumes a mouse and a wide viewport. There's no supported "stack
these panes vertically and hide the drag handles" mode; fighting it with media queries
means overriding a third-party library's internals, which breaks on every GoldenLayout
update and produces a UI that's still, underneath, a desktop window manager wearing a
trenchcoat. A phone player doesn't want panes at all — just the room text and a place to
type.

**Conclusion: a second, purpose-built lightweight client**, not a responsive layer on
the existing one. Same protocol (`evennia.js`'s websocket connection and message
format), a completely different — and much smaller — UI: one scrolling output area, a
fixed input bar, no panes to drag, no GoldenLayout/Bootstrap/jQuery-plugin weight.

## What a mobile client needs from the protocol

`evennia.js` already handles the parts that matter regardless of UI:
- Opening and maintaining the websocket connection (with the same `wsurl`/session-id
  setup `base.html` does today).
- Sending typed input.
- Receiving typed output (`text`, `prompt`, `map`, etc.) via `onText`-style callbacks.

A mobile client can reuse this file as-is and just replace everything that reads
GoldenLayout panes with a plain DOM append into one output container. `text2html.js`'s
ANSI-to-HTML conversion is reusable the same way — it's not tied to a pane, it's a pure
text-transform.

## Phased plan

1. **A new Django view + template**, not a GoldenLayout config change — e.g.
   `game/web/webclient/views.py::mobile` behind a `webclient/mobile/` route, with its own
   minimal template: single-column layout, `evennia.js` + `text2html.js` loaded, no
   GoldenLayout/Bootstrap/jQuery-UI-plugin script tags. This is the bulk of the work and
   the only phase that needs deciding now.
2. **Rendering correctness.** Everything server-side (item 1's room spacing, the
   prompt's exposure color-banding and trend marker from `feat/prompt-legibility`) is
   just ANSI markup — it should render correctly for free once `text2html.js` is wired
   up, but needs an actual-phone check, not just a resized desktop browser, since mobile
   Safari/Chrome handle viewport units and on-screen-keyboard resizing differently from
   desktop.
3. **Touch-friendly input.** A persistent input bar that doesn't get covered by the
   on-screen keyboard, and — since typing on a phone is real friction for a MUD — a
   small row of buttons for the highest-frequency verbs (`look`, `map`, `next`,
   `errands`) that just inject text into the input and submit.
4. **Routing.** Auto-detect mobile user agents and redirect to `webclient/mobile/`, vs.
   a manual "play on mobile" link. Auto-detect is friendlier but risks false positives
   (tablets, foldables) sending someone to a client with less on-screen information than
   they'd want — worth deciding after phase 1 is playable and can actually be tried on a
   few real devices.

Phase 1 is the only phase with no open design questions — a new lightweight template
reusing the existing protocol layer. Phases 2–4 depend on trying phase 1 on a real
phone first.

## Honest costs

- **A second client to maintain.** Any new server-side message type has to be handled
  in both UIs (or the mobile one degrades gracefully by ignoring types it doesn't
  render — acceptable for a first pass, since 2084's message types are mostly plain
  text plus a `map` type already ANSI-renderable as text).
- **No offline/native app.** This is a mobile-*browser* client, not a wrapped app —
  no push notifications, no home-screen icon beyond what a browser's "add to home
  screen" already offers for any website.
- **Testing needs real devices**, not just a narrow desktop browser window — on-screen
  keyboard behavior and viewport-resize quirks don't show up in desktop dev tools
  emulation reliably.

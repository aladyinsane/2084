"""
Shared bordered rendering for the Grid's bureaucratic forms (Form 1-A, 2-B,
9-A, 12-D, C-1) — one border style, not one invented per form.
"""

FORM_WIDTH = 50
_RULE = "|w" + "=" * FORM_WIDTH + "|n"


def form_box(*lines):
    """
    Wrap pre-formatted lines in a top/bottom ASCII rule, each line indented
    two spaces. Callers keep full control of their own color codes — Evennia
    color tags don't count toward visible width, so this stays left-aligned
    only rather than trying to right-close the box against a moving target.
    """
    body = "\n".join(f"  {line}" for line in lines)
    return f"{_RULE}\n{body}\n{_RULE}"

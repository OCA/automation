`automation_oca` activity steps support a static **Note** and **Summary** field,
which are written as plain text or HTML at configuration time and copied verbatim
to every activity created by the step.

This is limiting when the note needs to reflect data specific to each record —
for example, a personalised LinkedIn outreach prompt.

`automation_oca_activity_note_template` solves this by delegating the rendering
to a **mail template**, which already has a well-established mechanism for
per-record dynamic content and is familiar to Odoo users.

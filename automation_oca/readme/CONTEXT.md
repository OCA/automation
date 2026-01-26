Odoo core provides `base_automation`, which is well suited for **simple, isolated rules**
triggered by **internal record changes** (e.g. *on create*, *on update*, *on delete*, or *timed conditions*).

When processes become more complex (multiple steps, different timings, conditional paths),
it can be harder to understand and maintain the whole flow in `base_automation`.

`automation_oca` focuses on **workflow-based automations**, where the full process is defined
as a sequence of steps with **timings** and **dependencies**, and can also react to **external events**
such as email interactions (opened, replied, clicked, bounced, etc).

In short:

- use **`base_automation`** for simple automations driven by internal record updates
- use **`automation_oca`** for multi-step workflows with timings, dependencies, and external events

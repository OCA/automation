# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MailActivity(models.Model):
    _inherit = "mail.activity"

    automation_record_step_id = fields.Many2one("automation.record.step")

    def _action_done(self, *args, **kwargs):
        if self.automation_record_step_id:
            self.automation_record_step_id._set_activity_done()
        return super(
            MailActivity,
            self.with_context(
                automation_done=True,
            ),
        )._action_done(*args, **kwargs)

    def unlink(self):
        if self.automation_record_step_id and not self.env.context.get(
            "automation_done"
        ):
            self.automation_record_step_id._set_activity_cancel()
        return super(MailActivity, self).unlink()

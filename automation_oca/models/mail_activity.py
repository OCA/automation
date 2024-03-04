# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MailActivity(models.Model):
    _inherit = "mail.activity"

    automation_record_step_id = fields.Many2one("automation.record.step")

    def _action_done(self, *args, **kwargs):
        if self.automation_record_step_id:
            self.automation_record_step_id._set_activity_done()
        return super()._action_done(*args, **kwargs)

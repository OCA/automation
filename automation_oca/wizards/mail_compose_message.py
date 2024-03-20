# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MailComposeMessage(models.TransientModel):

    _inherit = "mail.compose.message"

    automation_record_activity_id = fields.Many2one("automation.record.activity")

    def get_mail_values(self, res_ids):
        result = super().get_mail_values(res_ids)
        if self.automation_record_activity_id:
            for res_id in res_ids:
                result[res_id][
                    "automation_record_activity_id"
                ] = self.automation_record_activity_id.id
        return result

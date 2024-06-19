# Copyright 2024 Dixmit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MailNotification(models.Model):
    _inherit = "mail.notification"

    def _set_read_gateway(self):
        res = super()._set_read_gateway()
        msg_references = self.mapped("mail_message_id.message_id") + self.mapped(
            "mail_message_id.gateway_message_id.message_id"
        )
        records = self.env["automation.record.step"].search(
            [("message_id", "in", msg_references)]
        )
        records._set_mail_open()
        return res

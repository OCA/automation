# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SignOcaRequest(models.Model):

    _inherit = "sign.oca.request"

    automation_step_id = fields.Many2one(
        "automation.record.step",
        readonly=True,
    )

    def _signed_hook(self):
        res = super()._signed_hook()
        self.automation_step_id._set_sign_signed()
        return res

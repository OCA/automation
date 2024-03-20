# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AutomationFilter(models.Model):
    _name = "automation.filter"
    _description = "Automation Filter"

    name = fields.Char(required=True)
    model_id = fields.Many2one(
        "ir.model",
        domain=[("is_mail_thread", "=", True)],
        required=True,
        ondelete="cascade",
        help="Model where the configuration is applied",
    )
    model = fields.Char(related="model_id.model")
    domain = fields.Char(required=True, default="[]", help="Filter to apply")

    @api.onchange("model_id")
    def _onchange_model(self):
        self.domain = []

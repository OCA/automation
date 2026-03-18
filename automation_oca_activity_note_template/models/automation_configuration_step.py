# Copyright 2026 ForgeFlow
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AutomationConfigurationStep(models.Model):
    _inherit = "automation.configuration.step"

    activity_note_template_id = fields.Many2one(
        "mail.template",
        string="Note Template",
        domain="[('model_id', '=', model_id)]",
        help="If set, the activity note is rendered from this mail template. "
        "The template body may use {{ object.method() }} expressions. "
        "Overrides the static Note field.",
    )

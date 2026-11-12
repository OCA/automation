# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AutomationConfigurationExport(models.TransientModel):
    _name = "automation.configuration.export"
    _description = "Export Automation Configuration"

    configuration_id = fields.Many2one(
        comodel_name="automation.configuration",
        required=True,
    )
    file_name = fields.Char()
    file_content = fields.Binary(readonly=True)

# Copyright 2024 KMEE
# License LGLP-3.0 or later (https://www.gnu.org/licenses/lglp).

from odoo import fields, models


class IaExecutionData(models.Model):

    _name = "ai.execution.data"
    _description = "ai Execution Data"

    key = fields.Char(required=True)
    value = fields.Char(required=True)
    execution_id = fields.Many2one("ai.execution", required=True)

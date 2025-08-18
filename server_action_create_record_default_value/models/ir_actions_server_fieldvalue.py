# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrActionsServerFieldValue(models.Model):
    _name = "ir.actions.server.fieldvalue"
    _description = "Server Action Field Value"

    server_action_id = fields.Many2one(
        "ir.actions.server", required=True, ondelete="cascade"
    )
    field_id = fields.Many2one(
        "ir.model.fields",
        domain="[('model_id', '=', parent.crud_model_id), "
        "('ttype', 'in', ('text', 'char', 'date', 'integer', "
        "'float', 'many2one', 'selection'))]",
        required=True,
        ondelete="cascade",
    )
    value = fields.Char()

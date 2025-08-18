# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import Command, _, fields, models
from odoo.exceptions import ValidationError

from ..tools import evaluate_python_expression


class IrActionsServer(models.Model):
    _inherit = "ir.actions.server"

    field_default_value_ids = fields.One2many(
        "ir.actions.server.fieldvalue",
        "server_action_id",
        string="Field Default Values",
    )

    # NOTE: This method overrides `_run_action_object_create` without calling `super()`.
    # Although bypassing `super()` is generally discouraged, it is intentional here
    # because the original implementation only supports creating a record using
    # "name_create(self.value)", which sets the "name" field only.
    # In contrast, this version allows creating a record in a configurable target model
    # (`crud_model_id`) with multiple dynamically evaluated field values
    # provided through `field_default_value_ids`.
    def _run_action_object_create(self, eval_context=None):
        """Create a record in `crud_model_id` using field_default_value_ids,
        or fallback to default `name_create(self.value)` logic if none are defined.
        """
        self.ensure_one()

        # Fallback to Odoo default behavior if no custom defaults are set
        if not self.field_default_value_ids:
            return super()._run_action_object_create(eval_context=eval_context)

        # Evaluate values for the destination record
        record = self.env[self.model_id.model].browse(self._context.get("active_id"))
        vals = {}
        for line in self.field_default_value_ids:
            try:
                vals[line.field_id.name] = evaluate_python_expression(
                    line.value, {"object": record}
                )
            except Exception as e:
                raise ValidationError(
                    _("Error evaluating value for field '%(field)s': %(error)s"),
                    params={"field": line.field_id.name, "error": str(e)},
                ) from e

        # Create the new record in the target model
        new_record = self.env[self.crud_model_id.model].create(vals)

        if self.link_field_id:
            record = self.env[self.model_id.model].browse(
                self._context.get("active_id")
            )
            if self.link_field_id.ttype in ["one2many", "many2many"]:
                record.write({self.link_field_id.name: [Command.link(new_record.id)]})
            else:
                record.write({self.link_field_id.name: new_record.id})

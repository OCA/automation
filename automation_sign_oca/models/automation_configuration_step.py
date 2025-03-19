# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class AutomationConfigurationStep(models.Model):

    _inherit = "automation.configuration.step"

    step_type = fields.Selection(
        selection_add=[("sign", "Sign")], ondelete={"sign": "cascade"}
    )
    sign_template_id = fields.Many2one("sign.oca.template")
    sign_signer_partner_field_id = fields.Many2one(
        "ir.model.fields",
        domain="[('model_id', '=', model_id), ('relation', '=', 'res.partner')]",
        string="Signer Partner Field",
    )

    @api.model
    def _step_icons(self):
        result = super()._step_icons()
        result["sign"] = "fa fa-pencil-square-o"
        return result

    @api.model
    def _trigger_types(self):
        result = super()._trigger_types()
        result.update(
            {
                "sign_signed": {
                    "name": _("Signed"),
                    "allow_expiry": True,
                    "step_type": ["sign"],
                    "color": "text-success",
                    "icon": "fa fa-pencil-square-o",
                    "message_configuration": _("Signed after"),
                    "message": _("Not Signed yet"),
                },
                "sign_not_signed": {
                    "name": _("Not Signed"),
                    "step_type": ["sign"],
                    "color": "text-danger",
                    "icon": "fa fa-pencil-square-o",
                    "message_configuration": _("Not Signed within"),
                    "message": False,
                },
            }
        )
        return result

    def _get_record_activity_scheduled_date(self):
        if self.trigger_type in ["sign_signed"]:
            return False
        return super()._get_record_activity_scheduled_date()

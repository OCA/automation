# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AutomationConfigurationStep(models.Model):

    _inherit = "automation.configuration.step"
    step_type = fields.Selection(
        selection_add=[("gateway", "Gateway")], ondelete={"gateway": "cascade"}
    )
    gateway_id = fields.Many2one("mail.gateway")
    gateway_author_id = fields.Many2one("res.users")
    gateway_template_id = fields.Many2one(
        "mail.template", domain="[('model_id', '=', model_id)]"
    )
    gateway_field_id = fields.Many2one("ir.model.fields")

    def _get_mail_activities(self):
        return super()._get_mail_activities() + ["gateway"]

    @api.model
    def _step_icons(self):
        result = super()._step_icons()
        result["gateway"] = "fa fa-paper-plane-o"
        return result

    @api.model
    def _trigger_types(self):
        result = super()._trigger_types()
        result["mail_open"]["step_type"].append("gateway")
        result["mail_not_open"]["step_type"].append("gateway")
        result["mail_reply"]["step_type"].append("gateway")
        result["mail_not_reply"]["step_type"].append("gateway")
        return result

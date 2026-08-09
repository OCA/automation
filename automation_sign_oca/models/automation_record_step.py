# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class AutomationRecordStep(models.Model):

    _inherit = "automation.record.step"

    sign_signed_on = fields.Datetime(readonly=True)

    def _run_sign_generate_vals(self):
        record = self.env[self.record_id.model].browse(self.record_id.res_id)
        return {
            "automation_step_id": self.id,
            "name": self.configuration_step_id.sign_template_id.name,
            "template_id": self.configuration_step_id.sign_template_id.id,
            "signatory_data": self.configuration_step_id.sign_template_id._get_signatory_data(),
            "data": self.configuration_step_id.sign_template_id.data,
            "ask_location": self.configuration_step_id.sign_template_id.ask_location,
            "signer_ids": [
                (
                    0,
                    0,
                    {
                        "partner_id": (
                            role.partner_selection_policy == "default"
                            and role.default_partner_id.id
                        )
                        or record[
                            self.configuration_step_id.sign_signer_partner_field_id.name
                        ].id,
                        "role_id": role.id,
                    },
                )
                for role in self.configuration_step_id.sign_template_id.item_ids.role_id
            ],
        }

    def _run_sign(self):
        request = self.env["sign.oca.request"].create(self._run_sign_generate_vals())
        request.action_send()
        self._fill_childs()

    def _set_sign_signed(self):
        self.filtered(lambda t: not t.sign_signed_on).write(
            {"sign_signed_on": fields.Datetime.now()}
        )
        self.child_ids.filtered(
            lambda r: r.trigger_type in ["sign_signed"]
            and not r.scheduled_date
            and r.state == "scheduled"
        )._activate()

    def _check_to_execute(self):
        if (
            self.configuration_step_id.trigger_type == "sign_not_signed"
            and self.parent_id.sign_signed_on
        ):
            return False
        return super()._check_to_execute()

    def _get_step_actions(self):
        actions = super()._get_step_actions()
        if self.step_type == "sign":
            actions.append(
                {
                    "icon": "fa fa-pencil-square-o",
                    "name": _("Signed"),
                    "done": bool(self.sign_signed_on),
                    "color": "text-success",
                }
            )
        return actions

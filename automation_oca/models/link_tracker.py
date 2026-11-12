# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class LinkTrackerClick(models.Model):
    _inherit = "link.tracker.click"

    automation_record_step_id = fields.Many2one("automation.record.step")
    automation_configuration_step_id = fields.Many2one(
        related="automation_record_step_id.configuration_step_id", store=True
    )
    automation_configuration_id = fields.Many2one(
        related="automation_record_step_id.configuration_id", store=True
    )

    @api.model
    def add_click(self, code, automation_record_step_id=False, **route_values):
        if automation_record_step_id:
            tracker_code = self.env["link.tracker.code"].search([("code", "=", code)])
            if not tracker_code:
                return None
            ip = route_values.get("ip", False)
            if self.search_count(
                [
                    (
                        "automation_record_step_id",
                        "=",
                        automation_record_step_id,
                    ),
                    ("link_id", "=", tracker_code.link_id.id),
                    ("ip", "=", ip),
                ]
            ):
                return None
            route_values["link_id"] = tracker_code.link_id.id
            click_values = self._prepare_click_values_from_route(
                automation_record_step_id=automation_record_step_id, **route_values
            )
            click = self.create(click_values)
            click.automation_record_step_id._set_mail_open()
            click.automation_record_step_id._set_mail_clicked()
            return click
        return super().add_click(code, **route_values)

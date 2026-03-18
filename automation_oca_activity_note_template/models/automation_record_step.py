# Copyright 2026 ForgeFlow
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from dateutil.relativedelta import relativedelta

from odoo import fields, models


class AutomationRecordStep(models.Model):
    _inherit = "automation.record.step"

    def _render_template_for_record(
        self, template_src, res_id, engine="inline_template"
    ):
        rendered = self.env["mail.template"]._render_template(
            template_src,
            self.record_id.model,
            [res_id],
            engine=engine,
        )
        return rendered.get(res_id, "")

    def _get_activity_summary(self):
        template = self.configuration_step_id.activity_note_template_id
        if not template:
            return self.configuration_step_id.activity_summary or ""
        return self._render_template_for_record(template.subject, self.record_id.res_id)

    def _get_activity_note(self):
        template = self.configuration_step_id.activity_note_template_id
        if not template:
            return self.configuration_step_id.activity_note or ""
        return self._render_template_for_record(
            template.body_html, self.record_id.res_id
        )

    def _run_activity(self):
        if not self.configuration_step_id.activity_note_template_id:
            return super()._run_activity()

        record = self.env[self.record_id.model].browse(self.record_id.res_id)
        step = self.configuration_step_id
        vals = {
            "summary": self._get_activity_summary(),
            "note": self._get_activity_note(),
            "activity_type_id": step.activity_type_id.id,
            "automation_record_step_id": self.id,
        }
        if step.activity_date_deadline_range > 0:
            range_type = step.activity_date_deadline_range_type
            vals["date_deadline"] = fields.Date.context_today(self) + relativedelta(
                **{range_type: step.activity_date_deadline_range}
            )
        user = False
        if step.activity_user_type == "specific":
            user = step.activity_user_id
        elif step.activity_user_type == "generic":
            user = record[step.activity_user_field_id.name]
        if user:
            vals["user_id"] = user.id
        record.activity_schedule(**vals)
        return True

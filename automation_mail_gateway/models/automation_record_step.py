# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import threading

from odoo import _, models
from odoo.exceptions import UserError


class AutomationRecordStep(models.Model):

    _inherit = "automation.record.step"

    def _run_gateway(self):
        record = self.env[self.record_id.model].browse(self.record_id.res_id)
        partner = record[self.configuration_step_id.gateway_field_id.name]
        channel = partner.gateway_channel_ids.filtered(
            lambda r: r.gateway_id == self.configuration_step_id.gateway_id
        )
        if not channel:
            raise UserError(
                _("Partner has no channel to send with gateway %s")
                % self.configuration_step_id.gateway_id.name
            )
        channel = channel[0]
        author_id = self.configuration_step_id.gateway_author_id.id
        composer_values = {
            "author_id": author_id,
            "record_name": False,
            "model": self.record_id.model,
            "composition_mode": "mass_post",
            "template_id": self.configuration_step_id.gateway_template_id.id,
            "automation_record_step_id": self.id,
        }
        res_ids = [self.record_id.res_id]
        composer = (
            self.env["mail.compose.message"]
            .with_context(active_ids=res_ids)
            .create(composer_values)
        )
        composer.write(
            composer._onchange_template_id(
                self.configuration_step_id.gateway_template_id.id,
                "mass_post",
                self.record_id.model,
                self.record_id.res_id,
            )["value"]
        )
        # composer.body =
        extra_context = self._run_mail_context()
        composer = composer.with_context(active_ids=res_ids, **extra_context)
        # auto-commit except in testing mode
        auto_commit = not getattr(threading.current_thread(), "testing", False)
        if not self.is_test:
            # We just abort the sending, but we want to check how the generation works
            _mails, messages = composer._action_send_mail(auto_commit=auto_commit)
            messages.with_context(
                automation_record_step_id=self.id
            )._send_to_gateway_thread(channel)
        self.mail_status = "sent"
        self.message_id = messages.message_id
        self._fill_childs()
        return

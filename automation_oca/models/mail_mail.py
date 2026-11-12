# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

import werkzeug.urls

from odoo import api, fields, models, tools


class MailMail(models.Model):
    _inherit = "mail.mail"

    automation_record_step_id = fields.Many2one("automation.record.step")

    @api.model_create_multi
    def create(self, values_list):
        records = super().create(values_list)
        for record in records.filtered("automation_record_step_id"):
            record.automation_record_step_id.message_id = record.message_id
        return records

    def _prepare_outgoing_body(self):
        """Override to add the tracking URL to the body and to add trace ID in
        shortened urls"""
        self.ensure_one()
        # super() already cleans pseudo-void content from editor
        body = super()._prepare_outgoing_body()
        if body and self.automation_record_step_id:
            body = self.env["mail.render.mixin"]._shorten_links(body, {})
            Wrapper = body.__class__
            token = self.automation_record_step_id._get_mail_tracking_token()
            for match in set(re.findall(tools.mail.URL_REGEX, body)):
                href = match[0]
                url = match[1]

                parsed = werkzeug.urls.url_parse(url, scheme="http")

                if parsed.scheme.startswith("http") and parsed.path.startswith("/r/"):
                    new_href = href.replace(
                        url,
                        f"{url}/au/{str(self.automation_record_step_id.id)}/{token}",
                    )
                    body = body.replace(Wrapper(href), Wrapper(new_href))

            # generate tracking URL
            tracking_url = self.automation_record_step_id._get_mail_tracking_url()
            body = tools.mail.append_content_to_html(
                body,
                f'<img src="{tracking_url}"/>',
                plaintext=False,
            )
        return body

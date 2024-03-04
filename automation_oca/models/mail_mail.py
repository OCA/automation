# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

import markupsafe
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

    def _send_prepare_body(self):
        body = super()._send_prepare_body()
        if self.automation_record_step_id:
            body = self.env["mail.render.mixin"]._shorten_links(body, {}, blacklist=[])
            token = self.automation_record_step_id._get_mail_tracking_token()
            for match in set(re.findall(tools.URL_REGEX, body)):
                href = match[0]
                url = match[1]

                parsed = werkzeug.urls.url_parse(url, scheme="http")

                if parsed.scheme.startswith("http") and parsed.path.startswith("/r/"):
                    new_href = href.replace(
                        url,
                        "%s/au/%s/%s"
                        % (url, str(self.automation_record_step_id.id), token),
                    )
                    body = body.replace(
                        markupsafe.Markup(href), markupsafe.Markup(new_href)
                    )
            body = tools.append_content_to_html(
                body,
                '<img src="%s"/>'
                % self.automation_record_step_id._get_mail_tracking_url(),
                plaintext=False,
            )
        return body

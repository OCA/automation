# Copyright 2024 Dixmit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

import markupsafe
import werkzeug.urls

from odoo import models, tools


class MailGatewayAbstract(models.AbstractModel):
    _inherit = "mail.gateway.abstract"

    def _post_process_reply(self, related_message):
        msg_references = related_message.mapped("message_id") + related_message.mapped(
            "gateway_message_id.message_id"
        )
        records = self.env[""].search([("message_id", "in", msg_references)])
        records._set_mail_reply()
        return super()._post_process_reply(related_message)

    def _get_message_body(self, record):
        body = super()._get_message_body(record)
        if self.env.context.get("automation_record_step_id"):
            body = self.env["mail.render.mixin"]._shorten_links(body, {}, blacklist=[])
            record_activity = self.env["automation.record.step"].browse(
                self.env.context.get("automation_record_step_id")
            )
            token = record_activity._get_mail_tracking_token()
            for match in set(re.findall(tools.URL_REGEX, body)):
                href = match[0]
                url = match[1]

                parsed = werkzeug.urls.url_parse(url, scheme="http")
                if parsed.scheme.startswith("http") and parsed.path.startswith("/r/"):
                    new_href = href.replace(
                        url,
                        "%s/au/%s/%s"
                        % (
                            url,
                            str(self.env.context.get("automation_record_step_id")),
                            token,
                        ),
                    )
                    body = body.replace(
                        markupsafe.Markup(href), markupsafe.Markup(new_href)
                    )
        return body

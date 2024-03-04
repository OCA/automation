# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, tools


class MailThread(models.AbstractModel):

    _inherit = "mail.thread"

    @api.model
    def _routing_handle_bounce(self, email_message, message_dict):
        """We want to mark the bounced email"""
        result = super(MailThread, self)._routing_handle_bounce(
            email_message, message_dict
        )
        bounced_msg_id = message_dict.get("bounced_msg_id")
        if bounced_msg_id:
            self.env["automation.record.step"].search(
                [("message_id", "in", bounced_msg_id)]
            )._set_mail_bounced()
        return result

    @api.model
    def _message_route_process(self, message, message_dict, routes):
        """Override to update the parent mailing traces. The parent is found
        by using the References header of the incoming message and looking for
        matching message_id in automation.record.step."""
        if routes:
            thread_references = (
                message_dict["references"] or message_dict["in_reply_to"]
            )
            msg_references = tools.mail_header_msgid_re.findall(thread_references)
            if msg_references:
                records = self.env["automation.record.step"].search(
                    [("message_id", "in", msg_references)]
                )
                records._set_mail_open()
                records._set_mail_reply()
        return super(MailThread, self)._message_route_process(
            message, message_dict, routes
        )

    @api.model
    def get_automation_access(self, doc_ids, operation, model_name=False):
        """Retrieve access policy.

        The behavior is similar to `mail.thread` and `mail.message`
        and it relies on the access rules defines on the related record.
        The behavior can be customized on the related model
        by defining `_automation_record_access`.

        By default `write`, otherwise the custom permission is returned.
        """
        DocModel = self.env[model_name] if model_name else self
        create_allow = getattr(DocModel, "_automation_record_access", "write")
        if operation in ["write", "unlink"]:
            check_operation = "write"
        elif operation == "create" and create_allow in [
            "create",
            "read",
            "write",
            "unlink",
        ]:
            check_operation = create_allow
        elif operation == "create":
            check_operation = "write"
        else:
            check_operation = operation
        return check_operation

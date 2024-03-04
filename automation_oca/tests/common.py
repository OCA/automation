# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class AutomationTestCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["automation.configuration"].search([]).toggle_active()
        cls.action = cls.env["ir.actions.server"].create(
            {
                "name": "Demo action",
                "state": "code",
                "model_id": cls.env.ref("base.model_res_partner").id,
                "code": "records.write({'comment': env.context.get('key_value')})",
            }
        )
        cls.activity_type = cls.env["mail.activity.type"].create({"name": "DEMO"})
        cls.error_action = cls.env["ir.actions.server"].create(
            {
                "name": "Demo action",
                "state": "code",
                "model_id": cls.env.ref("base.model_res_partner").id,
                "code": "raise UserError('ERROR')",
            }
        )
        cls.template = cls.env["mail.template"].create(
            {
                "name": "My template",
                "model_id": cls.env.ref("base.model_res_partner").id,
                "subject": "Subject",
                "partner_to": "{{ object.id }}",
                "body_html": 'My template <a href="https://www.twitter.com" /> with link',
            }
        )
        cls.partner_01 = cls.env["res.partner"].create(
            {"name": "Demo partner", "comment": "Demo", "email": "test@test.com"}
        )
        cls.partner_02 = cls.env["res.partner"].create(
            {"name": "Demo partner 2", "comment": "Demo", "email": "test@test.com"}
        )
        cls.configuration = cls.env["automation.configuration"].create(
            {
                "name": "Test configuration",
                "model_id": cls.env.ref("base.model_res_partner").id,
                "is_periodic": True,
            }
        )

    @classmethod
    def create_server_action(cls, parent_id=False, **kwargs):
        return cls.env["automation.configuration.step"].create(
            {
                "name": "Demo activity",
                "parent_id": parent_id,
                "configuration_id": cls.configuration.id,
                "step_type": "action",
                "server_action_id": cls.action.id,
                "trigger_type": "after_step" if parent_id else "start",
                **kwargs,
            }
        )

    @classmethod
    def create_activity_action(cls, parent_id=False, **kwargs):
        return cls.env["automation.configuration.step"].create(
            {
                "name": "Demo activity",
                "parent_id": parent_id,
                "configuration_id": cls.configuration.id,
                "step_type": "activity",
                "activity_type_id": cls.activity_type.id,
                "trigger_type": "after_step" if parent_id else "start",
                **kwargs,
            }
        )

    @classmethod
    def create_mail_activity(cls, parent_id=False, trigger_type=False, **kwargs):
        return cls.env["automation.configuration.step"].create(
            {
                "name": "Demo activity",
                "parent_id": parent_id,
                "configuration_id": cls.configuration.id,
                "step_type": "mail",
                "mail_template_id": cls.template.id,
                "trigger_type": trigger_type
                or ("after_step" if parent_id else "start"),
                **kwargs,
            }
        )

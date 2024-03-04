# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import users

from odoo.addons.mail.tests.common import mail_new_test_user

from .common import AutomationTestCase


class TestAutomationSecurity(AutomationTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Removing rules in order to check only what we expect
        cls.env["ir.rule"].search(
            [("model_id", "=", cls.env.ref("base.model_res_partner").id)]
        ).toggle_active()

        cls.user_automation_01 = mail_new_test_user(
            cls.env,
            login="user_automation_01",
            name="User automation 01",
            email="user_automation_01@test.example.com",
            company_id=cls.env.user.company_id.id,
            notification_type="inbox",
            groups="base.group_user,automation_oca.group_automation_user",
        )
        cls.user_automation_02 = mail_new_test_user(
            cls.env,
            login="user_automation_02",
            name="User automation 01",
            email="user_automation_02@test.example.com",
            company_id=cls.env.user.company_id.id,
            notification_type="inbox",
            groups="base.group_user,automation_oca.group_automation_user",
        )
        cls.group_1 = cls.env["res.groups"].create(
            {
                "name": "G1",
                "users": [(4, cls.user_automation_01.id)],
                "rule_groups": [
                    (
                        0,
                        0,
                        {
                            "name": "Rule 01",
                            "model_id": cls.env.ref("base.model_res_partner").id,
                            "domain_force": "[('id', '!=', %s)]" % cls.partner_01.id,
                        },
                    )
                ],
            }
        )
        cls.group_2 = cls.env["res.groups"].create(
            {
                "name": "G2",
                "users": [(4, cls.user_automation_02.id)],
                "rule_groups": [
                    (
                        0,
                        0,
                        {
                            "name": "Rule 01",
                            "model_id": cls.env.ref("base.model_res_partner").id,
                            "domain_force": "[('id', '!=', %s)]" % cls.partner_02.id,
                        },
                    )
                ],
            }
        )
        cls.configuration.editable_domain = [
            ("id", "in", (cls.partner_01 | cls.partner_02).ids)
        ]
        cls.configuration.start_automation()
        cls.env["automation.configuration"].cron_automation()

    @users("user_automation_01")
    def test_security_01(self):
        record = self.env["automation.record"].search(
            [("configuration_id", "=", self.configuration.id)]
        )
        self.assertEqual(1, len(record))
        self.assertEqual(self.partner_02, record.resource_ref)

    @users("user_automation_02")
    def test_security_02(self):
        record = self.env["automation.record"].search(
            [("configuration_id", "=", self.configuration.id)]
        )
        self.assertEqual(1, len(record))
        self.assertEqual(self.partner_01, record.resource_ref)

    @users("user_automation_01")
    def test_security_deleted_record(self):
        original_record = self.env["automation.record"].search(
            [("configuration_id", "=", self.configuration.id)]
        )
        self.partner_02.unlink()
        record = self.env["automation.record"].search(
            [("configuration_id", "=", self.configuration.id)]
        )
        self.assertFalse(record)
        self.assertTrue(original_record)
        self.assertFalse(original_record.read())

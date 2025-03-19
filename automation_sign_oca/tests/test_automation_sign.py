# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from .common import AutomationSignTestCase


class TestAutomationSign(AutomationSignTestCase):
    def test_sign_signed_child(self):
        sign_action = self.create_sign_action()
        activity_action = self.create_activity_action(
            parent_id=sign_action.id, trigger_type="sign_signed"
        )
        self.configuration.editable_domain = "[('id', '=', %s)]" % self.partner_01.id
        self.configuration.start_automation()
        self.env["automation.configuration"].cron_automation()
        self.assertFalse(
            self.env["sign.oca.request"].search(
                [("template_id", "=", self.sign_template.id)]
            )
        )
        self.env["automation.record.step"]._cron_automation_steps()
        sign_request = self.env["sign.oca.request"].search(
            [("template_id", "=", self.sign_template.id)]
        )
        self.assertTrue(sign_request)
        record_activity = self.env["automation.record.step"].search(
            [("configuration_step_id", "=", activity_action.id)]
        )
        self.assertTrue(record_activity)
        self.assertFalse(record_activity.scheduled_date)
        signer = sign_request.signer_ids.filtered(
            lambda s: s.partner_id == self.partner_01
        )
        self.assertTrue(signer)
        data = {}
        for key in signer.get_info()["items"]:
            val = signer.get_info()["items"][key].copy()
            val["value"] = "My Name"
            data[key] = val
        signer.action_sign(data)
        self.assertEqual(sign_request.state, "signed")
        record_activity.invalidate_recordset()
        self.assertTrue(record_activity.scheduled_date)

    def test_sign_signed_not_signed_child(self):
        sign_action = self.create_sign_action()
        activity_action = self.create_activity_action(
            parent_id=sign_action.id, trigger_type="sign_not_signed"
        )
        self.configuration.editable_domain = "[('id', '=', %s)]" % self.partner_01.id
        self.configuration.start_automation()
        self.env["automation.configuration"].cron_automation()
        self.assertFalse(
            self.env["sign.oca.request"].search(
                [("template_id", "=", self.sign_template.id)]
            )
        )
        self.env["automation.record.step"]._cron_automation_steps()
        sign_request = self.env["sign.oca.request"].search(
            [("template_id", "=", self.sign_template.id)]
        )
        self.assertTrue(sign_request)
        record_activity = self.env["automation.record.step"].search(
            [("configuration_step_id", "=", activity_action.id)]
        )
        self.assertTrue(record_activity)
        self.assertTrue(record_activity.scheduled_date)
        signer = sign_request.signer_ids.filtered(
            lambda s: s.partner_id == self.partner_01
        )
        self.assertTrue(signer)
        data = {}
        for key in signer.get_info()["items"]:
            val = signer.get_info()["items"][key].copy()
            val["value"] = "My Name"
            data[key] = val
        signer.action_sign(data)
        self.assertEqual(sign_request.state, "signed")
        self.assertEqual("scheduled", record_activity.state)
        record_activity.run()
        self.assertEqual("rejected", record_activity.state)

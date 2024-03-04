# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form

from .common import AutomationTestCase


class TestAutomationActivity(AutomationTestCase):
    def test_activity_execution(self):
        """
        We will check the execution of activity tasks (generation of an activity)
        """
        activity = self.create_activity_action()
        self.configuration.editable_domain = "[('id', '=', %s)]" % self.partner_01.id
        self.configuration.start_automation()
        self.env["automation.configuration"].cron_automation()
        self.assertFalse(self.partner_01.activity_ids)
        self.env["automation.record.step"]._cron_automation_steps()
        self.assertTrue(self.partner_01.activity_ids)
        record_activity = self.env["automation.record.step"].search(
            [("configuration_step_id", "=", activity.id)]
        )
        self.assertEqual(
            record_activity, self.partner_01.activity_ids.automation_record_step_id
        )
        self.assertFalse(record_activity.activity_done_on)
        record_activity.invalidate_recordset()
        self.assertFalse(
            [
                step
                for step in record_activity.step_actions
                if step["done"] and step["icon"] == "fa fa-clock-o"
            ]
        )
        self.partner_01.activity_ids.action_feedback()
        self.assertTrue(record_activity.activity_done_on)
        record_activity.invalidate_recordset()
        self.assertTrue(
            [
                step
                for step in record_activity.step_actions
                if step["done"] and step["icon"] == "fa fa-clock-o"
            ]
        )

    def test_activity_execution_child(self):
        """
        We will check the execution of the hild task (activity_done) is only scheduled
        after the activity is done
        """
        activity = self.create_activity_action()
        child_activity = self.create_server_action(
            parent_id=activity.id, trigger_type="activity_done"
        )
        self.configuration.editable_domain = "[('id', '=', %s)]" % self.partner_01.id
        self.configuration.start_automation()
        self.env["automation.configuration"].cron_automation()
        self.env["automation.record.step"]._cron_automation_steps()
        record_activity = self.env["automation.record.step"].search(
            [("configuration_step_id", "=", activity.id)]
        )
        record_child_activity = self.env["automation.record.step"].search(
            [("configuration_step_id", "=", child_activity.id)]
        )
        self.assertEqual(
            record_activity, self.partner_01.activity_ids.automation_record_step_id
        )
        self.assertFalse(record_activity.activity_done_on)
        self.assertFalse(record_child_activity.scheduled_date)
        self.partner_01.activity_ids.action_feedback()
        self.assertTrue(record_activity.activity_done_on)
        self.assertTrue(record_child_activity.scheduled_date)

    def test_activity_execution_not_done_child_done(self):
        """
        We will check the execution of the tasks with activity_not_done is not executed
        if it has been done
        """
        activity = self.create_activity_action()
        child_activity = self.create_server_action(
            parent_id=activity.id, trigger_type="activity_not_done"
        )
        self.configuration.editable_domain = "[('id', '=', %s)]" % self.partner_01.id
        self.configuration.start_automation()
        self.env["automation.configuration"].cron_automation()
        self.env["automation.record.step"]._cron_automation_steps()
        record_activity = self.env["automation.record.step"].search(
            [("configuration_step_id", "=", activity.id)]
        )
        record_child_activity = self.env["automation.record.step"].search(
            [("configuration_step_id", "=", child_activity.id)]
        )
        self.assertEqual(
            record_activity, self.partner_01.activity_ids.automation_record_step_id
        )
        self.assertFalse(record_activity.activity_done_on)
        self.assertTrue(record_child_activity.scheduled_date)
        self.partner_01.activity_ids.action_feedback()
        self.assertTrue(record_activity.activity_done_on)
        self.assertTrue(record_child_activity.scheduled_date)
        self.assertEqual("scheduled", record_child_activity.state)
        record_child_activity.run()
        self.assertEqual("rejected", record_child_activity.state)

    def test_activity_execution_not_done_child_not_done(self):
        """
        We will check the execution of the tasks with activity_not_done is executed
        if it has been not done
        """
        activity = self.create_activity_action()
        child_activity = self.create_server_action(
            parent_id=activity.id, trigger_type="activity_not_done"
        )
        self.configuration.editable_domain = "[('id', '=', %s)]" % self.partner_01.id
        self.configuration.start_automation()
        self.env["automation.configuration"].cron_automation()
        self.env["automation.record.step"]._cron_automation_steps()
        record_activity = self.env["automation.record.step"].search(
            [("configuration_step_id", "=", activity.id)]
        )
        record_child_activity = self.env["automation.record.step"].search(
            [("configuration_step_id", "=", child_activity.id)]
        )
        self.assertEqual(
            record_activity, self.partner_01.activity_ids.automation_record_step_id
        )
        self.assertFalse(record_activity.activity_done_on)
        self.assertTrue(record_child_activity.scheduled_date)
        self.assertEqual("scheduled", record_child_activity.state)
        record_child_activity.run()
        self.assertEqual("done", record_child_activity.state)

    def test_compute_default_values(self):
        activity = self.create_server_action()
        self.assertFalse(activity.activity_user_id)
        with Form(activity) as f:
            f.step_type = "activity"
            f.activity_type_id = self.activity_type
        self.assertTrue(activity.activity_user_id)
        with Form(activity) as f:
            f.step_type = "action"
            f.server_action_id = self.action
        self.assertFalse(activity.activity_user_id)

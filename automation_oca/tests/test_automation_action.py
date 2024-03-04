# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import AutomationTestCase


class TestAutomationAction(AutomationTestCase):
    def test_activity_execution(self):
        """
        We will check the execution of the tasks and that we cannot execute them again
        """
        activity = self.create_server_action()
        self.configuration.editable_domain = "[('id', '=', %s)]" % self.partner_01.id
        self.configuration.start_automation()
        self.env["automation.configuration"].cron_automation()
        self.assertTrue(self.partner_01.comment)
        self.assertTrue(self.partner_02.comment)
        self.env["automation.record.step"]._cron_automation_steps()
        self.assertFalse(self.partner_01.comment)
        self.assertTrue(self.partner_02.comment)
        record_activity = self.env["automation.record.step"].search(
            [("configuration_step_id", "=", activity.id)]
        )
        self.assertEqual(1, len(record_activity))
        self.assertEqual("done", record_activity.state)
        self.partner_01.comment = "My comment"
        # We check that the action is not executed again
        record_activity.run()
        self.assertFalse(record_activity.step_actions)
        self.assertTrue(self.partner_01.comment)

    def test_child_execution_filters(self):
        """
        We will create a task that executes two more tasks filtered with and extra task
        The child tasks should only be created after the first one is finished.
        Also, if one is aborted, the subsuquent tasks will not be created.
        TASK 1 ---> TASK 1_1 (only for partner 1) --> TASK 1_1_1
               ---> TASK 1_2 (only for partner 2) --> TASK 1_2_1

        In this case, the task 1_1_1 will only be generated for partner 1 and task 1_2_1
        for partner 2
        """
        self.configuration.editable_domain = "[('id', 'in', [%s, %s])]" % (
            self.partner_01.id,
            self.partner_02.id,
        )

        activity_1 = self.create_server_action()
        activity_1_1 = self.create_server_action(
            parent_id=activity_1.id, domain="[('id', '=', %s)]" % self.partner_01.id
        )
        activity_1_2 = self.create_server_action(
            parent_id=activity_1.id, domain="[('id', '=', %s)]" % self.partner_02.id
        )
        activity_1_1_1 = self.create_server_action(parent_id=activity_1_1.id)
        activity_1_2_1 = self.create_server_action(parent_id=activity_1_2.id)
        self.configuration.start_automation()
        self.env["automation.configuration"].cron_automation()
        self.assertEqual(
            0,
            self.env["automation.record.step"].search_count(
                [
                    (
                        "configuration_step_id",
                        "in",
                        (
                            activity_1_1
                            | activity_1_2
                            | activity_1_1_1
                            | activity_1_2_1
                        ).ids,
                    )
                ]
            ),
        )
        self.assertTrue(self.partner_01.comment)
        self.assertTrue(self.partner_02.comment)
        self.env["automation.record.step"]._cron_automation_steps()
        self.assertFalse(self.partner_01.comment)
        self.assertFalse(self.partner_02.comment)
        self.assertEqual(
            1,
            self.env["automation.record.step"].search_count(
                [
                    ("configuration_step_id", "=", activity_1_1.id),
                    ("record_id.res_id", "=", self.partner_01.id),
                ]
            ),
        )
        self.assertEqual(
            1,
            self.env["automation.record.step"].search_count(
                [
                    ("configuration_step_id", "=", activity_1_2.id),
                    ("record_id.res_id", "=", self.partner_01.id),
                ]
            ),
        )
        self.assertEqual(
            1,
            self.env["automation.record.step"].search_count(
                [
                    ("configuration_step_id", "=", activity_1_1.id),
                    ("record_id.res_id", "=", self.partner_02.id),
                ]
            ),
        )
        self.assertEqual(
            1,
            self.env["automation.record.step"].search_count(
                [
                    ("configuration_step_id", "=", activity_1_2.id),
                    ("record_id.res_id", "=", self.partner_02.id),
                ]
            ),
        )
        self.assertEqual(
            0,
            self.env["automation.record.step"].search_count(
                [
                    (
                        "configuration_step_id",
                        "in",
                        (activity_1_1_1 | activity_1_2_1).ids,
                    )
                ]
            ),
        )
        self.env["automation.record.step"]._cron_automation_steps()
        self.assertEqual(
            1,
            self.env["automation.record.step"].search_count(
                [
                    ("configuration_step_id", "=", activity_1_1.id),
                    ("record_id.res_id", "=", self.partner_01.id),
                    ("state", "=", "done"),
                ]
            ),
        )
        self.assertEqual(
            1,
            self.env["automation.record.step"].search_count(
                [
                    ("configuration_step_id", "=", activity_1_2.id),
                    ("record_id.res_id", "=", self.partner_01.id),
                    ("state", "=", "rejected"),
                ]
            ),
        )
        self.assertEqual(
            1,
            self.env["automation.record.step"].search_count(
                [
                    ("configuration_step_id", "=", activity_1_1.id),
                    ("record_id.res_id", "=", self.partner_02.id),
                    ("state", "=", "rejected"),
                ]
            ),
        )
        self.assertEqual(
            1,
            self.env["automation.record.step"].search_count(
                [
                    ("configuration_step_id", "=", activity_1_2.id),
                    ("record_id.res_id", "=", self.partner_02.id),
                    ("state", "=", "done"),
                ]
            ),
        )
        self.assertEqual(
            1,
            self.env["automation.record.step"].search_count(
                [
                    ("configuration_step_id", "=", activity_1_1_1.id),
                    ("record_id.res_id", "=", self.partner_01.id),
                ]
            ),
        )
        self.assertEqual(
            0,
            self.env["automation.record.step"].search_count(
                [
                    ("configuration_step_id", "=", activity_1_2_1.id),
                    ("record_id.res_id", "=", self.partner_01.id),
                ]
            ),
        )
        self.assertEqual(
            0,
            self.env["automation.record.step"].search_count(
                [
                    ("configuration_step_id", "=", activity_1_1_1.id),
                    ("record_id.res_id", "=", self.partner_02.id),
                ]
            ),
        )
        self.assertEqual(
            1,
            self.env["automation.record.step"].search_count(
                [
                    ("configuration_step_id", "=", activity_1_2_1.id),
                    ("record_id.res_id", "=", self.partner_02.id),
                ]
            ),
        )

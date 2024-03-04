# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from freezegun import freeze_time

from odoo.exceptions import ValidationError
from odoo.tests import Form
from odoo.tools.safe_eval import safe_eval

from .common import AutomationTestCase


class TestAutomationBase(AutomationTestCase):
    def test_no_cron_no_start(self):
        """
        We want to check that the system only generates on periodical configurations
        """
        self.env["automation.configuration"].cron_automation()
        self.assertEqual(
            0,
            self.env["automation.record"].search_count(
                [("configuration_id", "=", self.configuration.id)]
            ),
        )
        self.configuration.run_automation()
        self.assertEqual(
            0,
            self.env["automation.record"].search_count(
                [("configuration_id", "=", self.configuration.id)]
            ),
        )

    def test_no_cron_on_demand(self):
        """
        We want to check that the system does not generate using cron
        on on demand configurations, but allows manuall execution
        """
        self.configuration.is_periodic = False
        self.configuration.start_automation()
        self.env["automation.configuration"].cron_automation()
        self.assertEqual(
            0,
            self.env["automation.record"].search_count(
                [("configuration_id", "=", self.configuration.id)]
            ),
        )
        self.configuration.run_automation()
        self.assertNotEqual(
            0,
            self.env["automation.record"].search_count(
                [("configuration_id", "=", self.configuration.id)]
            ),
        )

    def test_next_execution_date(self):
        with freeze_time("2022-01-01"):
            self.assertFalse(self.configuration.next_execution_date)
            self.env.ref(
                "automation_oca.cron_configuration_run"
            ).nextcall = datetime.now()
            self.configuration.start_automation()
            self.assertEqual(
                self.configuration.next_execution_date, datetime(2022, 1, 1, 0, 0, 0)
            )

    def test_cron_no_duplicates(self):
        """
        We want to check that the records are generated only once, not twice
        """
        self.create_server_action()
        self.configuration.start_automation()
        self.env["automation.configuration"].cron_automation()
        record = self.env["automation.record"].search(
            [
                ("configuration_id", "=", self.configuration.id),
                ("res_id", "=", self.partner_01.id),
            ]
        )
        self.assertEqual(
            1,
            self.env["automation.record"].search_count(
                [
                    ("configuration_id", "=", self.configuration.id),
                    ("res_id", "=", self.partner_01.id),
                ]
            ),
        )
        self.assertEqual(
            1,
            self.env["automation.record"].search_count(
                [
                    ("configuration_id", "=", self.configuration.id),
                    ("res_id", "=", self.partner_02.id),
                ]
            ),
        )

        self.env["automation.configuration"].cron_automation()
        self.assertEqual(
            1,
            self.env["automation.record"].search_count(
                [
                    ("configuration_id", "=", self.configuration.id),
                    ("res_id", "=", self.partner_01.id),
                ]
            ),
        )
        self.assertEqual(
            1,
            self.env["automation.record"].search_count(
                [
                    ("configuration_id", "=", self.configuration.id),
                    ("res_id", "=", self.partner_02.id),
                ]
            ),
        )
        record = self.env["automation.record"].search(
            [
                ("configuration_id", "=", self.configuration.id),
                ("res_id", "=", self.partner_01.id),
            ]
        )
        self.assertEqual(
            1,
            self.env["automation.record.step"].search_count(
                [("record_id", "=", record.id)]
            ),
        )

    def test_filter(self):
        """
        We want to see that the records are only generated for
        the records that fulfill the domain
        """
        self.create_server_action()
        self.configuration.editable_domain = "[('id', '=', %s)]" % self.partner_01.id
        self.configuration.start_automation()
        self.env["automation.configuration"].cron_automation()
        self.assertEqual(
            1,
            self.env["automation.record"].search_count(
                [
                    ("configuration_id", "=", self.configuration.id),
                    ("res_id", "=", self.partner_01.id),
                ]
            ),
        )
        self.assertEqual(
            0,
            self.env["automation.record"].search_count(
                [
                    ("configuration_id", "=", self.configuration.id),
                    ("res_id", "=", self.partner_02.id),
                ]
            ),
        )

    def test_exception(self):
        """
        Check that the error is raised properly and stored the full error
        """
        activity = self.create_server_action(server_action_id=self.error_action.id)
        self.configuration.editable_domain = "[('id', '=', %s)]" % self.partner_01.id
        self.configuration.start_automation()
        self.env["automation.configuration"].cron_automation()
        record = self.env["automation.record.step"].search(
            [("configuration_step_id", "=", activity.id)]
        )
        self.assertFalse(record.error_trace)
        self.env["automation.record.step"]._cron_automation_steps()
        self.assertEqual(record.state, "error")
        self.assertTrue(record.error_trace)

    def test_record_resource_information(self):
        """
        Check the record computed fields of record
        """
        self.create_server_action(server_action_id=self.error_action.id)
        self.configuration.editable_domain = "[('id', '=', %s)]" % self.partner_01.id
        self.configuration.start_automation()
        self.env["automation.configuration"].cron_automation()
        record = self.env["automation.record"].search(
            [("configuration_id", "=", self.configuration.id)]
        )
        self.assertEqual(self.partner_01.display_name, record.display_name)
        self.assertEqual(self.partner_01, record.resource_ref)
        record.model = "unexistent.model"
        self.assertFalse(record.resource_ref)

    def test_expiry(self):
        """
        Testing that expired actions are not executed
        """
        activity = self.create_server_action(expiry=True, trigger_interval=1)
        self.configuration.editable_domain = "[('id', '=', %s)]" % self.partner_01.id
        self.configuration.start_automation()
        self.env["automation.configuration"].cron_automation()
        record_activity = self.env["automation.record.step"].search(
            [("configuration_step_id", "=", activity.id)]
        )
        self.assertEqual("scheduled", record_activity.state)
        self.env["automation.record.step"]._cron_automation_steps()
        self.assertEqual("expired", record_activity.state)

    def test_cancel(self):
        """
        Testing that cancelled actions are not executed
        """
        activity = self.create_server_action()
        self.configuration.editable_domain = "[('id', '=', %s)]" % self.partner_01.id
        self.configuration.start_automation()
        self.env["automation.configuration"].cron_automation()
        record_activity = self.env["automation.record.step"].search(
            [("configuration_step_id", "=", activity.id)]
        )
        self.assertEqual("scheduled", record_activity.state)
        record_activity.cancel()
        self.assertEqual("cancel", record_activity.state)
        self.env["automation.record.step"]._cron_automation_steps()
        self.assertEqual("cancel", record_activity.state)

    def test_counter(self):
        """
        Check the counter function
        """
        self.create_server_action(server_action_id=self.error_action.id)
        self.configuration.editable_domain = "[('id', '=', %s)]" % self.partner_01.id
        self.configuration.start_automation()
        self.assertEqual(0, self.configuration.record_count)
        self.assertEqual(0, self.configuration.record_test_count)
        self.env["automation.configuration"].cron_automation()
        self.configuration.invalidate_recordset()
        self.assertEqual(1, self.configuration.record_count)
        self.assertEqual(0, self.configuration.record_test_count)

    def test_start_configuration_twice_exception(self):
        """
        Check that we cannot start automation twice
        """
        self.configuration.start_automation()
        with self.assertRaises(ValidationError):
            self.configuration.start_automation()

    def test_state_automation_management(self):
        """
        Testing the change of state
        Draft -> Run -> Stop -> Draft
        """
        self.configuration.start_automation()
        self.assertEqual(self.configuration.state, "periodic")
        self.configuration.done_automation()
        self.assertEqual(self.configuration.state, "done")
        self.env["automation.configuration"].cron_automation()
        self.assertFalse(
            self.env["automation.record"].search(
                [
                    ("configuration_id", "=", self.configuration.id),
                ]
            )
        )
        self.configuration.back_to_draft()
        self.assertEqual(self.configuration.state, "draft")

    def test_graph(self):
        """
        Checking the graph results.
        We will use 2 parent actions (1 will fail) and a child action of the one ok.
        After 2 executions, we should have (1 OK, 0 Errors) for parent and child and
        (0 OK, 1 Error) for the failing one.
        """
        activity_01 = self.create_server_action()
        activity_02 = self.create_server_action(server_action_id=self.error_action.id)
        activity_03 = self.create_mail_activity()
        child_activity = self.create_server_action(parent_id=activity_01.id)
        self.configuration.editable_domain = "[('id', '=', %s)]" % self.partner_01.id
        self.configuration.start_automation()
        self.env["automation.configuration"].cron_automation()
        self.assertEqual(0, self.configuration.activity_mail_count)
        self.assertEqual(0, self.configuration.activity_action_count)
        self.assertEqual(0, activity_01.graph_done)
        self.assertEqual(0, activity_01.graph_error)
        self.assertEqual(0, sum(d["y"] for d in activity_01.graph_data["done"]))
        self.assertEqual(0, sum(d["y"] for d in activity_01.graph_data["error"]))
        self.assertEqual(0, activity_02.graph_done)
        self.assertEqual(0, activity_02.graph_error)
        self.assertEqual(0, sum(d["y"] for d in activity_02.graph_data["done"]))
        self.assertEqual(0, sum(d["y"] for d in activity_02.graph_data["error"]))
        self.assertEqual(0, activity_03.graph_done)
        self.assertEqual(0, activity_03.graph_error)
        self.assertEqual(0, sum(d["y"] for d in activity_03.graph_data["done"]))
        self.assertEqual(0, sum(d["y"] for d in activity_03.graph_data["error"]))
        self.assertEqual(0, child_activity.graph_done)
        self.assertEqual(0, child_activity.graph_error)
        self.assertEqual(0, sum(d["y"] for d in child_activity.graph_data["done"]))
        self.assertEqual(0, sum(d["y"] for d in child_activity.graph_data["error"]))
        self.env["automation.record.step"]._cron_automation_steps()
        self.configuration.invalidate_recordset()
        self.assertEqual(1, self.configuration.activity_mail_count)
        self.assertEqual(1, self.configuration.activity_action_count)
        activity_01.invalidate_recordset()
        self.assertEqual(1, activity_01.graph_done)
        self.assertEqual(0, activity_01.graph_error)
        self.assertEqual(1, sum(d["y"] for d in activity_01.graph_data["done"]))
        self.assertEqual(0, sum(d["y"] for d in activity_01.graph_data["error"]))
        activity_02.invalidate_recordset()
        self.assertEqual(0, activity_02.graph_done)
        self.assertEqual(1, activity_02.graph_error)
        self.assertEqual(0, sum(d["y"] for d in activity_02.graph_data["done"]))
        self.assertEqual(1, sum(d["y"] for d in activity_02.graph_data["error"]))
        activity_03.invalidate_recordset()
        self.assertEqual(1, activity_03.graph_done)
        self.assertEqual(0, activity_03.graph_error)
        self.assertEqual(1, sum(d["y"] for d in activity_03.graph_data["done"]))
        self.assertEqual(0, sum(d["y"] for d in activity_03.graph_data["error"]))
        child_activity.invalidate_recordset()
        self.assertEqual(0, child_activity.graph_done)
        self.assertEqual(0, child_activity.graph_error)
        self.assertEqual(0, sum(d["y"] for d in child_activity.graph_data["done"]))
        self.assertEqual(0, sum(d["y"] for d in child_activity.graph_data["error"]))
        self.env["automation.record.step"]._cron_automation_steps()
        self.configuration.invalidate_recordset()
        self.assertEqual(1, self.configuration.activity_mail_count)
        self.assertEqual(2, self.configuration.activity_action_count)
        activity_01.invalidate_recordset()
        self.assertEqual(1, activity_01.graph_done)
        self.assertEqual(0, activity_01.graph_error)
        self.assertEqual(1, sum(d["y"] for d in activity_01.graph_data["done"]))
        self.assertEqual(0, sum(d["y"] for d in activity_01.graph_data["error"]))
        activity_02.invalidate_recordset()
        self.assertEqual(0, activity_02.graph_done)
        self.assertEqual(1, activity_02.graph_error)
        self.assertEqual(0, sum(d["y"] for d in activity_02.graph_data["done"]))
        self.assertEqual(1, sum(d["y"] for d in activity_02.graph_data["error"]))
        activity_03.invalidate_recordset()
        self.assertEqual(1, activity_03.graph_done)
        self.assertEqual(0, activity_03.graph_error)
        self.assertEqual(1, sum(d["y"] for d in activity_03.graph_data["done"]))
        self.assertEqual(0, sum(d["y"] for d in activity_03.graph_data["error"]))
        child_activity.invalidate_recordset()
        self.assertEqual(1, child_activity.graph_done)
        self.assertEqual(0, child_activity.graph_error)
        self.assertEqual(1, sum(d["y"] for d in child_activity.graph_data["done"]))
        self.assertEqual(0, sum(d["y"] for d in child_activity.graph_data["error"]))

    def test_schedule_date_computation_hours(self):
        with freeze_time("2022-01-01"):
            activity = self.create_server_action(trigger_interval=1)
            self.assertEqual(1, activity.trigger_interval_hours)
            self.configuration.editable_domain = (
                "[('id', '=', %s)]" % self.partner_01.id
            )
            self.configuration.start_automation()
            self.env["automation.configuration"].cron_automation()
            record_activity = self.env["automation.record.step"].search(
                [("configuration_step_id", "=", activity.id)]
            )
            self.assertEqual("scheduled", record_activity.state)
            self.assertEqual(
                record_activity.scheduled_date, datetime(2022, 1, 1, 1, 0, 0, 0)
            )

    def test_schedule_date_computation_days(self):
        with freeze_time("2022-01-01"):
            activity = self.create_server_action(
                trigger_interval=1, trigger_interval_type="days"
            )
            self.assertEqual(24, activity.trigger_interval_hours)
            self.configuration.editable_domain = (
                "[('id', '=', %s)]" % self.partner_01.id
            )
            self.configuration.start_automation()
            self.env["automation.configuration"].cron_automation()
            record_activity = self.env["automation.record.step"].search(
                [("configuration_step_id", "=", activity.id)]
            )
            self.assertEqual("scheduled", record_activity.state)
            self.assertEqual(
                record_activity.scheduled_date, datetime(2022, 1, 2, 0, 0, 0, 0)
            )

    def test_onchange_activity_trigger_type(self):
        activity = self.create_mail_activity()
        child_activity = self.create_mail_activity(parent_id=activity.id)
        self.assertEqual(child_activity.trigger_type, "after_step")
        self.assertTrue(child_activity.parent_id)
        with Form(child_activity) as f:
            f.trigger_type = "mail_bounce"
            self.assertTrue(f.parent_id)

    def test_onchange_activity_trigger_type_start(self):
        activity = self.create_server_action()
        child_activity = self.create_server_action(parent_id=activity.id)
        self.assertEqual(child_activity.trigger_type, "after_step")
        self.assertTrue(child_activity.parent_id)
        with Form(child_activity) as f:
            f.trigger_type = "start"
            self.assertFalse(f.parent_id)

    def test_field_not_field_unicity(self):
        self.configuration.editable_domain = (
            "[('id', 'in', %s)]" % (self.partner_01 | self.partner_02).ids
        )
        self.configuration.start_automation()
        self.env["automation.configuration"].cron_automation()
        self.assertEqual(
            2,
            len(
                self.env["automation.record"].search(
                    [("configuration_id", "=", self.configuration.id)]
                )
            ),
        )

    def test_field_field_unicity(self):
        self.configuration.editable_domain = (
            "[('id', 'in', %s)]" % (self.partner_01 | self.partner_02).ids
        )
        self.configuration.field_id = self.env.ref("base.field_res_partner__email")
        self.configuration.start_automation()
        self.env["automation.configuration"].cron_automation()
        self.assertEqual(
            1,
            len(
                self.env["automation.record"].search(
                    [("configuration_id", "=", self.configuration.id)]
                )
            ),
        )
        self.partner_01.email = "t" + self.partner_01.email
        self.env["automation.configuration"].cron_automation()
        self.assertEqual(
            2,
            len(
                self.env["automation.record"].search(
                    [("configuration_id", "=", self.configuration.id)]
                )
            ),
        )

    def test_configuration_filter_domain(self):
        domain = [("partner_id", "=", self.partner_01.id)]
        self.assertFalse(self.configuration.filter_id)
        self.configuration.editable_domain = domain
        self.configuration.save_filter()
        self.assertTrue(self.configuration.filter_id)
        self.assertEqual(self.configuration.model_id, self.configuration.model_id)
        domain = [("partner_id", "=", self.partner_02.id)]
        self.configuration.invalidate_recordset()
        self.assertNotEqual(domain, safe_eval(self.configuration.domain))
        self.configuration.filter_id.domain = domain
        self.assertEqual(domain, safe_eval(self.configuration.domain))
        with Form(self.env["automation.configuration"]) as f:
            self.assertFalse(f.filter_domain)
            f.name = "My other configuration"
            f.filter_id = self.configuration.filter_id
            self.assertEqual(f.model_id, self.env.ref("base.model_res_partner"))
            self.assertIn(
                self.configuration.filter_id,
                self.env["automation.filter"].search(f.filter_domain),
            )
            f.model_id = self.env.ref("base.model_res_users")
            self.assertFalse(f.filter_id)

    def test_filter_onchange(self):
        with Form(self.env["automation.filter"]) as f:
            f.name = "My other configuration"
            f.model_id = self.env.ref("base.model_res_partner")
            f.domain = [("id", "=", 1)]
            f.model_id = self.env.ref("base.model_res_users")
            self.assertFalse(safe_eval(f.domain))

    def test_constrains_mail(self):
        activity = self.create_server_action()
        with self.assertRaises(ValidationError):
            self.create_server_action(parent_id=activity.id, trigger_type="mail_bounce")

    def test_constrains_start_with_parent(self):
        activity = self.create_server_action()
        with self.assertRaises(ValidationError):
            self.create_server_action(parent_id=activity.id, trigger_type="start")

    def test_constrains_no_start_without_parent(self):
        with self.assertRaises(ValidationError):
            self.create_server_action(parent_id=False, trigger_type="after_step")

    def test_is_test_behavior(self):
        """
        We want to ensure that no mails are sent on tests
        """
        self.create_server_action()
        with Form(
            self.env["automation.configuration.test"].with_context(
                default_configuration_id=self.configuration.id,
                defaul_model=self.configuration.model,
            )
        ) as f:
            self.assertTrue(f.resource_ref)
            f.resource_ref = "%s,%s" % (self.partner_01._name, self.partner_01.id)
        wizard = f.save()
        wizard_action = wizard.test_record()
        record = self.env[wizard_action["res_model"]].browse(wizard_action["res_id"])
        self.assertEqual(self.configuration, record.configuration_id)
        self.assertEqual(1, self.configuration.record_test_count)
        self.assertEqual(0, self.configuration.record_count)

    def test_check_icons(self):
        action = self.create_server_action()
        mail = self.create_mail_activity()
        activity = self.create_activity_action()
        self.assertEqual(action.step_icon, "fa fa-cogs")
        self.assertEqual(mail.step_icon, "fa fa-envelope")
        self.assertEqual(activity.step_icon, "fa fa-clock-o")

    def test_trigger_types(self):
        action = self.create_server_action()
        child = self.create_server_action(parent_id=action.id)
        self.assertTrue(action.trigger_type_data["allow_parent"])
        self.assertFalse(child.trigger_type_data.get("allow_parent", False))

    def test_trigger_childs(self):
        action = self.create_server_action()
        mail = self.create_mail_activity()
        activity = self.create_activity_action()
        self.assertEqual(1, len(action.trigger_child_types))
        self.assertEqual({"after_step"}, set(action.trigger_child_types.keys()))
        self.assertEqual(8, len(mail.trigger_child_types))
        self.assertEqual(
            {
                "after_step",
                "mail_open",
                "mail_not_open",
                "mail_reply",
                "mail_not_reply",
                "mail_click",
                "mail_not_clicked",
                "mail_bounce",
            },
            set(mail.trigger_child_types.keys()),
        )
        self.assertEqual(3, len(activity.trigger_child_types))
        self.assertEqual(
            {"after_step", "activity_done", "activity_not_done"},
            set(activity.trigger_child_types.keys()),
        )

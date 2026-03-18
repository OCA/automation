# Copyright 2026 ForgeFlow
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.automation_oca.tests.common import AutomationTestCase


class TestAutomationActivityNoteTemplate(AutomationTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.note_template = cls.env["mail.template"].create(
            {
                "name": "Activity note template",
                "model_id": cls.env.ref("base.model_res_partner").id,
                "subject": "Follow up with {{ object.name }}",
                "body_html": "<p>Contact: {{ object.name }}</p>",
            }
        )

    def _run_automation(self, domain):
        self.configuration.editable_domain = domain
        self.configuration.start_automation()
        self.env["automation.configuration"].cron_automation()
        self.env["automation.record.step"]._cron_automation_steps()

    def test_summary_and_note_rendered_from_template(self):
        """Both subject and body_html of the template are rendered into summary and note."""
        activity = self.create_activity_action(
            activity_note_template_id=self.note_template.id,
        )
        self._run_automation(f"[('id', '=', {self.partner_01.id})]")
        self.assertTrue(self.partner_01.activity_ids)
        act = self.partner_01.activity_ids
        self.assertIn(self.partner_01.name, act.summary)
        self.assertIn(self.partner_01.name, act.note)
        activity.unlink()

    def test_static_note_without_template(self):
        """Without a note template, static activity_note is used unchanged."""
        activity = self.create_activity_action(
            activity_note="<p>Static note</p>",
        )
        self._run_automation(f"[('id', '=', {self.partner_01.id})]")
        self.assertTrue(self.partner_01.activity_ids)
        self.assertEqual(self.partner_01.activity_ids.note, "<p>Static note</p>")
        activity.unlink()

    def test_note_rendered_from_template(self):
        """When a note template is set, body_html is rendered against the record."""
        activity = self.create_activity_action(
            activity_note_template_id=self.note_template.id,
        )
        self._run_automation(f"[('id', '=', {self.partner_01.id})]")
        self.assertTrue(self.partner_01.activity_ids)
        self.assertIn(self.partner_01.name, self.partner_01.activity_ids.note)
        activity.unlink()

    def test_template_overrides_static_note(self):
        """When both note template and static note are set, template takes precedence."""
        activity = self.create_activity_action(
            activity_note="<p>Static note</p>",
            activity_note_template_id=self.note_template.id,
        )
        self._run_automation(f"[('id', '=', {self.partner_01.id})]")
        self.assertTrue(self.partner_01.activity_ids)
        note = self.partner_01.activity_ids.note
        self.assertIn(self.partner_01.name, note)
        self.assertNotIn("Static note", note)
        activity.unlink()

    def test_note_rendered_per_record(self):
        """Template is rendered individually for each record."""
        activity = self.create_activity_action(
            activity_note_template_id=self.note_template.id,
        )
        self._run_automation(
            f"[('id', 'in', [{self.partner_01.id}, {self.partner_02.id}])]"
        )
        self.assertTrue(self.partner_01.activity_ids)
        self.assertTrue(self.partner_02.activity_ids)
        note_01 = self.partner_01.activity_ids.note
        note_02 = self.partner_02.activity_ids.note
        self.assertIn(self.partner_01.name, note_01)
        self.assertIn(self.partner_02.name, note_02)
        self.assertNotEqual(note_01, note_02)
        self.assertNotIn(self.partner_02.name, note_01)
        activity.unlink()

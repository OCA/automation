# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from freezegun import freeze_time

from odoo.orm.model_classes import add_to_registry
from odoo.orm.models import MetaModel

from .common import AutomationTestCase


class TestAutomationDate(AutomationTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from .models import ResPartner

        original_bases = cls.registry["res.partner"]._base_classes__

        def _restore():
            cls.registry["res.partner"]._base_classes__ = original_bases
            MetaModel._module_to_models__[ResPartner._module].remove(ResPartner)

        cls.addClassCleanup(_restore)
        cls.env.invalidate_all()
        add_to_registry(cls.registry, ResPartner)
        cls.registry._setup_models__(cls.env.cr, ["res.partner"])
        cls.registry.init_models(cls.env.cr, ["res.partner"], {"models_to_check": True})

    def test_schedule_date_force(self):
        partner_01 = self.env["res.partner"].create(
            {
                "name": "Demo partner",
                "comment": "Demo",
                "email": "test@test.com",
                "date": "2025-01-01",
            }
        )
        with freeze_time("2024-01-01 00:00:00"):
            activity = self.create_server_action(
                trigger_date_kind="date",
                trigger_date_field_id=self.env["ir.model.fields"]
                .search(
                    [
                        ("name", "=", "date"),
                        ("model", "=", "res.partner"),
                    ]
                )
                .id,
                trigger_interval=1,
                trigger_interval_type="days",
            )
            self.configuration.editable_domain = f"[('id', '=', {partner_01.id})]"
            self.configuration.start_automation()
            self.env["automation.configuration"].cron_automation()
            record_activity = self.env["automation.record.step"].search(
                [("configuration_step_id", "=", activity.id)]
            )
            self.assertEqual("scheduled", record_activity.state)
            self.assertEqual(record_activity.scheduled_date, datetime(2025, 1, 2))

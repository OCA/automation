# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import unittest
from datetime import datetime

from freezegun import freeze_time

from .common import AutomationTestCase

try:
    from odoo_test_helper import FakeModelLoader

    _HAS_FAKE_MODEL_LOADER = True
except (ImportError, AttributeError):
    # odoo-test-helper (<= 2.1.3) is not compatible with Odoo 19 yet: at import
    # time it reads ``MetaModel.module_to_models`` (renamed to
    # ``_module_to_models__`` in 19.0) and internally it drives the registry via
    # the old ``Registry.load(cr, package)`` / ``setup_models`` API, both changed
    # in 19.0. We skip this single date-trigger test until the helper is ported.
    FakeModelLoader = None
    _HAS_FAKE_MODEL_LOADER = False


@unittest.skipUnless(
    _HAS_FAKE_MODEL_LOADER, "odoo-test-helper is not compatible with Odoo 19 yet"
)
class TestAutomationDate(AutomationTestCase):
    def setUp(self):
        super().setUp()
        self.loader = FakeModelLoader(self.env, self.__module__)
        self.loader.backup_registry()

        # The fake class is imported here !! After the backup_registry
        from .models import ResPartner

        self.loader.update_registry((ResPartner,))

    def tearDown(self):
        self.loader.restore_registry()
        return super().tearDown()

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

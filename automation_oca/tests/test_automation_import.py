# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64
import json

from .common import AutomationTestCase


class TestAutomationBase(AutomationTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Adding two languages to test the import and export of automations
        cls.env["base.language.install"].create(
            {
                "overwrite": True,
                "lang_ids": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref("base.lang_es").id,
                            cls.env.ref("base.lang_fr").id,
                        ],
                    )
                ],
            }
        ).lang_install()
        cls.create_server_action()
        cls.create_activity_action()
        cls.create_mail_activity()
        cls.action.with_context(lang="en_US").name = "Test Automation Configuration"
        cls.action.with_context(
            lang="es_ES"
        ).name = "Configuración de Automatización de Prueba"
        cls.action.with_context(
            lang="fr_FR"
        ).name = "Configuration d'Automatisation de Test"

    def test_export_automation(self):
        action = self.configuration.export_configuration()
        wizard = self.env[action["res_model"]].browse(action["res_id"])
        file = wizard.file_content
        data = json.loads(base64.b64decode(file))
        action_id = self.action.get_external_id()[self.action.id]
        self.assertEqual(
            data["server_actions"][action_id]["name"]["en_US"],
            "Test Automation Configuration",
        )
        self.assertEqual(
            data["server_actions"][action_id]["name"]["es_ES"],
            "Configuración de Automatización de Prueba",
        )
        self.assertEqual(
            data["server_actions"][action_id]["name"]["fr_FR"],
            "Configuration d'Automatisation de Test",
        )

    def test_import_automation_creation_copy(self):
        action = self.configuration.export_configuration()
        wizard = self.env[action["res_model"]].browse(action["res_id"])
        file = wizard.file_content
        self.action.name = "Test Automation Configuration changed"
        record_action = self.env[
            "automation.configuration"
        ].create_document_from_attachment(file)
        configuration = self.env[record_action["res_model"]].browse(
            record_action["res_id"]
        )
        self.assertEqual(configuration.name, self.configuration.name)
        self.assertEqual(3, len(configuration.automation_step_ids))
        self.assertEqual(
            self.action,
            configuration.automation_step_ids.filtered(
                lambda r: r.server_action_id
            ).server_action_id,
        )
        self.assertEqual(
            self.template,
            configuration.automation_step_ids.filtered(
                lambda r: r.mail_template_id
            ).mail_template_id,
        )
        self.assertEqual(
            self.activity_type,
            configuration.automation_step_ids.filtered(
                lambda r: r.activity_type_id
            ).activity_type_id,
        )
        self.assertEqual(self.action.name, "Test Automation Configuration changed")

    def test_import_automation_creation_creation(self):
        action = self.configuration.export_configuration()
        wizard = self.env[action["res_model"]].browse(action["res_id"])
        file = wizard.file_content
        self.configuration.automation_step_ids.unlink()
        original_action_id = self.action.id
        self.action.unlink()
        self.template.unlink()
        self.activity_type.unlink()
        record_action = self.env[
            "automation.configuration"
        ].create_document_from_attachment(file)
        configuration = self.env[record_action["res_model"]].browse(
            record_action["res_id"]
        )
        self.assertEqual(configuration.name, self.configuration.name)
        self.assertEqual(3, len(configuration.automation_step_ids))
        action = configuration.automation_step_ids.filtered(
            lambda r: r.server_action_id
        ).server_action_id
        self.assertNotEqual(original_action_id, action.id)
        self.assertEqual(
            action.with_context(lang="en_US").name, "Test Automation Configuration"
        )
        self.assertEqual(
            action.with_context(lang="es_ES").name,
            "Configuración de Automatización de Prueba",
        )
        self.assertEqual(
            action.with_context(lang="fr_FR").name,
            "Configuration d'Automatisation de Test",
        )

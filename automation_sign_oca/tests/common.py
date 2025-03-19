# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo.modules.module import get_module_resource

from odoo.addons.automation_oca.tests.common import AutomationTestCase


class AutomationSignTestCase(AutomationTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.data = base64.b64encode(
            open(
                get_module_resource("sign_oca", "tests", "empty.pdf"),
                "rb",
            ).read()
        )
        cls.sign_template = cls.env["sign.oca.template"].create(
            {
                "data": cls.data,
                "name": "Demo template",
                "filename": "empty.pdf",
            }
        )
        cls.sign_template.add_item(
            {
                "field_id": cls.env.ref("sign_oca.sign_field_name").id,
                "page": 1,
                "position_x": 10,
                "position_y": 10,
                "width": 10,
                "height": 10,
                "required": True,
            }
        )

    @classmethod
    def create_sign_action(cls, parent_id=False, **kwargs):
        return cls.env["automation.configuration.step"].create(
            {
                "name": "Demo Sign Activity",
                "parent_id": parent_id,
                "configuration_id": cls.configuration.id,
                "step_type": "sign",
                "sign_template_id": cls.sign_template.id,
                "trigger_type": "after_step" if parent_id else "start",
                **kwargs,
            }
        )

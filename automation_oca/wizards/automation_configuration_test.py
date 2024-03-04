# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AutomationConfigurationTest(models.TransientModel):

    _name = "automation.configuration.test"
    _description = "Test automation configuration"

    configuration_id = fields.Many2one("automation.configuration", required=True)
    model = fields.Char(related="configuration_id.model")
    resource_ref = fields.Reference(
        selection="_selection_target_model",
        readonly=False,
        required=True,
        store=True,
        compute="_compute_resource_ref",
    )

    @api.model
    def _selection_target_model(self):
        return [
            (model.model, model.name)
            for model in self.env["ir.model"]
            .sudo()
            .search([("is_mail_thread", "=", True)])
        ]

    @api.depends("model")
    def _compute_resource_ref(self):
        for record in self:
            if record.model and record.model in self.env:
                res = self.env[record.model].search([], limit=1)
                record.resource_ref = "%s,%s" % (record.model, res.id)
            else:
                record.resource_ref = None

    def test_record(self):
        return self.configuration_id._create_record(
            self.resource_ref, is_test=True
        ).get_formview_action()

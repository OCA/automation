# Copyright 2024 KEE
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3).

from odoo import fields, models


class IaExecution(models.Model):

    _name = "ai.execution"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "ai Process"

    name = fields.Char(
        states={"done": [("readonly", True)], "error": [("readonly", True)]}
    )
    crew_id = fields.Many2one(
        "ai.crew",
        required=True,
        states={"done": [("readonly", True)], "error": [("readonly", True)]},
    )
    agent_ids = fields.Many2many(related="crew_id.agent_ids", readonly=True)
    task_ids = fields.One2many(related="crew_id.task_ids", readonly=True)
    execution_data_ids = fields.One2many(
        "ai.execution.data",
        "execution_id",
        string="Execution Data",
        states={"done": [("readonly", True)], "error": [("readonly", True)]},
        copy=True,
    )
    execution_result = fields.Text(readonly=True, copy=False)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("running", "Running"),
            ("done", "Done"),
            ("error", "Error"),
        ],
        default="draft",
        required=True,
    )

    def _kickoff(self):
        for record in self:
            crew = record.crew_id.crew()
            inputs = {data.key: data.value for data in record.execution_data_ids}
            result = crew.kickoff(inputs=inputs)
            record.write(
                {
                    "execution_result": result,
                    "state": "done",
                }
            )

    def action_confirm(self):
        for record in self:
            record.write(
                {
                    "state": "running",
                }
            )
            record.with_delay(channel="root.ai")._kickoff()
        return True

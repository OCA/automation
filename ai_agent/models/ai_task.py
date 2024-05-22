# Copyright 2024 KMEE
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3).

from crewai import Task

from odoo import fields, models


class IaTask(models.Model):

    _name = "ai.task"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Task"

    name = fields.Char(required=True)
    description = fields.Text(
        help="""Description
        A clear, concise statement of what the task entails.""",
        required=True,
    )
    agent_id = fields.Many2one(
        comodel_name="ai.agent",
        help="""Agent Optionally, you can specify which agent is
         responsible for the task. If not,
         the crew's process will determine who takes it on.""",
    )
    expected_output = fields.Text(
        help="""Expected Output
        Clear and detailed definition of expected output for the task.""",
    )
    tool_ids = fields.Many2many(
        comodel_name="ai.tool",
        string="Tools",
        help="""Tools
        These are the functions or capabilities the agent can utilize to
        perform the task.
         They can be anything from simple actions like 'search' to more
         complex interactions with other agents or APIs.""",
    )
    async_execution = fields.Boolean(
        help="""Async Execution
        Indicates whether the task should be executed asynchronously,
         allowing the crew to continue with the next task without waiting
          for completion.""",
    )
    context = fields.Many2many(
        comodel_name="ai.task",
        relation="ia_task_context_rel",
        column1="task_id",
        column2="context_id",
        help="""Context
        Other tasks that will have their output used as context for this task.
        If a task is asynchronous, the system will wait for that to
        finish before using its output as context.""",
    )
    output_json = fields.Text(
        help="""Output JSON
        Takes a pydantic model and returns the output as a JSON object.
        Agent LLM needs to be using an OpenAI client,
        could be Ollama for example but using the OpenAI wrapper""",
    )
    output_pydantic = fields.Text(
        help="""Output Pydantic
        Takes a pydantic model and returns the output as a pydantic object.
         Agent LLM needs to be using an OpenAI client,
         could be Ollama for example but using the OpenAI wrapper""",
    )
    output_file = fields.Text(
        help="""Output File
        Takes a file path and saves the output of the task on it.""",
    )
    callback = fields.Text(
        help="""Callback
        A function to be executed after the task is completed.""",
    )

    crew_id = fields.Many2one("ai.crew", string="Crew", ondelete="cascade")

    def task(self):
        """
        Create a new Task object with the provided description,
         expected output, agent, and tools.

        Returns:
            Task: The newly created Task object.
        """
        task = Task(
            description=self.description,
            expected_output=self.expected_output,
            agent=self.agent_id.agent() if self.agent_id else None,
            tools=[t.tool() for t in self.tool_ids],
            async_execution=self.async_execution,
            # output_file=self.output_file,
        )
        return task

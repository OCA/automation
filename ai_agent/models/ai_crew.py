# Copyright 2024 KMEE
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3).

from crewai import Crew, Process

from odoo import fields, models


class IaCrews(models.Model):

    _name = "ai.crew"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "ai Crews"

    name = fields.Char(required=True)
    task_ids = fields.One2many(
        comodel_name="ai.task",
        inverse_name="crew_id",
        required=True,
        help="""A list of tasks assigned to the crew.""",
    )
    agent_ids = fields.Many2many(
        comodel_name="ai.agent",
        relation="ia_crew_agent_rel",
        column1="crew_id",
        column2="agent_id",
        required=True,
        help="""A list of agents that are part of the crew.""",
    )
    process = fields.Selection(
        [("sequential", "Sequential"), ("hierarchical", "Hierarchical")],
        default="sequential",
        required=True,
        help="""The process flow (e.g., sequential, hierarchical) the cr follows.""",
    )
    verbose = fields.Boolean(
        help="""The verbosity level for logging during execution.""",
    )
    manager_llm_id = fields.Many2one(
        string="Manager LLM",
        comodel_name="ai.llm",
        help="""The language model used by the manager agent in a hierarchical
         process. Required when using a hierarchical process.""",
    )
    function_calling_llm = fields.Char(
        string="Function Calling LLM",
        help="""If passed, the crew will use this LLM to do function calling for
         tools for all agents in the crew. Each agent can have its own LLM,
          which overrides the crew's LLM for function calling.""",
    )
    config = fields.Text(
        string="Configuration",
        help="""Optional configuration settings for the crew,
        in Json or Dict[str, Any] format.""",
    )
    max_rpm = fields.Integer(
        string="Max RPM",
        help="""Maximum requests per minute the crew adheres to during execution.""",
    )
    language = fields.Selection(
        [("en", "English"), ("es", "Spanish"), ("pt", "Portuguese")],
        default="en",
        help="""Language used for the crew, defaults to English.""",
    )
    full_output = fields.Boolean(
        help="""Whether the crew should return the full output with all tasks
        outputs or just the final output.""",
    )
    step_callback = fields.Char(
        help="""A function that is called after each step of every agent.
        This can be used to log the agent's actions or to perform other operations;
         it won't override the agent-specific step_callback.""",
    )
    share_crew = fields.Boolean(
        help="""Whether you want to share the complete crew information and execution
         with the crewAI team to make the library better, and allow us to train models.""",
    )

    def crew(self):
        # Forming the tech-focused crew with enhanced configurations

        if self.process == "sequential":
            process = Process.sequential
        elif self.process == "hierarchical":
            process = Process.hierarchical
        else:
            raise NotImplementedError

        crew = Crew(
            agents=[agent.agent() for agent in self.agent_ids],
            tasks=[task.task() for task in self.task_ids],
            process=process,
        )
        return crew

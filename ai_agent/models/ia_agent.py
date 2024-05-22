# Copyright 2024 KMEE
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3).

from crewai import Agent

from odoo import fields, models


class IaAgent(models.Model):
    """
    An agent is an autonomous unit programmed to:

    Perform tasks
    Make decisions
    Communicate with other agents

    Think of an agent as a member of a team, with specific skills and a particular job to do.

    Agents can have different roles like 'Researcher', 'Writer',
        or 'Customer Support', each contributing to the overall goal of the crew.
    """

    _name = "ai.agent"
    _description = "ai Agent"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    _rec_name = "role"

    role = fields.Char(
        help="""Defines the agent's function within the crew.
        It determines the kind of tasks the agent is best suited for.""",
        required=True,
    )
    goal = fields.Text(
        help="""The individual objective that the agent aims to achieve.
         It guides the agent's decision-making process.""",
        required=True,
    )
    backstory = fields.Text(
        help="""Provides context to the agent's role and goal,
         enriching the interaction and collaboration dynamics.""",
        required=True,
    )
    llm_id = fields.Many2one(
        comodel_name="ai.llm",
        string="LLM",
        # default=lambda self: self.env.ref("ai.llm_gpt_4"),
        help="""The language model used by the agent to process and generate text.
        It dynamically fetches the model name from the
        OPENAI_MODEL_NAME environment variable, defaulting to 'gpt-4' if not specified.""",
    )
    tool_ids = fields.Many2many(
        comodel_name="ai.tool",
        relation="ia_agent_tool_rel",
        column1="agent_id",
        column2="tool_id",
        help="""Set of capabilities or functions that the agent can use
         to perform tasks.
        Tools can be shared or exclusive to specific agents.
        It's an attribute that can be set during the
        initialization of an agent,
        with a default value of an empty list.""",
    )
    function_calling_llm = fields.Char(
        string="Function Calling LLM",
        help="""If passed, this agent will use this LLM to execute
        function calling for tools instead of relying on the main LLM output.""",
    )
    max_iter = fields.Integer(
        string="Max Iterations",
        default=15,
        help="""The maximum number of iterations the agent can perform
        before being forced to give its best answer. Default is 15.""",
    )
    max_rpm = fields.Integer(
        string="Max RPM",
        help="""The maximum number of requests per minute the agent
        can perform to avoid rate limits. It's optional and can be left
         unspecified, with a default value of None.""",
    )
    verbose = fields.Boolean(
        default=False,
        help="""Enables detailed logging of the agent's execution for
         debugging or monitoring purposes when set to True. Default is False.""",
    )
    allow_delegation = fields.Boolean(
        default=True,
        help="""Agents can delegate tasks or questions to one another,
         ensuring that each task is handled by the most suitable agent.
          Default is True.""",
    )
    step_callback = fields.Char(
        help="""A function that is called after each step of the agent.
         This can be used to log the agent's actions or to perform other operations.
          It will overwrite the crew step_callback.""",
    )
    memory = fields.Boolean(
        default=False,
        help="""Indicates whether the agent should have memory or not,
         with a default value of False.
         This impacts the agent's ability to remember past interactions.
          Default is False.""",
    )

    def agent(self):
        """
        Create a new agent with the given values.
        """
        agent = Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            tools=[t.tool() for t in self.tool_ids],
            llm=self.llm_id.llm() if self.llm_id else None,
            # function_calling_llm=self.llm,
            # max_iter=self.max_iter,
            # max_rpm=self.max_rpm,
            verbose=self.verbose,
            allow_delegation=self.allow_delegation,
            # step_callback=self.step_callback,
            memory=self.memory,
        )
        return agent

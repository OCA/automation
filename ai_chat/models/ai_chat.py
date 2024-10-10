# Copyright 2024 KMEE
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models

from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    BaseMessageChunk,
    ChatMessage,
    ChatMessageChunk,
    FunctionMessage,
    FunctionMessageChunk,
    HumanMessage,
    HumanMessageChunk,
    SystemMessage,
    SystemMessageChunk,
    ToolMessage,
    ToolMessageChunk,
)

class AiChat(models.Model):

    _name = "ai.chat"
    _description = "Ai Chat"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char()
    llm_id = fields.Many2one(
        comodel_name="ai.llm",
        string="LLM",
        # default=lambda self: self.env.ref("ai.llm_gpt_4"),
        help="""The language model used by the agent to process and generate text.
        It dynamically fetches the model name from the
        OPENAI_MODEL_NAME environment variable, defaulting to 'gpt-4' if not specified.""",
    )

    prompt = fields.Text()

    def action_send(self):
        for record in self:
            if record.prompt:
                result = record.llm_id.llm().invoke([HumanMessage(record.prompt)])
                record.prompt += '\n\n ----' + result.content


    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        self = self.with_context(default_user_id=False)
        return super().message_new(msg_dict, custom_values=custom_values)

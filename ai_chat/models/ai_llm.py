# Copyright 2024 KMEE
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from langchain_openai import ChatOpenAI

from odoo import fields, models


class AiLlm(models.Model):

    _name = "ai.llm"
    _description = "Llm"

    name = fields.Char()

    llm_type = fields.Selection(
        string="Tool",
        selection=[
            ("ChatOpenAI", "ChatOpenAI"),
        ],
        default="ChatOpenAI",
    )

    model_name = fields.Char()
    endpoint = fields.Char()
    api_key = fields.Char()

    def name_get(self):
        return [(record.id, f"{record.name} ({record.model_name})") for record in self]

    def llm(self):

        if self.llm_type == "ChatOpenAI":
            # os.environ['OPENAI_API_KEY'] = ''
            chat_open_ai = ChatOpenAI(
                openai_api_key=self.api_key,
                openai_api_base=self.endpoint,
                model_name=self.model_name,
            )
            # chat_open_ai.temperature = self.model_name
            # chat_open_ai.openai_organization = self.api_key
            # chat_open_ai.openai_proxy = self.api_key
            return chat_open_ai
        else:
            raise NotImplementedError

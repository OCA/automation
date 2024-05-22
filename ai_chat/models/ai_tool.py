# Copyright 2024 KMEE
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3).

import inspect

import crewai_tools

from odoo import fields, models


class AiTools(models.Model):

    _name = "ai.tool"
    _description = "ai Tools"

    name = fields.Char()

    def _get_tool_selection(self):
        tools = [
            cls.__name__
            for cls in vars(crewai_tools).values()
            if inspect.isclass(cls)
            and issubclass(cls, crewai_tools.BaseTool)
            and cls != crewai_tools.BaseTool
            and cls != crewai_tools.Tool
        ]
        return [
            (tool, tool) for tool in sorted(tools)
        ]  # Transformar a lista de ferramentas em uma lista de tuplas para o campo Selection

    tool_type = fields.Selection(
        string="Tool",
        selection="_get_tool_selection",
    )

    serper_api_key = fields.Char()

    def tool(self):
        Tool = getattr(crewai_tools, self.tool_type)

        if self.tool_type == "SerperDevTool":
            tool = Tool(serper_api_key=self.serper_api_key)
            return tool
        else:
            raise NotImplementedError

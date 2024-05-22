# Copyright 2024 KMEE
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "ai",
    "summary": """
        ai""",
    "version": "16.0.1.0.0",
    "license": "LGPL-3",
    "author": "KMEE,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/ai",
    "depends": [
        "mail",
        "queue_job",
        "ia_chat",
    ],
    "data": [
        "security/ia_execution_data.xml",
        # "security/ia_llm.xml",
        "security/ia_crew.xml",
        "security/ia_execution.xml",
        # "security/ia_tool.xml",
        "security/ia_task.xml",
        "security/ia_agent.xml",
        #
        # "views/ia_llm.xml",
        "views/ia_crew.xml",
        "views/ia_execution_data.xml",
        "views/ia_execution.xml",
        # "views/ia_tool.xml",
        "views/ia_task.xml",
        "views/ia_agent.xml",
        # data
        # "data/ia_tool.xml",
        # "data/ia_llm.xml",
        "data/ia_agent.xml",
        "data/ia_task.xml",
        "data/ia_crew.xml",
        "data/ia_execution.xml",
    ],
    "demo": [
        "demo/ia_execution_data.xml",
        # "demo/ia_llm.xml",
        "demo/ia_crew.xml",
        "demo/ia_execution.xml",
        # "demo/ia_tool.xml",
        "demo/ia_task.xml",
        "demo/ia_agent.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["mileo"],
    "external_dependencies": {
        "python": [
            "crewai",
            "crewai[tools]",
        ]
    },
}

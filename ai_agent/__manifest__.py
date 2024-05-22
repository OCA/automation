# Copyright 2024 KMEE
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "AI Agents",
    "summary": """Ai Agents""",
    "version": "16.0.1.0.0",
    "license": "LGPL-3",
    "author": "KMEE,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/ai",
    "depends": [
        "mail",
        "queue_job",
        "ai_chat",
    ],
    "data": [
        "security/ai_execution_data.xml",
        # "security/ai_llm.xml",
        "security/ai_crew.xml",
        "security/ai_execution.xml",
        # "security/ai_tool.xml",
        "security/ai_task.xml",
        "security/ai_agent.xml",
        #
        # "views/ai_llm.xml",
        "views/ai_crew.xml",
        "views/ai_execution_data.xml",
        "views/ai_execution.xml",
        # "views/ai_tool.xml",
        "views/ai_task.xml",
        "views/ai_agent.xml",
        # data
        # "data/ai_tool.xml",
        # "data/ai_llm.xml",
        "data/ai_agent.xml",
        "data/ai_task.xml",
        "data/ai_crew.xml",
        "data/ai_execution.xml",
    ],
    "demo": [
        "demo/ai_execution_data.xml",
        # "demo/ai_llm.xml",
        "demo/ai_crew.xml",
        "demo/ai_execution.xml",
        # "demo/ai_tool.xml",
        "demo/ai_task.xml",
        "demo/ai_agent.xml",
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

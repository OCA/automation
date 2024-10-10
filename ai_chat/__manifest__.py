# Copyright 2024 KMEE
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "AI Chat",
    "summary": """AI Chat Prompt""",
    "version": "16.0.1.0.0",
    "license": "LGPL-3",
    "author": "KMEE,Odoo Community Association (OCA)",
    "website": "https://kmee.com.br",
    "depends": [
        "mail",
        "queue_job",
    ],
    "data": [
        'security/ai_chat.xml',
        "security/ai_llm.xml",
        "security/ai_tool.xml",
        #
        "views/ai_menu.xml",
        #
        'views/ai_chat.xml',
        #
        "views/ai_llm.xml",
        "views/ai_tool.xml",
        # data
        "data/ai_tool.xml",
        "data/ai_llm.xml",
    ],
    "demo": [
        'demo/ai_chat.xml',
        "demo/ai_llm.xml",
        "demo/ai_tool.xml",
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

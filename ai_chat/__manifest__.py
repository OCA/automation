# Copyright 2024 KMEE
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "ai Chat",
    "summary": """
        ai Chat Prompt""",
    "version": "16.0.1.0.0",
    "license": "LGPL-3",
    "author": "KMEE,Odoo Community Association (OCA)",
    "website": "https://kmee.com.br",
    "depends": [
        "mail",
        "queue_job",
    ],
    "data": [
        'security/ia_chat.xml',
        "security/ia_llm.xml",
        "security/ia_tool.xml",
        #
        "views/ia_menu.xml",
        #
        'views/ia_chat.xml',
        #
        "views/ia_llm.xml",
        "views/ia_tool.xml",
        # data
        "data/ia_tool.xml",
        "data/ia_llm.xml",
    ],
    "demo": [
        'demo/ia_chat.xml',
        "demo/ia_llm.xml",
        "demo/ia_tool.xml",
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

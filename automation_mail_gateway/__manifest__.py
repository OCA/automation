# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Automation Mail Gateway",
    "summary": """
        Integrate automation and mail gateway""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Dixmit,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/automation",
    "depends": ["automation_oca", "mail_gateway"],
    "data": [
        "views/automation_configuration_step.xml",
        "views/automation_configuration.xml",
    ],
    "demo": [],
}

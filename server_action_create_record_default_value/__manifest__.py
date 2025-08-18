# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Server Action Create Record Default Value",
    "summary": """
        Customize Server action""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["samirGuesmi", "sbejaoui"],
    "category": "marketing",
    "website": "https://github.com/OCA/automation",
    "depends": ["base"],
    "data": [
        "security/ir_actions_server_fieldvalue.xml",
        "views/server_action.xml",
    ],
    "installable": True,
}

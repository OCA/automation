# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Automation Oca",
    "summary": """
        Automate actions in threaded models""",
    "version": "16.0.1.1.3",
    "license": "AGPL-3",
    "category": "Automation",
    "author": "Dixmit,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/automation",
    "depends": ["mail", "link_tracker"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/menu.xml",
        "wizards/automation_configuration_test.xml",
        "views/automation_record.xml",
        "views/automation_record_step.xml",
        "views/automation_configuration_step.xml",
        "views/automation_configuration.xml",
        "views/link_tracker_clicks.xml",
        "views/automation_filter.xml",
        "views/automation_tag.xml",
        "data/cron.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "automation_oca/static/src/**/*.js",
            "automation_oca/static/src/**/*.xml",
            "automation_oca/static/src/**/*.scss",
        ],
    },
    "demo": [
        "demo/demo.xml",
    ],
}

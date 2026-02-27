# Copyright 2026 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    cr.execute(
        "UPDATE automation_record_step SET state='skipped' WHERE state='rejected'"
    )

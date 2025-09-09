# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import json
import uuid
from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import (
    datetime as safe_datetime,
)
from odoo.tools.safe_eval import (
    dateutil as safe_dateutil,
)
from odoo.tools.safe_eval import (
    safe_eval,
)
from odoo.tools.safe_eval import (
    time as safe_time,
)

from ..utils.query import add_complex_left_join


class AutomationConfiguration(models.Model):
    _name = "automation.configuration"
    _description = "Automation Configuration"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    tag_ids = fields.Many2many("automation.tag")
    company_id = fields.Many2one("res.company")
    domain = fields.Char(
        required=True,
        default="[]",
        compute="_compute_domain",
        help="""
        Filter to apply
        Following special variable can be used in filter :
         * datetime
         * dateutil
         * time
         * user
         * ref """,
    )
    editable_domain = fields.Char(
        required=True,
        default="[]",
        help="""Filter to apply
        Following special variable can be used in filter :
         * datetime
         * dateutil
         * time
         * user
         * ref """,
    )
    model_id = fields.Many2one(
        "ir.model",
        domain=[("is_mail_thread", "=", True)],
        required=True,
        ondelete="cascade",
        help="Model where the configuration is applied",
        string="Model ID",
    )
    filter_id = fields.Many2one("automation.filter")
    filter_domain = fields.Binary(compute="_compute_filter_domain")
    model = fields.Char(string="Model", related="model_id.model")
    field_id = fields.Many2one(
        "ir.model.fields",
        domain="[('model_id', '=', model_id), "
        "('ttype', 'in', ['char', 'selection', 'integer', 'text', 'many2one'])]",
        help="Used to avoid duplicates",
    )
    is_periodic = fields.Boolean(
        help="Mark it if you want to make the execution periodic"
    )
    # The idea of flow of states will be:
    # draft -> run       -> done -> draft (for periodic execution)
    #       -> on demand -> done -> draft (for on demand execution)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("periodic", "Periodic"),
            ("ondemand", "On demand"),
            ("done", "Done"),
        ],
        default="draft",
        required=True,
        group_expand="_group_expand_states",
    )
    automation_step_ids = fields.One2many(
        "automation.configuration.step", inverse_name="configuration_id"
    )
    automation_direct_step_ids = fields.One2many(
        "automation.configuration.step",
        inverse_name="configuration_id",
        domain=[("parent_id", "=", False)],
    )
    record_test_count = fields.Integer(compute="_compute_record_test_count")
    record_count = fields.Integer(compute="_compute_record_count")
    record_done_count = fields.Integer(compute="_compute_record_count")
    record_run_count = fields.Integer(compute="_compute_record_count")
    activity_mail_count = fields.Integer(compute="_compute_activity_count")
    activity_action_count = fields.Integer(compute="_compute_activity_count")
    click_count = fields.Integer(compute="_compute_click_count")
    next_execution_date = fields.Datetime(compute="_compute_next_execution_date")

    @api.depends("filter_id.domain", "filter_id", "editable_domain")
    def _compute_domain(self):
        for record in self:
            record.domain = (
                record.filter_id and record.filter_id.domain
            ) or record.editable_domain

    @api.depends()
    def _compute_click_count(self):
        data = self.env["link.tracker.click"].read_group(
            [("automation_configuration_id", "in", self.ids)],
            [],
            ["automation_configuration_id"],
            lazy=False,
        )
        mapped_data = {d["automation_configuration_id"][0]: d["__count"] for d in data}
        for record in self:
            record.click_count = mapped_data.get(record.id, 0)

    @api.depends()
    def _compute_activity_count(self):
        data = self.env["automation.record.step"].read_group(
            [
                ("configuration_id", "in", self.ids),
                ("state", "=", "done"),
                ("is_test", "=", False),
            ],
            [],
            ["configuration_id", "step_type"],
            lazy=False,
        )
        mapped_data = defaultdict(lambda: {})
        for d in data:
            mapped_data[d["configuration_id"][0]][d["step_type"]] = d["__count"]
        for record in self:
            record.activity_mail_count = mapped_data[record.id].get("mail", 0)
            record.activity_action_count = mapped_data[record.id].get("action", 0)

    @api.depends()
    def _compute_record_count(self):
        data = self.env["automation.record"].read_group(
            [("configuration_id", "in", self.ids), ("is_test", "=", False)],
            [],
            ["configuration_id", "state"],
            lazy=False,
        )
        mapped_data = defaultdict(lambda: {})
        for d in data:
            mapped_data[d["configuration_id"][0]][d["state"]] = d["__count"]
        for record in self:
            record.record_done_count = mapped_data[record.id].get("done", 0)
            record.record_run_count = mapped_data[record.id].get("periodic", 0)
            record.record_count = sum(mapped_data[record.id].values())

    @api.depends()
    def _compute_record_test_count(self):
        data = self.env["automation.record"].read_group(
            [("configuration_id", "in", self.ids), ("is_test", "=", True)],
            [],
            ["configuration_id"],
            lazy=False,
        )
        mapped_data = {d["configuration_id"][0]: d["__count"] for d in data}
        for record in self:
            record.record_test_count = mapped_data.get(record.id, 0)

    @api.depends("model_id")
    def _compute_filter_domain(self):
        for record in self:
            record.filter_domain = (
                [] if not record.model_id else [("model_id", "=", record.model_id.id)]
            )

    @api.depends("state")
    def _compute_next_execution_date(self):
        for record in self:
            if record.state == "periodic":
                record.next_execution_date = self.env.ref(
                    "automation_oca.cron_configuration_run"
                ).nextcall
            else:
                record.next_execution_date = False

    @api.onchange("filter_id")
    def _onchange_filter(self):
        self.model_id = self.filter_id.model_id

    @api.onchange("model_id")
    def _onchange_model(self):
        self.editable_domain = []
        self.filter_id = False
        self.field_id = False
        self.automation_step_ids = [(5, 0, 0)]

    def start_automation(self):
        self.ensure_one()
        if self.state != "draft":
            raise ValidationError(_("State must be in draft in order to start"))
        self.state = "periodic" if self.is_periodic else "ondemand"

    def done_automation(self):
        self.ensure_one()
        self.state = "done"

    def back_to_draft(self):
        self.ensure_one()
        self.state = "draft"

    def cron_automation(self):
        for record in self.search([("state", "=", "periodic")]):
            record.run_automation()

    def _get_eval_context(self):
        """Prepare the context used when evaluating python code
        :returns: dict -- evaluation context given to safe_eval
        """
        return {
            "ref": self.env.ref,
            "user": self.env.user,
            "time": safe_time,
            "datetime": safe_datetime,
            "dateutil": safe_dateutil,
        }

    def _get_automation_records_to_create(self):
        """
        We will find all the records that fulfill the domain but don't have a
        record created. Also, we need to check by autencity field if defined.

        In order to do this, we will add some extra joins on the query of the domain
        """
        eval_context = self._get_eval_context()
        domain = safe_eval(self.domain, eval_context)
        Record = self.env[self.model_id.model]
        if self.company_id and "company_id" in Record._fields:
            # In case of company defined, we add only if the records have company field
            domain += [("company_id", "=", self.company_id.id)]
        query = Record._where_calc(domain)
        alias = add_complex_left_join(
            query,
            Record._table,
            "id",
            "automation_record",
            "res_id",
            "automation_record",
            "{rhs}.model = %s AND {rhs}.configuration_id = %s AND "
            "({rhs}.is_test IS NULL OR NOT {rhs}.is_test)",
            [Record._name, self.id],
        )
        query.add_where(f"{alias}.id is NULL")
        if self.field_id:
            # In case of unicity field defined, we need to add this
            # left join to find already created records
            linked_tab = add_complex_left_join(
                query,
                Record._table,
                self.field_id.name,
                Record._table,
                self.field_id.name,
                "linked",
                "",
                [],
            )
            alias2 = add_complex_left_join(
                query,
                linked_tab,
                "id",
                "automation_record",
                "res_id",
                "automation_record_linked",
                "{rhs}.model = %s AND {rhs}.configuration_id = %s AND "
                "({rhs}.is_test IS NULL OR NOT {rhs}.is_test)",
                [Record._name, self.id],
            )
            query.add_where(f"{alias2}.id is NULL")
            query.group_by = f'"{Record._table}".{self.field_id.name}'
            query_str, params = query.select(f'MIN("{Record._table}".id)')
        else:
            query_str, params = query.select()
        self.env.cr.execute(query_str, params)
        return Record.browse([r[0] for r in self.env.cr.fetchall()])

    def run_automation(self):
        self.ensure_one()
        if self.state not in ["periodic", "ondemand"]:
            return
        records = self.env["automation.record"]
        for record in self._get_automation_records_to_create():
            records |= self._create_record(record)
        records.automation_step_ids._trigger_activities()

    def _create_record(self, record, **kwargs):
        return self.env["automation.record"].create(
            self._create_record_vals(record, **kwargs)
        )

    def _create_record_vals(self, record, **kwargs):
        return {
            **kwargs,
            "res_id": record.id,
            "model": record._name,
            "configuration_id": self.id,
            "automation_step_ids": [
                (0, 0, activity._create_record_activity_vals(record))
                for activity in self.automation_direct_step_ids
            ],
        }

    def _group_expand_states(self, states, domain):
        """
        This is used to show all the states on the kanban view
        """
        return [key for key, _val in self._fields["state"].selection]

    def save_filter(self):
        self.ensure_one()
        self.filter_id = self.env["automation.filter"].create(
            {
                "name": self.name,
                "domain": self.editable_domain,
                "model_id": self.model_id.id,
            }
        )

    def export_configuration(self):
        """
        Export the configuration to a JSON format.
        This method is used to export the configuration for external use.
        """
        self.ensure_one()
        data = self._export_configuration()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "automation_oca.automation_configuration_export_act_window"
        )
        file_name = f"automation_configuration_{self.name or 'export'}.json"
        action["res_id"] = (
            self.env["automation.configuration.export"]
            .create(
                {
                    "configuration_id": self.id,
                    "file_name": file_name,
                    "file_content": base64.b64encode(
                        json.dumps(data).encode()
                    ).decode(),
                }
            )
            .id
        )
        return action

    def _export_configuration(self):
        self.ensure_one()
        data = {
            "id": self._get_external_xmlid(self),
            "name": self.name,
            "domain": self.domain,
            "model_id": self._get_external_xmlid(self.model_id),
            "field_id": self._get_external_xmlid(self.field_id),
            "is_periodic": self.is_periodic,
            "steps": [],
        }
        extra_data = defaultdict(lambda: {})
        for step in self.automation_direct_step_ids:
            step_data = step._export_step(extra_data)
            if step_data:
                data["steps"].append(step_data)
        data["activity_types"] = extra_data["activity_types"]
        data["mail_templates"] = extra_data["mail_templates"]
        data["server_actions"] = extra_data["server_actions"]
        return data

    def _get_external_xmlid(self, record, module="__export__", name=None):
        if not record:
            return False
        result = record.get_external_id()[record.id]
        if result:
            return result
        if not name:
            name = f"{record._table}_{record.id}_{uuid.uuid4().hex[:8]}"
        self.env["ir.model.data"].create(
            {
                "name": name,
                "model": record._name,
                "res_id": record.id,
                "module": module,
            }
        )
        return f"__export__.{name}"

    def create_document_from_attachment(self, b64_data):
        data = json.loads(base64.b64decode(b64_data))
        return self._create_document_from_data(data).get_formview_action()

    def _create_document_from_data(self, data):
        record = self.create(self._create_document_from_data_vals(data))
        langs = [lang[0] for lang in self.env["res.lang"].get_installed()]
        for activity_type_id, activity_type in data.get("activity_types", {}).items():
            if not self.env.ref(activity_type_id, raise_if_not_found=False):
                self._create_document_add_activity_type(
                    activity_type_id, activity_type, langs
                )
        for mail_template_id, mail_template in data.get("mail_templates", {}).items():
            if not self.env.ref(mail_template_id, raise_if_not_found=False):
                self._create_document_add_mail_template(
                    mail_template_id, mail_template, langs
                )
        for server_action_id, server_action in data.get("server_actions", {}).items():
            if not self.env.ref(server_action_id, raise_if_not_found=False):
                self._create_document_add_server_action(
                    server_action_id, server_action, langs
                )
        for step_data in data.get("steps", []):
            record._create_document_step_from_data(step_data)
        return record

    def _create_document_step_from_data(self, step_data, parent=False):
        step = self.env["automation.configuration.step"].create(
            self._create_step_vals(step_data, parent=parent)
        )
        for child_step in step_data.get("steps", []):
            self._create_document_step_from_data(child_step, parent=step)
        return step

    def _create_document_add_activity_type(
        self, activity_type_id, activity_data, langs
    ):
        activity_type = self.env["mail.activity.type"].create(
            self._create_activity_vals(activity_data)
        )
        activity_fields = self._get_activity_type_translatable_fields()
        for lang in langs:
            vals = {}
            for field in activity_fields:
                if activity_data.get(field) and lang in activity_data[field]:
                    vals[field] = activity_data[field][lang]
            if vals:
                activity_type.with_context(lang=lang).write(vals)
        self._get_external_xmlid(
            activity_type,
            module=activity_type_id.split(".")[0],
            name=activity_type_id.split(".")[1],
        )

    def _get_activity_type_translatable_fields(self):
        """Return the fields that are translatable for activity types."""
        return ["name", "summary"]

    def _create_activity_vals(self, activity_data):
        return {
            "name": (activity_data.get("name") or {}).get(
                "en_US", "Imported activity type"
            ),
            "summary": (activity_data.get("summary") or {}).get(
                "en_US", "Imported activity summary"
            ),
            "sequence": activity_data.get("sequence", 10),
            "delay_count": activity_data.get("delay_count", 0),
            "delay_unit": activity_data.get("delay_unit", "minutes"),
            "delay_from": activity_data.get("delay_from", "now"),
            "icon": activity_data.get("icon", "fa-clock"),
            "decoration_type": activity_data.get("decoration_type"),
            "res_model": activity_data.get("res_model"),
            "triggered_next_type_id": activity_data.get("triggered_next_type_id")
            and (
                self.env.ref(
                    activity_data["triggered_next_type_id"], raise_if_not_found=False
                )
                or self.env["mail.activity.type"]
            ).id
            or False,
            "chaining_type": activity_data.get("chaining_type"),
            "category": activity_data.get("category"),
            "default_note": activity_data.get("default_note"),
        }

    def _create_document_add_mail_template(
        self, mail_template_id, mail_template_data, langs
    ):
        mail_template = self.env["mail.template"].create(
            self._create_mail_template_vals(mail_template_data)
        )
        mail_template_fields = self._get_mail_template_translatable_fields()
        for lang in langs:
            vals = {}
            for field in mail_template_fields:
                if mail_template_data.get(field) and lang in mail_template_data[field]:
                    vals[field] = mail_template_data[field][lang]
            if vals:
                mail_template.with_context(lang=lang).write(vals)
        self._get_external_xmlid(
            mail_template,
            module=mail_template_id.split(".")[0],
            name=mail_template_id.split(".")[1],
        )

    def _get_mail_template_translatable_fields(self):
        """Return the fields that are translatable for mail templates."""
        return [
            "name",
            "subject",
            "body_html",
        ]

    def _create_mail_template_vals(self, mail_template_data):
        return {
            "name": (mail_template_data.get("name") or {}).get(
                "en_US", "Imported mail template"
            ),
            "subject": (mail_template_data.get("subject") or {}).get("en_US", ""),
            "body_html": (mail_template_data.get("body_html") or {}).get("en_US", ""),
            "model_id": self.env.ref(mail_template_data["model_id"]).id
            if mail_template_data.get("model_id")
            else False,
            "auto_delete": mail_template_data.get("auto_delete", False),
            "lang": mail_template_data.get("lang", False),
            "email_from": mail_template_data.get("email_from", False),
            "email_to": mail_template_data.get("email_to", False),
            "partner_to": mail_template_data.get("partner_to", False),
            "reply_to": mail_template_data.get("reply_to", False),
        }

    def _create_document_add_server_action(
        self, server_action_id, server_action_data, langs
    ):
        server_action = self.env["ir.actions.server"].create(
            self._create_server_action_vals(server_action_data)
        )
        server_action_fields = self._get_server_action_translatable_fields()
        for lang in langs:
            vals = {}
            for field in server_action_fields:
                if server_action_data.get(field) and lang in server_action_data[field]:
                    vals[field] = server_action_data[field][lang]
            if vals:
                server_action.with_context(lang=lang).write(vals)
        self._get_external_xmlid(
            server_action,
            module=server_action_id.split(".")[0],
            name=server_action_id.split(".")[1],
        )

    def _get_server_action_translatable_fields(self):
        """Return the fields that are translatable for server actions."""
        return [
            "name",
        ]

    def _create_server_action_vals(self, server_action_data):
        return {
            "name": server_action_data.get("name", {}).get(
                "en_US", "Imported server action"
            ),
            "state": server_action_data.get("state"),
            "model_id": self.env.ref(server_action_data.get("model_id")).id,
            "binding_model_id": server_action_data.get("binding_model_id")
            and self.env.ref(server_action_data.get("binding_model_id")),
            "binding_type": server_action_data.get("binding_type"),
            "code": server_action_data.get("code"),
        }

    def _create_step_vals(self, step_data, parent=False):
        return {
            "name": step_data.get("name", ""),
            "step_type": step_data.get("step_type", "mail"),
            "configuration_id": self.id,
            "parent_id": parent.id if parent else False,
            "domain": step_data.get("domain", "[]"),
            "apply_parent_domain": step_data.get("apply_parent_domain", True),
            "trigger_interval": step_data.get("trigger_interval", 0),
            "trigger_interval_type": step_data.get("trigger_interval_type", "seconds"),
            "expiry": step_data.get("expiry", False),
            "expiry_interval": step_data.get("expiry_interval", 0),
            "trigger_type": step_data.get("trigger_type"),
            "mail_author_id": step_data.get("mail_author_id")
            and (
                self.env.ref(step_data.get("mail_author_id"), raise_if_not_found=False)
                or self.env.user
            ).id,
            "mail_template_id": step_data.get("mail_template_id")
            and self.env.ref(step_data.get("mail_template_id")).id,
            "server_action_id": step_data.get("server_action_id")
            and self.env.ref(step_data.get("server_action_id")).id,
            "server_context": step_data.get("server_context", "{}"),
            "activity_type_id": step_data.get("activity_type_id")
            and self.env.ref(step_data.get("activity_type_id")).id,
            "activity_summary": step_data.get("activity_summary", ""),
            "activity_note": step_data.get("activity_note", ""),
            "activity_date_deadline_range": step_data.get(
                "activity_date_deadline_range"
            ),
            "activity_date_deadline_range_type": step_data.get(
                "activity_date_deadline_range_type"
            ),
            "activity_user_type": step_data.get("activity_user_type"),
            "activity_user_id": step_data.get("activity_user_id")
            and (
                self.env.ref(
                    step_data.get("activity_user_id"), raise_if_not_found=False
                )
                or self.env.user
            ).id,
            "activity_user_field_id": step_data.get("activity_user_field_id")
            and self.env.ref(step_data.get("activity_user_field_id")).id,
        }

    def _create_document_from_data_vals(self, data):
        return {
            "name": data.get("name", ""),
            "model_id": self.env.ref(data.get("model_id")).id,
            "field_id": data.get("field_id") and self.env.ref(data.get("field_id")).id,
            "is_periodic": data.get("is_periodic"),
            "editable_domain": data.get("domain", "[]"),
        }

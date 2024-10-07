# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

import babel.dates
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools import get_lang
from odoo.tools.safe_eval import safe_eval


class AutomationConfigurationStep(models.Model):

    _name = "automation.configuration.step"
    _description = "Automation Steps"
    _order = "trigger_interval_hours ASC"

    name = fields.Char(required=True)
    configuration_id = fields.Many2one(
        "automation.configuration", required=True, auto_join=True
    )
    domain = fields.Char(
        required=True, default="[]", help="Filter to apply specifically"
    )
    applied_domain = fields.Char(
        compute="_compute_applied_domain",
        recursive=True,
    )
    parent_id = fields.Many2one("automation.configuration.step", ondelete="cascade")
    model_id = fields.Many2one(related="configuration_id.model_id")
    model = fields.Char(related="model_id.model")
    child_ids = fields.One2many(
        "automation.configuration.step", inverse_name="parent_id"
    )
    step_type = fields.Selection(
        [("mail", "Mail"), ("action", "Server Action"), ("activity", "Activity")],
        required=True,
        default="mail",
    )
    step_icon = fields.Char(compute="_compute_step_info")
    step_name = fields.Char(compute="_compute_step_info")
    trigger_interval_hours = fields.Integer(
        compute="_compute_trigger_interval_hours", store=True
    )
    trigger_interval = fields.Integer()
    trigger_interval_type = fields.Selection(
        [("hours", "Hour(s)"), ("days", "Day(s)")], required=True, default="hours"
    )
    allow_expiry = fields.Boolean(compute="_compute_allow_expiry")
    expiry = fields.Boolean(compute="_compute_expiry", store=True, readonly=False)
    expiry_interval = fields.Integer()
    expiry_interval_type = fields.Selection(
        [("hours", "Hour(s)"), ("days", "Day(s)")], required=True, default="hours"
    )
    trigger_type = fields.Selection(
        selection="_trigger_type_selection",
        required=True,
        default="start",
    )
    trigger_child_types = fields.Json(compute="_compute_trigger_child_types")
    trigger_type_data = fields.Json(compute="_compute_trigger_type_data")
    mail_author_id = fields.Many2one(
        "res.partner", required=True, default=lambda r: r.env.user.id
    )
    mail_template_id = fields.Many2one(
        "mail.template", domain="[('model_id', '=', model_id)]"
    )
    server_action_id = fields.Many2one(
        "ir.actions.server", domain="[('model_id', '=', model_id)]"
    )
    activity_type_id = fields.Many2one(
        "mail.activity.type",
        string="Activity",
        domain="['|', ('res_model', '=', False), ('res_model', '=', model)]",
        compute="_compute_activity_info",
        readonly=False,
        store=True,
        ondelete="restrict",
    )
    activity_summary = fields.Char(
        "Summary", compute="_compute_activity_info", readonly=False, store=True
    )
    activity_note = fields.Html(
        "Note", compute="_compute_activity_info", readonly=False, store=True
    )
    activity_date_deadline_range = fields.Integer(
        string="Due Date In",
        compute="_compute_activity_info",
        readonly=False,
        store=True,
    )
    activity_date_deadline_range_type = fields.Selection(
        [("days", "Day(s)"), ("weeks", "Week(s)"), ("months", "Month(s)")],
        string="Due type",
        default="days",
        compute="_compute_activity_info",
        readonly=False,
        store=True,
    )
    activity_user_type = fields.Selection(
        [("specific", "Specific User"), ("generic", "Generic User From Record")],
        compute="_compute_activity_info",
        readonly=False,
        store=True,
        help="""Use 'Specific User' to always assign the same user on the next activity.
        Use 'Generic User From Record' to specify the field name of the user
        to choose on the record.""",
    )
    activity_user_id = fields.Many2one(
        "res.users",
        string="Responsible",
        compute="_compute_activity_info",
        readonly=False,
        store=True,
    )
    activity_user_field_id = fields.Many2one(
        "ir.model.fields",
        "User field name",
        compute="_compute_activity_info",
        readonly=False,
        store=True,
    )
    parent_position = fields.Integer(
        compute="_compute_parent_position", recursive=True, store=True
    )
    graph_data = fields.Json(compute="_compute_graph_data")
    graph_done = fields.Integer(compute="_compute_total_graph_data")
    graph_error = fields.Integer(compute="_compute_total_graph_data")

    @api.onchange("trigger_type")
    def _onchange_trigger_type(self):
        if self.trigger_type == "start":
            # Theoretically, only start allows no parent, so we will keep it this way
            self.parent_id = False

    ########################################
    # Graph computed fields ################
    ########################################

    @api.depends()
    def _compute_graph_data(self):
        total = self.env["automation.record.step"].read_group(
            [
                ("configuration_step_id", "in", self.ids),
                (
                    "processed_on",
                    ">=",
                    fields.Date.context_today(self) + relativedelta(days=-14),
                ),
                ("is_test", "=", False),
            ],
            ["configuration_step_id"],
            ["configuration_step_id", "processed_on:day"],
            lazy=False,
        )
        done = self.env["automation.record.step"].read_group(
            [
                ("configuration_step_id", "in", self.ids),
                (
                    "processed_on",
                    ">=",
                    fields.Date.context_today(self) + relativedelta(days=-14),
                ),
                ("state", "=", "done"),
                ("is_test", "=", False),
            ],
            ["configuration_step_id"],
            ["configuration_step_id", "processed_on:day"],
            lazy=False,
        )
        now = fields.Datetime.now()
        date_map = {
            babel.dates.format_datetime(
                now + relativedelta(days=i - 14),
                format="dd MMM yyy",
                tzinfo=self._context.get("tz", None),
                locale=get_lang(self.env).code,
            ): 0
            for i in range(0, 15)
        }
        result = defaultdict(
            lambda: {"done": date_map.copy(), "error": date_map.copy()}
        )
        for line in total:
            result[line["configuration_step_id"][0]]["error"][
                line["processed_on:day"]
            ] += line["__count"]
        for line in done:
            result[line["configuration_step_id"][0]]["done"][
                line["processed_on:day"]
            ] += line["__count"]
            result[line["configuration_step_id"][0]]["error"][
                line["processed_on:day"]
            ] -= line["__count"]
        for record in self:
            graph_info = dict(result[record.id])
            record.graph_data = {
                "error": [
                    {"x": key[:-5], "y": value, "name": key}
                    for (key, value) in graph_info["error"].items()
                ],
                "done": [
                    {"x": key[:-5], "y": value, "name": key}
                    for (key, value) in graph_info["done"].items()
                ],
            }

    @api.depends()
    def _compute_total_graph_data(self):
        for record in self:
            record.graph_done = self.env["automation.record.step"].search_count(
                [
                    ("configuration_step_id", "=", record.id),
                    ("state", "=", "done"),
                    ("is_test", "=", False),
                ]
            )
            record.graph_error = self.env["automation.record.step"].search_count(
                [
                    ("configuration_step_id", "=", record.id),
                    ("state", "in", ["expired", "rejected", "error", "cancel"]),
                    ("is_test", "=", False),
                ]
            )

    @api.depends("step_type")
    def _compute_activity_info(self):
        for to_reset in self.filtered(lambda act: act.step_type != "activity"):
            to_reset.activity_summary = False
            to_reset.activity_note = False
            to_reset.activity_date_deadline_range = False
            to_reset.activity_date_deadline_range_type = False
            to_reset.activity_user_type = False
            to_reset.activity_user_id = False
            to_reset.activity_user_field_id = False
        for activity in self.filtered(lambda act: act.step_type == "activity"):
            if not activity.activity_date_deadline_range_type:
                activity.activity_date_deadline_range_type = "days"
            if not activity.activity_user_id:
                activity.activity_user_id = self.env.user.id

    @api.depends("trigger_interval", "trigger_interval_type")
    def _compute_trigger_interval_hours(self):
        for record in self:
            record.trigger_interval_hours = record._get_trigger_interval_hours()

    def _get_trigger_interval_hours(self):
        if self.trigger_interval_type == "days":
            return self.trigger_interval * 24
        return self.trigger_interval

    @api.depends("parent_id", "parent_id.parent_position", "trigger_type")
    def _compute_parent_position(self):
        for record in self:
            record.parent_position = (
                (record.parent_id.parent_position + 1) if record.parent_id else 0
            )

    @api.depends(
        "domain", "configuration_id.domain", "parent_id", "parent_id.applied_domain"
    )
    def _compute_applied_domain(self):
        for record in self:
            eval_context = record.configuration_id._get_eval_context()
            record.applied_domain = expression.AND(
                [
                    safe_eval(record.domain, eval_context),
                    safe_eval(
                        (record.parent_id and record.parent_id.applied_domain)
                        or record.configuration_id.domain,
                        eval_context,
                    ),
                ]
            )

    @api.model
    def _trigger_type_selection(self):
        return [
            (trigger_id, trigger.get("name", trigger_id))
            for trigger_id, trigger in self._trigger_types().items()
        ]

    @api.model
    def _trigger_types(self):
        """
        This function will return a dictionary that map trigger_types to its configurations.
        Each trigger_type can contain:
        - name (Required field)
        - step type: List of step types that succeed after this.
          If it is false, it will work for all step types,
          otherwise only for the ones on the list
        - color: Color of the icon
        - icon: Icon to show
        - message_configuration: Message to show on the step configuration
        - allow_expiry: True if it allows expiration of activity
        - message: Message to show on the record if expected is not date defined
        """
        return {
            "start": {
                "name": _("start of workflow"),
                "step_type": [],
                "message_configuration": False,
                "message": False,
                "allow_parent": True,
            },
            "after_step": {
                "name": _("execution of another step"),
                "color": "text-success",
                "icon": "fa fa-code-fork fa-rotate-180 fa-flip-vertical",
                "message_configuration": False,
                "message": False,
            },
            "mail_open": {
                "name": _("Mail opened"),
                "allow_expiry": True,
                "step_type": ["mail"],
                "color": "text-success",
                "icon": "fa fa-envelope-open-o",
                "message_configuration": _("Opened after"),
                "message": _("Not opened yet"),
            },
            "mail_not_open": {
                "name": _("Mail not opened"),
                "step_type": ["mail"],
                "color": "text-danger",
                "icon": "fa fa-envelope-open-o",
                "message_configuration": _("Not opened within"),
                "message": False,
            },
            "mail_reply": {
                "name": _("Mail replied"),
                "allow_expiry": True,
                "step_type": ["mail"],
                "color": "text-success",
                "icon": "fa fa-reply",
                "message_configuration": _("Replied after"),
                "message": _("Not replied yet"),
            },
            "mail_not_reply": {
                "name": _("Mail not replied"),
                "step_type": ["mail"],
                "color": "text-danger",
                "icon": "fa fa-reply",
                "message_configuration": _("Not replied within"),
                "message": False,
            },
            "mail_click": {
                "name": _("Mail clicked"),
                "allow_expiry": True,
                "step_type": ["mail"],
                "color": "text-success",
                "icon": "fa fa-hand-pointer-o",
                "message_configuration": _("Clicked after"),
                "message": _("Not clicked yet"),
            },
            "mail_not_clicked": {
                "name": _("Mail not clicked"),
                "step_type": ["mail"],
                "color": "text-danger",
                "icon": "fa fa-hand-pointer-o",
                "message_configuration": _("Not clicked within"),
                "message": False,
            },
            "mail_bounce": {
                "name": _("Mail bounced"),
                "allow_expiry": True,
                "step_type": ["mail"],
                "color": "text-danger",
                "icon": "fa fa-exclamation-circle",
                "message_configuration": _("Bounced after"),
                "message": _("Not bounced yet"),
            },
            "activity_done": {
                "name": _("Activity has been finished"),
                "step_type": ["activity"],
                "color": "text-success",
                "icon": "fa fa-clock-o",
                "message_configuration": _("After finished"),
                "message": _("Activity not done"),
            },
            "activity_not_done": {
                "name": _("Activity has not been finished"),
                "allow_expiry": True,
                "step_type": ["activity"],
                "color": "text-danger",
                "icon": "fa fa-clock-o",
                "message_configuration": _("Not finished within"),
                "message": False,
            },
        }

    @api.model
    def _step_icons(self):
        """
        This function will return a dictionary that maps step types and icons
        """
        return {
            "mail": "fa fa-envelope",
            "activity": "fa fa-clock-o",
            "action": "fa fa-cogs",
        }

    @api.depends("step_type")
    def _compute_step_info(self):
        step_icons = self._step_icons()
        step_name_map = dict(self._fields["step_type"].selection)
        for record in self:
            record.step_icon = step_icons.get(record.step_type, "")
            record.step_name = step_name_map.get(record.step_type, "")

    @api.depends("trigger_type")
    def _compute_trigger_type_data(self):
        trigger_types = self._trigger_types()
        for record in self:
            record.trigger_type_data = trigger_types[record.trigger_type]

    @api.depends("trigger_type")
    def _compute_allow_expiry(self):
        trigger_types = self._trigger_types()
        for record in self:
            record.allow_expiry = trigger_types[record.trigger_type].get(
                "allow_expiry", False
            )

    @api.depends("trigger_type")
    def _compute_expiry(self):
        trigger_types = self._trigger_types()
        for record in self:
            record.expiry = (
                trigger_types[record.trigger_type].get("allow_expiry", False)
                and record.expiry
            )

    @api.depends("step_type")
    def _compute_trigger_child_types(self):
        trigger_types = self._trigger_types()
        for record in self:
            trigger_child_types = {}
            for trigger_type_id, trigger_type in trigger_types.items():
                if "step_type" not in trigger_type:
                    # All are allowed
                    trigger_child_types[trigger_type_id] = trigger_type
                elif record.step_type in trigger_type["step_type"]:
                    trigger_child_types[trigger_type_id] = trigger_type
            record.trigger_child_types = trigger_child_types

    def _check_configuration(self):
        trigger_conf = self._trigger_types()[self.trigger_type]
        if not self.parent_id and not trigger_conf.get("allow_parent"):
            raise ValidationError(
                _("%s configurations needs a parent") % trigger_conf["name"]
            )
        if (
            self.parent_id
            and "step_type" in trigger_conf
            and self.parent_id.step_type not in trigger_conf["step_type"]
        ):
            step_types = dict(self._fields["step_type"].selection)
            raise ValidationError(
                _("To use a %(name)s trigger type we need a parent of type %(parents)s")
                % {
                    "name": trigger_conf["name"],
                    "parents": ",".join(
                        [
                            name
                            for step_type, name in step_types.items()
                            if step_type in trigger_conf["step_type"]
                        ]
                    ),
                }
            )

    @api.constrains("parent_id", "parent_id.step_type", "trigger_type")
    def _check_parent_configuration(self):
        for record in self:
            record._check_configuration()

    def _get_record_activity_scheduled_date(self):
        if self.trigger_type in [
            "mail_open",
            "mail_bounce",
            "mail_click",
            "mail_not_clicked",
            "mail_reply",
            "mail_not_reply",
            "activity_done",
        ]:
            return False
        return fields.Datetime.now() + relativedelta(
            **{self.trigger_interval_type: self.trigger_interval}
        )

    def _get_expiry_date(self):
        if not self.expiry:
            return False
        return fields.Datetime.now() + relativedelta(
            **{self.expiry_interval_type: self.expiry_interval}
        )

    def _create_record_activity_vals(self, record, **kwargs):
        return {
            "configuration_step_id": self.id,
            "expiry_date": self._get_expiry_date(),
            "scheduled_date": self._get_record_activity_scheduled_date(),
            **kwargs,
        }

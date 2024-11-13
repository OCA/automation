# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import threading
import traceback
from io import StringIO

import werkzeug.urls
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models, tools
from odoo.tools.safe_eval import safe_eval


class AutomationRecordStep(models.Model):
    _name = "automation.record.step"
    _description = "Activities done on the record"
    _order = "scheduled_date ASC"

    name = fields.Char(related="configuration_step_id.name")
    record_id = fields.Many2one("automation.record", required=True, ondelete="cascade")
    configuration_step_id = fields.Many2one(
        "automation.configuration.step", required=True
    )
    configuration_id = fields.Many2one(
        related="configuration_step_id.configuration_id",
        store=True,
    )
    step_type = fields.Selection(related="configuration_step_id.step_type", store=True)
    scheduled_date = fields.Datetime(readonly=True)
    expiry_date = fields.Datetime(readonly=True)
    processed_on = fields.Datetime(readonly=True)
    parent_id = fields.Many2one("automation.record.step", readonly=True)
    child_ids = fields.One2many("automation.record.step", inverse_name="parent_id")
    trigger_type = fields.Selection(related="configuration_step_id.trigger_type")
    trigger_type_data = fields.Json(compute="_compute_trigger_type_data")
    step_icon = fields.Char(compute="_compute_step_info")
    step_name = fields.Char(compute="_compute_step_info")
    state = fields.Selection(
        [
            ("scheduled", "Scheduled"),
            ("done", "Done"),
            ("expired", "Expired"),
            ("rejected", "Rejected"),
            ("error", "Error"),
            ("cancel", "Cancelled"),
        ],
        default="scheduled",
        readonly=True,
    )
    error_trace = fields.Text(readonly=True)
    parent_position = fields.Integer(
        compute="_compute_parent_position", recursive=True, store=True
    )

    # Mailing fields
    message_id = fields.Char(readonly=True)
    mail_status = fields.Selection(
        [
            ("sent", "Sent"),
            ("open", "Opened"),
            ("bounce", "Bounced"),
            ("reply", "Replied"),
        ],
        readonly=True,
    )
    mail_clicked_on = fields.Datetime(readonly=True)
    mail_replied_on = fields.Datetime(readonly=True)
    mail_opened_on = fields.Datetime(readonly=True)
    activity_done_on = fields.Datetime(readonly=True)
    is_test = fields.Boolean(related="record_id.is_test", store=True)
    step_actions = fields.Json(compute="_compute_step_actions")

    @api.depends("trigger_type")
    def _compute_trigger_type_data(self):
        trigger_types = self.env["automation.configuration.step"]._trigger_types()
        for record in self:
            record.trigger_type_data = trigger_types[record.trigger_type]

    @api.depends("parent_id", "parent_id.parent_position")
    def _compute_parent_position(self):
        for record in self:
            record.parent_position = (
                (record.parent_id.parent_position + 1) if record.parent_id else 0
            )

    @api.depends("step_type")
    def _compute_step_info(self):
        step_icons = self.env["automation.configuration.step"]._step_icons()
        step_name_map = dict(
            self.env["automation.configuration.step"]._fields["step_type"].selection
        )
        for record in self:
            record.step_icon = step_icons.get(record.step_type, "")
            record.step_name = step_name_map.get(record.step_type, "")

    def _check_to_execute(self):
        if (
            self.configuration_step_id.trigger_type == "mail_not_open"
            and self.parent_id.mail_status in ["open", "reply"]
        ):
            return False
        if (
            self.configuration_step_id.trigger_type == "mail_not_reply"
            and self.parent_id.mail_status == "reply"
        ):
            return False
        if (
            self.configuration_step_id.trigger_type == "mail_not_clicked"
            and self.parent_id.mail_clicked_on
        ):
            return False
        if (
            self.configuration_step_id.trigger_type == "activity_not_done"
            and self.parent_id.activity_done_on
        ):
            return False
        return True

    def run(self, trigger_activity=True):
        self.ensure_one()
        if self.state != "scheduled":
            return self.browse()
        if (
            self.record_id.resource_ref is None
            or not self.record_id.resource_ref.filtered_domain(
                safe_eval(
                    self.configuration_step_id.applied_domain,
                    self.configuration_step_id.configuration_id._get_eval_context(),
                )
            )
            or not self._check_to_execute()
        ):
            self.write({"state": "rejected", "processed_on": fields.Datetime.now()})
            return self.browse()
        try:
            result = getattr(self, "_run_%s" % self.configuration_step_id.step_type)()
            self.write({"state": "done", "processed_on": fields.Datetime.now()})
            if result:
                childs = self._fill_childs()
                if trigger_activity:
                    childs._trigger_activities()
                return childs
        except Exception:
            buff = StringIO()
            traceback.print_exc(file=buff)
            traceback_txt = buff.getvalue()
            self.write(
                {
                    "state": "error",
                    "error_trace": traceback_txt,
                    "processed_on": fields.Datetime.now(),
                }
            )
        return self.browse()

    def _fill_childs(self, **kwargs):
        return self.create(
            [
                activity._create_record_activity_vals(
                    self.record_id.resource_ref,
                    parent_id=self.id,
                    record_id=self.record_id.id,
                    **kwargs
                )
                for activity in self.configuration_step_id.child_ids
            ]
        )

    def _run_activity(self):
        record = self.env[self.record_id.model].browse(self.record_id.res_id)

        vals = {
            "summary": self.configuration_step_id.activity_summary or "",
            "note": self.configuration_step_id.activity_note or "",
            "activity_type_id": self.configuration_step_id.activity_type_id.id,
            "automation_record_step_id": self.id,
        }
        if self.configuration_step_id.activity_date_deadline_range > 0:
            range_type = self.configuration_step_id.activity_date_deadline_range_type
            vals["date_deadline"] = fields.Date.context_today(self) + relativedelta(
                **{range_type: self.configuration_step_id.activity_date_deadline_range}
            )
        user = False
        if self.configuration_step_id.activity_user_type == "specific":
            user = self.configuration_step_id.activity_user_id
        elif self.configuration_step_id.activity_user_type == "generic":
            user = record[self.configuration_step_id.activity_user_field_id.name]
        if user:
            vals["user_id"] = user.id
        record.activity_schedule(**vals)
        return True

    def _run_mail(self):
        author_id = self.configuration_step_id.mail_author_id.id
        composer_values = {
            "author_id": author_id,
            "record_name": False,
            "model": self.record_id.model,
            "composition_mode": "mass_mail",
            "template_id": self.configuration_step_id.mail_template_id.id,
            "automation_record_step_id": self.id,
        }
        res_ids = [self.record_id.res_id]
        composer = (
            self.env["mail.compose.message"]
            .with_context(active_ids=res_ids)
            .create(composer_values)
        )
        composer.write(
            composer._onchange_template_id(
                self.configuration_step_id.mail_template_id.id,
                "mass_mail",
                self.record_id.model,
                self.record_id.res_id,
            )["value"]
        )
        # composer.body =
        extra_context = self._run_mail_context()
        composer = composer.with_context(active_ids=res_ids, **extra_context)
        # auto-commit except in testing mode
        auto_commit = not getattr(threading.current_thread(), "testing", False)
        if not self.is_test:
            # We just abort the sending, but we want to check how the generation works
            composer._action_send_mail(auto_commit=auto_commit)
        self.mail_status = "sent"
        return True

    def _get_mail_tracking_token(self):
        return tools.hmac(self.env(su=True), "automation_oca", self.id)

    def _get_mail_tracking_url(self):
        return werkzeug.urls.url_join(
            self.get_base_url(),
            "automation_oca/track/%s/%s/blank.gif"
            % (self.id, self._get_mail_tracking_token()),
        )

    def _run_mail_context(self):
        return {}

    def _run_action(self):
        self.configuration_step_id.server_action_id.with_context(
            active_model=self.record_id.model,
            active_ids=[self.record_id.res_id],
        ).run()
        return True

    def _cron_automation_steps(self):
        childs = self.browse()
        for activity in self.search(
            [
                ("state", "=", "scheduled"),
                ("scheduled_date", "<=", fields.Datetime.now()),
            ]
        ):
            childs |= activity.run(trigger_activity=False)
        childs._trigger_activities()
        self.search(
            [
                ("state", "=", "scheduled"),
                ("expiry_date", "!=", False),
                ("expiry_date", "<=", fields.Datetime.now()),
            ]
        )._expiry()

    def _trigger_activities(self):
        # Creates a cron trigger.
        # On glue modules we could use queue job for a more discrete example
        # But cron trigger fulfills the job in some way
        for date in set(self.mapped("scheduled_date")):
            if date:
                self.env["ir.cron.trigger"].create(
                    {
                        "call_at": date,
                        "cron_id": self.env.ref("automation_oca.cron_step_execute").id,
                    }
                )

    def _expiry(self):
        self.write({"state": "expired", "processed_on": fields.Datetime.now()})

    def cancel(self):
        self.filtered(lambda r: r.state == "scheduled").write(
            {"state": "cancel", "processed_on": fields.Datetime.now()}
        )

    def _activate(self):
        todo = self.filtered(lambda r: not r.scheduled_date)
        for record in todo:
            config = record.configuration_step_id
            record.scheduled_date = fields.Datetime.now() + relativedelta(
                **{config.trigger_interval_type: config.trigger_interval}
            )
        todo._trigger_activities()

    def _set_activity_done(self):
        self.write({"activity_done_on": fields.Datetime.now()})
        self.child_ids.filtered(
            lambda r: r.trigger_type == "activity_done"
            and not r.scheduled_date
            and r.state == "scheduled"
        )._activate()

    def _set_mail_bounced(self):
        self.write({"mail_status": "bounce"})
        self.child_ids.filtered(
            lambda r: r.trigger_type == "mail_bounce"
            and not r.scheduled_date
            and r.state == "scheduled"
        )._activate()

    def _set_mail_open(self):
        self.filtered(lambda t: t.mail_status not in ["open", "reply"]).write(
            {"mail_status": "open", "mail_opened_on": fields.Datetime.now()}
        )
        self.child_ids.filtered(
            lambda r: r.trigger_type
            in ["mail_open", "mail_not_reply", "mail_not_clicked"]
            and not r.scheduled_date
            and r.state == "scheduled"
        )._activate()

    def _set_mail_clicked(self):
        self.filtered(lambda t: not t.mail_clicked_on).write(
            {"mail_clicked_on": fields.Datetime.now()}
        )
        self.child_ids.filtered(
            lambda r: r.trigger_type == "mail_click"
            and not r.scheduled_date
            and r.state == "scheduled"
        )._activate()

    def _set_mail_reply(self):
        self.filtered(lambda t: t.mail_status != "reply").write(
            {"mail_status": "reply", "mail_replied_on": fields.Datetime.now()}
        )
        self.child_ids.filtered(
            lambda r: r.trigger_type == "mail_reply"
            and not r.scheduled_date
            and r.state == "scheduled"
        )._activate()

    @api.depends("state")
    def _compute_step_actions(self):
        for record in self:
            record.step_actions = record._get_step_actions()

    def _get_step_actions(self):
        """
        This should return a list of dictionaries that will have the following keys:
        - icon: Icon to show (fontawesome icon like fa fa-clock-o)
        - name: name of the action to show (translatable value)
        - done: if the action succeeded (boolean)
        - color: Color to show when done (text-success, text-danger...)
        """
        if self.step_type == "activity":
            return [
                {
                    "icon": "fa fa-clock-o",
                    "name": _("Activity Done"),
                    "done": bool(self.activity_done_on),
                    "color": "text-success",
                }
            ]
        if self.step_type == "mail":
            return [
                {
                    "icon": "fa fa-envelope",
                    "name": _("Sent"),
                    "done": bool(self.mail_status and self.mail_status != "bounced"),
                    "color": "text-success",
                },
                {
                    "icon": "fa fa-envelope-open-o",
                    "name": _("Opened"),
                    "done": bool(
                        self.mail_status and self.mail_status in ["reply", "open"]
                    ),
                    "color": "text-success",
                },
                {
                    "icon": "fa fa-hand-pointer-o",
                    "name": _("Clicked"),
                    "done": bool(self.mail_status and self.mail_clicked_on),
                    "color": "text-success",
                },
                {
                    "icon": "fa fa-reply",
                    "name": _("Replied"),
                    "done": bool(self.mail_status and self.mail_status == "reply"),
                    "color": "text-success",
                },
                {
                    "icon": "fa fa-exclamation-circle",
                    "name": _("Bounced"),
                    "done": bool(self.mail_status and self.mail_status == "bounce"),
                    "color": "text-danger",
                },
            ]
        return []

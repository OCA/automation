# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from werkzeug.exceptions import NotFound

from odoo import http, tools
from odoo.http import Response, request
from odoo.tools import consteq


class AutomationOCAController(http.Controller):
    # ------------------------------------------------------------
    # TRACKING
    # ------------------------------------------------------------

    @http.route(
        "/automation_oca/track/<int:record_id>/<string:token>/blank.gif",
        type="http",
        auth="public",
    )
    def automation_oca_mail_open(self, record_id, token, **post):
        """Email tracking. Blank item added.
        We will return the blank item allways, but we will make the request only if
        the data is correct"""
        if consteq(
            token,
            tools.hmac(request.env(su=True), "automation_oca", record_id),
        ):
            request.env["automation.record.step"].sudo().browse(
                record_id
            )._set_mail_open()
        response = Response()
        response.mimetype = "image/gif"
        response.data = base64.b64decode(
            b"R0lGODlhAQABAIAAANvf7wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=="
            # This is the code of a blank small image
        )

        return response

    @http.route(
        "/r/<string:code>/au/<int:record_id>/<string:token>", type="http", auth="public"
    )
    def automation_oca_redirect(self, code, record_id, token, **post):
        # don't assume geoip is set, it is part of the website module
        # which mass_mailing doesn't depend on
        country_code = request.geoip.get("country_code")
        automation_record_step_id = False
        if consteq(
            token,
            tools.hmac(request.env(su=True), "automation_oca", record_id),
        ):
            automation_record_step_id = record_id
        request.env["link.tracker.click"].sudo().add_click(
            code,
            ip=request.httprequest.remote_addr,
            country_code=country_code,
            automation_record_step_id=automation_record_step_id,
        )
        redirect_url = request.env["link.tracker"].get_url_from_code(code)
        if not redirect_url:
            raise NotFound()
        return request.redirect(redirect_url, code=301, local=False)

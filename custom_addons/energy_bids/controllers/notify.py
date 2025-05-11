from odoo import http
from odoo.http import request

class EnergyBidNotify(http.Controller):

    @staticmethod
    def send_admin_bid_notification(bid):
        """Send email to admins when a new bid is submitted."""
        template = request.env.ref('energy_bids.email_template_bid_submission')
        if template:
            # Safe fallback: manually set base URL in context, avoid relying on company_id.website_id
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            ctx = {
                'default_url': f"{base_url}/my/bids/{bid.id}",
                'default_company_id': request.env.company.id,
            }
            template.sudo().with_context(ctx).send_mail(bid.id, force_send=True)
from odoo import http
from odoo.http import request

class SupplierPortal(http.Controller):

    @http.route('/my/supplier-bids', type='http', auth='user', website=True)
    def supplier_bids_portal(self, **kwargs):
        user = request.env.user
        if user.user_type != 'supplier':
            return request.redirect('/my')

        supplier_bids = request.env['supplier.bid'].sudo().search([
            ('supplier_id', '=', user.id)
        ], order="submitted_at desc")

        return request.render('energy_bids.portal_supplier_bids_template', {
            'supplier_bids': supplier_bids,
        })
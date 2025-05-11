
from odoo import http
from odoo.http import request

class BidPortal(http.Controller):

    @http.route('/my/bids', type='http', auth='user', website=True)
    def my_bids(self):
        company = request.env['energy.company'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        if not company:
            return request.redirect('/register/step1')

        bids = request.env['energy.bid'].sudo().search([('company_id', '=', company.id)], order="create_date desc")
        return request.render('energy_bids.portal_bids', {'bids': bids, 'company': company})
    
    @http.route('/my/bids/create', type='http', auth='user', methods=['GET'], website=True)
    @http.route('/my/bids/create', type='http', auth='user', methods=['GET'], website=True)
    def create_bid_get(self):
        company = request.env['energy.company'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        if not company:
            return request.redirect('/register/step1')
        
        if not company.is_approved:
            return request.render('energy_bids.portal_bids_not_approved')

        return request.render('energy_bids.portal_bids_create')

    @http.route('/my/bids/create', type='http', auth='user', methods=['POST'], website=True)
    def create_bid_post(self, **post):
        company = request.env['energy.company'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        if not company:
            return request.redirect('/register/step1')
        
        if not company.is_approved:
            return request.render('energy_bids.portal_bids_not_approved')

        bid = request.env['energy.bid'].sudo().create({
            'company_id': company.id,
            'energy_type': post.get('energy_type'),
            'volume_requested': float(post.get('volume_requested').replace(',', '')),
            'location': post.get('location'),
            'payment_type': post.get('payment_type'),
            'supply_date': post.get('supply_date'),
            'preferred_hours': post.get('preferred_hours'),
            'frequency': post.get('frequency'),
            'user_id': request.env.user.id,
        })
        from odoo.addons.energy_bids.controllers.notify import EnergyBidNotify
        EnergyBidNotify.send_admin_bid_notification(bid)
        return request.redirect('/my/bids')

    @http.route('/my/bids/<int:bid_id>', type='http', auth='user', website=True)
    def view_bid(self, bid_id):
        bid = request.env['energy.bid'].sudo().browse(bid_id)
        if bid.user_id.id != request.env.user.id:
            return request.redirect('/my/bids')
        return request.render('energy_bids.portal_bids_view', {'bid': bid})

    @http.route('/my/bids/<int:bid_id>/cancel', type='http', auth='user', website=True)
    def cancel_bid(self, bid_id):
        bid = request.env['energy.bid'].sudo().browse(bid_id)
        if bid.user_id.id == request.env.user.id and bid.status == 'pending':
            bid.sudo().write({'status': 'cancelled'})
        return request.redirect('/my/bids')

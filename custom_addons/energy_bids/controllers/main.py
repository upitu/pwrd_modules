
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
    
    # @http.route('/my/bids/create', type='http', auth='user', methods=['GET'], website=True)
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
        
        try:
            volume = float(post.get('volume_requested', '0').replace(',', '').strip())
        except ValueError:
            volume = 0
        
        try:
            try:
                location_id = int(post.get('location_id')) if post.get('location_id') else int(post.get('location_name')) if post.get('location_name') else False
            except ValueError:
                    location_id = False
            location_link = post.get('location_link', '').strip()

            bid = request.env['energy.bid'].sudo().create({
                'company_id': company.id,
                'energy_type': post.get('energy_type'),
                'volume_requested': volume,
                'location': location_id,
                'location_link': location_link,
                'payment_type': post.get('payment_type'),
                'supply_date': post.get('supply_date'),
                'preferred_hours': post.get('preferred_hours'),
                'frequency': post.get('frequency'),
                'user_id': request.env.user.id,
            })
            from odoo.addons.energy_bids.controllers.notify import EnergyBidNotify
            EnergyBidNotify.send_admin_bid_notification(bid)
            return request.redirect('/my/bids')
        except Exception as e:
            request.env.cr.rollback()
            return request.render('energy_bids.portal_bids_create', {
                'error': str(e)
            })

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

    @http.route('/my/bids/view/<int:bid_id>', type='http', auth='user', website=True)
    def view_bid_details(self, bid_id, **kwargs):
        user = request.env.user
        if user.user_type != 'company':
            return request.redirect('/my')

        bid = request.env['energy.bid'].sudo().browse(bid_id)
        if not bid or bid.company_id.user_id.id != user.id:
            return request.not_found()

        supplier_bids = request.env['supplier.bid'].sudo().search([
            ('bid_id', '=', bid.id)
        ], order="amount asc")

        return request.render('energy_bids.portal_company_bid_view_template', {
            'bid': bid,
            'supplier_bids': supplier_bids,
        })
    
    @http.route('/my/bids/<int:supplier_bid_id>/approve', type='json', auth='user')
    def approve_supplier_bid(self, supplier_bid_id, **kwargs):
        supplier_bid = request.env['supplier.bid'].sudo().browse(supplier_bid_id)
        bid = supplier_bid.bid_id

        if request.env.user.id != bid.company_id.user_id.id:
            return {'error': 'Unauthorized'}

        supplier_bids = request.env['supplier.bid'].sudo().search([
            ('bid_id', '=', bid.id)
        ])
        for sb in supplier_bids:
            sb.status = 'rejected'

        supplier_bid.status = 'approved'

        return {'success': True}
import json
from urllib import response
from odoo import http
from odoo.http import request, Response
import logging

_logger = logging.getLogger(__name__)

class BidsMarketplace(http.Controller):

    @http.route(['/bids/marketplace'], type='http', auth='public', website=True)
    def bids_marketplace(self, **kw):
        try:
            env = request.env
            domain = []

            if 'energy_type' in kw:
                domain.append(('energy_type', '=', kw['energy_type']))
            if kw.get('min_volume'):
                domain.append(('volume_requested', '>=', float(kw['min_volume'])))
            if kw.get('max_volume'):
                domain.append(('volume_requested', '<=', float(kw['max_volume'])))
            if kw.get('location'):
                domain.append(('location', '=', int(kw['location'])))

            bids = env['energy.bid'].sudo().with_context(prefetch_fields=[
                'company_id.company_name',
                'location.name',
            ]).search(domain)

            bids.read(['company_id', 'location']) 

            energy_types = [
                {'value': 'diesel', 'label': 'Diesel'},
                # {'value': 'petrol', 'label': 'Petrol'},
                # {'value': 'gas', 'label': 'Natural Gas'}
            ]
            user = request.env.user
            locations = request.env['res.country.state'].sudo().search([])

            is_authenticated = user != env.ref('base.public_user')
            is_supplier = user.user_type == 'supplier'
            is_company = user.user_type == 'company'

            return request.render('energy_marketplace.bids_marketplace_template', {
                'bids': bids,
                'energy_types': energy_types,
                'locations': locations,
                'is_authenticated': is_authenticated,
                'is_supplier': is_supplier,
                'is_company': is_company,
                'user_type': 'supplier' if is_supplier else 'company',
                'user_id': user.id if is_authenticated else False,
                'filters': kw,
            })

        except Exception as e:
            _logger.exception("🔥 Bids marketplace failed")
            return f"<h1>💥 Template rendering failed: {e}</h1>"
        
    @http.route('/bids/<int:bid_id>', type='http', auth='public', website=True)
    def public_bid_details(self, bid_id, modal=False, **kw):
        bid = request.env['energy.bid'].sudo().browse(bid_id)
        if not bid.exists():
            return request.not_found()

        template = 'energy_marketplace.bid_details_modal_partial'

        return request.render(template, {
            'bid': bid
        })
    
    @http.route('/bids/<int:bid_id>/submit', type='http', auth='public', website=True, methods=['GET', 'POST'])
    def submit_supplier_bid(self, bid_id, **post):
        env = request.env
        user = env.user
        is_supplier = user.user_type == 'supplier'

        if not user or user._is_public():
            return request.redirect('/web/login')

        bid = env['energy.bid'].sudo().browse(bid_id)

        template = 'energy_marketplace.bid_submit_modal_partial'

        # Access control: Only suppliers can submit
        if not getattr(user, 'user_type', None) == 'supplier':
            return request.redirect('/web/login')
        
        _logger.info(f"User Type: {user.user_type}")

        # Safety: If bid doesn't exist
        if not bid.exists():
            return request.not_found()

        # POST: Form submission
        if request.httprequest.method == 'POST':
            # ✅ Validate amount
            raw_amount = post.get('amount')
            if not raw_amount:
                return request.render(template, {'bid': bid, 'error': 'Amount is required.'})

            try:
                amount = float(raw_amount)
                if amount <= 0:
                    raise ValueError
            except ValueError:
                return request.render(template, {'bid': bid, 'error': 'Amount must be a positive number.'})

            # ✅ Prevent duplicate bid
            existing = env['supplier.bid'].sudo().search([
                ('bid_id', '=', bid.id),
                ('supplier_id', '=', user.id),
            ], limit=1)

            if existing:
                return request.make_response(
                    json.dumps({'success': False, 'error': 'You have already submitted a bid for this request.'}),
                    headers=[('Content-Type', 'application/json')]
                )

            # ✅ Create new supplier bid
            env['supplier.bid'].sudo().create({
                'bid_id': bid.id,
                'supplier_id': user.id,
                'amount': amount,
            })

            # Success — reload the page (JS modal stays open unless handled on frontend)
            return request.make_response(
                json.dumps({'success': True, 'message': 'Bid submitted successfully.'}),
                headers=[('Content-Type', 'application/json')]
            )

        # GET: Show modal form
        return request.render(template, {'bid': bid})
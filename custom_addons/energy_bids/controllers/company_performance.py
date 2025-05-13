from odoo import http
from odoo.http import request
from collections import Counter
import logging

_logger = logging.getLogger(__name__)

class CompanyPerformanceController(http.Controller):
    @http.route('/my/performance', type='http', auth='user', website=True)
    def performance_dashboard(self, **kw):
        user = request.env.user
        if user.user_type != 'company':
            return request.redirect('/my')

        company = request.env['energy.company'].sudo().search([('user_id', '=', user.id)], limit=1)

        # Top Section: Company-specific KPIs
        company_bids = request.env['energy.bid'].sudo().search([('company_id', '=', company.id)])
        liters_ordered = sum(company_bids.mapped('volume_requested'))
        bids_created = len(company_bids)
        liters_delivered = 748  # Placeholder, depends on your logic
        overall_ranking = 1  # Placeholder for leaderboard logic

        # Middle Section: Market stats (anonymized)
        market_bids = request.env['energy.bid'].sudo().read_group(
            [], ['volume_requested'], ['energy_type']
        )
        bids_by_location = request.env['energy.bid'].sudo().read_group(
            [], ['volume_requested'], ['location']
        )

        ranking_data = request.env['energy.bid'].sudo().read_group(
            [], ['volume_requested'], ['company_id']
        )

        supplier_bids = request.env['supplier.bid'].sudo().search([]).read(['bid_id'])

        _logger.info("Total Supplier Bids fetched: %s", len(supplier_bids))
        _logger.info("Sample Supplier Bid: %s", supplier_bids[0] if supplier_bids else "None")

        bid_ids = [rec['bid_id'][0] for rec in supplier_bids if rec['bid_id']]
        bids = request.env['energy.bid'].sudo().browse(bid_ids).read(['id', 'company_id'])

        bid_to_company = {b['id']: b['company_id'][0] for b in bids if b['company_id']}

        company_counts = Counter()
        for rec in supplier_bids:
            bid_id = rec['bid_id'][0] if rec['bid_id'] else None
            company_id = bid_to_company.get(bid_id)
            if company_id:
                company_counts[company_id] += 1

        for r in ranking_data:
            company_id = r.get('company_id', [None])[0]
            r['label'] = f"PWRD Client #{100 + company_id}" if company_id else "Unknown"
            r['volume_requested'] = r.get('volume_requested', 0)
            r['supplier_bid_count'] = company_counts.get(company_id, 0)

        market_bid_breakdown = {
            'Total Bids': request.env['energy.bid'].sudo().search_count([]),
            'Cash Bids': request.env['energy.bid'].sudo().search_count([('payment_type', '=', 'cash')]),
            'Credit Bids': request.env['energy.bid'].sudo().search_count([('payment_type', '=', 'credit')]),
            'Cheque Bids': request.env['energy.bid'].sudo().search_count([('payment_type', '=', 'cheque')]),
            'Bank Transfer Bids': request.env['energy.bid'].sudo().search_count([('payment_type', '=', 'bank_transfer')]),
        }

        # Bottom Section: Bids table
        user_bids = company_bids.sorted(key=lambda b: b.create_date, reverse=True)

        return request.render('energy_bids.portal_company_performance_template', {
            'company': company,
            'bids_created': bids_created,
            'liters_ordered': liters_ordered,
            'liters_delivered': liters_delivered,
            'overall_ranking': overall_ranking,
            'market_bids': market_bids,
            'bids_by_location': bids_by_location,
            'user_bids': user_bids,
            'ranking_data': ranking_data,
            'market_bid_breakdown': market_bid_breakdown,
        })
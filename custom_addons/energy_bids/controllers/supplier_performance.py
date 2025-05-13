from odoo import http
from odoo.http import request
from datetime import datetime, timedelta
from collections import Counter
import logging

class SupplierPerformance(http.Controller):

    @http.route('/my/supplier-performance', type='http', auth='user', website=True)
    def supplier_perf_view(self):
        user = request.env.user
        if user.user_type != 'supplier':
            return request.redirect('/my')

        supplier_bids = request.env['supplier.bid'].sudo().search([('supplier_id', '=', user.id)])

        # KPIs this month
        now = datetime.now()
        first_day = now.replace(day=1)
        last_month = (first_day - timedelta(days=1)).replace(day=1)

        def get_kpi_count(domain):
            return request.env['supplier.bid'].sudo().search_count(domain)

        def get_month_kpi_count(domain, date_start, date_end):
            return request.env['supplier.bid'].sudo().search_count(domain + [
                ('create_date', '>=', date_start), ('create_date', '<=', date_end)
            ])

        # Current stats
        this_month_domain = [('supplier_id', '=', user.id), ('create_date', '>=', first_day)]
        prev_month_domain = [('supplier_id', '=', user.id), ('create_date', '>=', last_month), ('create_date', '<', first_day)]

        today = datetime.today()
        first_day_this_month = today.replace(day=1)
        first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)
        last_day_last_month = first_day_this_month - timedelta(days=1)

        # Count wins this month
        this_month_wins = request.env['supplier.bid'].sudo().search_count([
            ('supplier_id', '=', user.id),
            ('status', '=', 'approved'),
            ('submitted_at', '>=', first_day_this_month)
        ])

        # Count wins last month
        last_month_wins = request.env['supplier.bid'].sudo().search_count([
            ('supplier_id', '=', user.id),
            ('status', '=', 'approved'),
            ('submitted_at', '>=', first_day_last_month),
            ('submitted_at', '<=', last_day_last_month)
        ])

        wins_change = this_month_wins - last_month_wins

        def delta(curr, prev):
            return curr - prev

        bids_won = get_month_kpi_count([('status', '=', 'approved')], first_day, now)
        bids_lost = get_month_kpi_count([('status', '=', 'rejected')], first_day, now)
        total_bids = get_month_kpi_count([], first_day, now)

        bids_won_prev = get_month_kpi_count([('status', '=', 'approved')], last_month, first_day)
        bids_lost_prev = get_month_kpi_count([('status', '=', 'rejected')], last_month, first_day)
        total_bids_prev = get_month_kpi_count([], last_month, first_day)

        # Bids by emirate
        emirates = request.env['res.country.state'].sudo().search([])
        bids_by_emirate = []
        for em in emirates:
            total = request.env['supplier.bid'].sudo().search([
                ('supplier_id', '=', user.id),
                ('bid_id.location', '=', em.id)
            ])
            volume = sum(total.mapped('bid_id.volume_requested'))
            bids_by_emirate.append({
                'label': em.name,
                'volume': volume,
            })

        # 🔹 Count losses this month
        this_month_losses = request.env['supplier.bid'].sudo().search_count([
            ('supplier_id', '=', user.id),
            ('status', '=', 'rejected'),
            ('submitted_at', '>=', first_day_this_month)
        ])

        # 🔹 Count losses last month
        last_month_losses = request.env['supplier.bid'].sudo().search_count([
            ('supplier_id', '=', user.id),
            ('status', '=', 'rejected'),
            ('submitted_at', '>=', first_day_last_month),
            ('submitted_at', '<=', last_day_last_month)
        ])

        # 🔹 Compute delta
        losses_change = this_month_losses - last_month_losses

        # Won bids by company
        won_bids = request.env['supplier.bid'].sudo().search([
            ('supplier_id', '=', user.id),
            ('status', '=', 'approved')
        ])

        # Count total bids this month
        bids_this_month = supplier_bids.search_count([
            ('supplier_id', '=', user.id),
            ('submitted_at', '>=', first_day_this_month)
        ])

        # Count total bids last month
        bids_last_month = supplier_bids.search_count([
            ('supplier_id', '=', user.id),
            ('submitted_at', '>=', first_day_last_month),
            ('submitted_at', '<', first_day_this_month)
        ])

        bids_total_change = bids_this_month - bids_last_month

        company_volumes = {}
        for wb in won_bids:
            company_id = wb.bid_id.company_id.id
            key = f"PWRD Client #{100 + company_id}" if company_id else "Unknown"
            company_volumes[key] = company_volumes.get(key, 0) + (wb.bid_id.volume_requested or 0)
            won_by_company = [{'company_label': k, 'volume_requested': v} for k, v in company_volumes.items()]

        market_bid_breakdown = {
            'Total Bids': request.env['energy.bid'].sudo().search_count([]),
            'Cash Bids': request.env['energy.bid'].sudo().search_count([('payment_type', '=', 'cash')]),
            'Credit Bids': request.env['energy.bid'].sudo().search_count([('payment_type', '=', 'credit')]),
            'Cheque Bids': request.env['energy.bid'].sudo().search_count([('payment_type', '=', 'cheque')]),
            'Bank Transfer Bids': request.env['energy.bid'].sudo().search_count([('payment_type', '=', 'bank_transfer')]),
        }

        supplier_bid = request.env['supplier.bid'].sudo().search([]).read(['bid_id'])
        bid_ids = [rec['bid_id'][0] for rec in supplier_bid if rec['bid_id']]
        bids = request.env['energy.bid'].sudo().browse(bid_ids).read(['id', 'company_id'])
        bid_to_company = {b['id']: b['company_id'][0] for b in bids if b['company_id']}

        ranking_data = request.env['energy.bid'].sudo().read_group(
            [], ['volume_requested'], ['company_id']
        )

        company_counts = Counter()
        for rec in supplier_bid:
            bid_id = rec['bid_id'][0] if rec['bid_id'] else None
            company_id = bid_to_company.get(bid_id)
            if company_id:
                company_counts[company_id] += 1

        for r in ranking_data:
            company_id = r.get('company_id', [None])[0]
            r['label'] = f"PWRD Client #{100 + company_id}" if company_id else "Unknown"
            r['volume_requested'] = r.get('volume_requested', 0)
            r['supplier_bid_count'] = company_counts.get(company_id, 0)

        bids_by_location = request.env['energy.bid'].sudo().read_group(
            [], ['volume_requested'], ['location']
        )

        return request.render('energy_bids.performance_dashboard_supplier_template', {
            'bids_won': bids_won,
            'bids_lost': bids_lost,
            'total_bids': total_bids,
            'bids_won_delta': delta(bids_won, bids_won_prev),
            'bids_lost_delta': delta(bids_lost, bids_lost_prev),
            'bids_total_delta': delta(total_bids, total_bids_prev),
            'bids_by_emirate': bids_by_emirate,
            'won_bids': won_by_company,
            'supplier_bids': supplier_bids,
            'wins_change': wins_change,
            'this_month_losses': this_month_losses,
            'last_month_losses': last_month_losses,
            'losses_change': losses_change,
            'bids_total_change': bids_total_change,
            'bids_this_month' : bids_this_month,
            'ranking_data' : ranking_data,
            'bids_by_location' : bids_by_location,
            'market_bid_breakdown' : market_bid_breakdown,
        })
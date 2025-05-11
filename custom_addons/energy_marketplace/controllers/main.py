
from odoo import http
from odoo.http import request
from werkzeug.datastructures import MultiDict
import re
import base64
import logging

_logger = logging.getLogger(__name__)

FREE_EMAIL_DOMAINS = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com']

def is_business_email(email):
    domain = email.split('@')[-1].lower()
    return domain not in FREE_EMAIL_DOMAINS and re.match(r"[^@]+@[^@]+\.[^@]+", email)

class CompanyRegistrationWizard(http.Controller):

    @http.route('/register/check_email', type='json', auth='public', csrf=False)
    def check_email_exists(self, **kw):
        try:
            email = request.params.get('email')
            if not email:
                return {'status': 'invalid', 'reason': 'No email provided'}

            domain = email.split('@')[-1].lower()

            free_domains = request.env['energy_marketplace.free_domain'].sudo().search([]).mapped('name')

            if domain in [d.lower() for d in free_domains]:
                return {'status': 'free_email'}

            domain_used = request.env['res.users'].sudo().search([('login', 'ilike', f'%@{domain}')], limit=1)
            if domain_used:
                return {'status': 'domain_used'}

            email_used = request.env['res.users'].sudo().search([('login', 'ilike', email)], limit=1)
            if email_used:
                return {'status': 'email_taken'}

            return {'status': 'ok'}

        except Exception as e:
            _logger.error(f"Email check error: {e}")
            return {'status': 'error', 'details': str(e)}

    @http.route('/register/step1', type='http', auth='public', website=True, sitemap=False, methods=['GET', 'POST'])
    def register_step1(self, **post):
        if http.request.httprequest.method == 'POST':
            password = post.get('password')
            confirm_password = post.get('confirm_password')
            user_type = post.get('user_type', 'company')

            if not password or password != confirm_password:
                return request.render('energy_marketplace.registration_step1', {
                    'error': 'Passwords do not match. Please try again.'
                })
            
            email = post.get('email', '').lower()
            if not is_business_email(email):
                return request.render('energy_marketplace.registration_step1', {
                    'error': 'Please use a valid business email (e.g. not Gmail, Yahoo, etc.)'
                })
            request.session['step1'] = {
                'full_name': post.get('full_name'),
                'email': email,
                'phone_number': post.get('phone_number'),
                'position': post.get('position'),
                'password': password,
                'user_type': user_type,
            }
            return request.redirect('/register/step2')
        return request.render('energy_marketplace.registration_step1')

    @http.route('/register/step2', type='http', auth='public', website=True, sitemap=False, methods=['GET', 'POST'])
    def register_step2(self, **post):
        uae_country = request.env.ref('base.ae', raise_if_not_found=False)
        if not uae_country:
            uae_country = request.env['res.country'].sudo().search([('code', '=', 'AE')], limit=1)
        countries = request.env['res.country'].sudo().search([])
        post_data = MultiDict(http.request.httprequest.form)
        emirates_selected = post_data.getlist("emirate")
        
        if http.request.httprequest.method == 'POST':
            request.session['step2'] = {
                'company_name': post.get('company_name'),
                'emirate': emirates_selected,
                'company_type': post.get('company_type'),
                'country_id': int(post.get('country_id')) if post.get('country_id') else False,
                'country_name': post.get('country_name'),
            }
            return request.redirect('/register/step3')
        return request.render('energy_marketplace.registration_step2', {'countries': countries, 'uae': uae_country})

    @http.route('/register/step3', type='http', auth='public', website=True, sitemap=False, methods=['GET', 'POST'])
    def register_step3(self, **post):
        if http.request.httprequest.method == 'POST':
            request.session['step3'] = {
                'volume_required': post.get('volume_required'),
                'frequency': post.get('frequency'),
                'delivery_location': post.get('delivery_location'),
                'storage_capacity': post.get('storage_capacity'),
                'current_supplier': post.get('current_supplier'),
                'specific_grade': post.get('specific_grade'),
            }
            return request.redirect('/register/step4')
        return request.render('energy_marketplace.registration_step3')

    @http.route('/register/step4', type='http', auth='public', website=True, sitemap=False, methods=['GET', 'POST'])
    def register_step4(self, **post):
        if http.request.httprequest.method == 'POST':
            files = request.httprequest.files
            trade_file = files.get('trade_license')
            vat_file = files.get('vat_registration')

            trade_bin = vat_bin = None
            trade_fname = vat_fname = ""

            if trade_file:
                ext = trade_file.filename.split('.')[-1].lower()
                if ext not in ['pdf', 'doc', 'docx']:
                    return request.render('energy_marketplace.registration_step4', {'error': 'Trade License must be PDF or Word.'})
                trade_bin = base64.b64encode(trade_file.read()).decode()
                trade_fname = trade_file.filename

            if vat_file:
                ext = vat_file.filename.split('.')[-1].lower()
                if ext not in ['pdf', 'doc', 'docx']:
                    return request.render('energy_marketplace.registration_step4', {'error': 'VAT Registration must be PDF or Word.'})
                vat_bin = base64.b64encode(vat_file.read()).decode()
                vat_fname = vat_file.filename

            request.session['step4'] = {
                'trade_license_attachment': trade_bin,
                'trade_license_filename': trade_fname,
                'vat_registration_attachment': vat_bin,
                'vat_registration_filename': vat_fname,
            }
            return request.redirect('/register/review')
        return request.render('energy_marketplace.registration_step4')

    @http.route('/register/review', type='http', auth='public', website=True, sitemap=False, methods=['GET', 'POST'])
    def register_review(self, **post):
        if http.request.httprequest.method == 'POST':
            step1 = request.session.get('step1', {})
            step2 = request.session.get('step2', {})
            step3 = request.session.get('step3', {})
            step4 = request.session.get('step4', {})

            _logger.info(f"🌍 Country Name: {step2.get('country_id')}")

            EMIRATE_CODE_TO_STATE_ID = {
                'AD': 546,  # Abu Dhabi
                'DU': 548,  # Dubai
                'SH': 551,  # Sharjah
                'AJ': 547,  # Ajman
                'UAQ': 552, # Umm al-Quwain
                'RAK': 550, # Ras al-Khaimah
                'FU': 549   # Fujairah
            }

            EMIRATE_CODE_TO_STATE_NAME = {
                'AD': 'Abu Dhabi',
                'DU': 'Dubai',
                'SH': 'Sharjah',
                'AJ': 'Ajman',
                'UAQ':'Umm al-Quwain',
                'RAK':'Ras al-Khaimah',
                'FU': 'Fujairah'
            }

            selected_code = post.get('emirate')
            emirate_id = EMIRATE_CODE_TO_STATE_ID.get(selected_code)
            emirate_name = EMIRATE_CODE_TO_STATE_NAME.get(selected_code)

            portal_group = request.env.ref('base.group_portal')
            user = request.env['res.users'].sudo().create({
                'name': step1.get('full_name'),
                'company_name': step2.get('company_name'),
                'login': step1.get('email'),
                'phone': step1.get('phone_number'),
                'street': step3.get('delivery_location'),
                'city': emirate_name,
                'email': step1.get('email'),
                'password': step1.get('password'),
                'groups_id': [(6, 0, [portal_group.id])],
                'user_type': step1.get('user_type', 'company'),
                'country_id': step2.get('country_id'),
                'active': True,
            })

            user.partner_id.sudo().write({
                'state_id': emirate_id,
                'city': emirate_name,
                'street': step3.get('delivery_location'),
            })

            company_data = {
                'user_id': user.id,
                'user_type': step1.get('user_type'),
                'full_name': step1.get('full_name'),
                'email': step1.get('email'),
                'phone_number': step1.get('phone_number'),
                'position': step1.get('position'),
                'company_name': step2.get('company_name'),
                'emirate': step2.get('emirate'),
                'company_type': step2.get('company_type'),
                'country_id': step2.get('country_id'),
                'country_name': step2.get('country_name'),
                'volume_required': step3.get('volume_required'),
                'frequency': step3.get('frequency'),
                'delivery_location': step3.get('delivery_location'),
                'storage_capacity': step3.get('storage_capacity'),
                'current_supplier': step3.get('current_supplier'),
                'specific_grade': step3.get('specific_grade'),
                'trade_license_attachment': step4.get('trade_license_attachment'),
                'trade_license_filename': step4.get('trade_license_filename'),
                'vat_registration_attachment': step4.get('vat_registration_attachment'),
                'vat_registration_filename': step4.get('vat_registration_filename'),
                'is_approved': False
            }

            request.env['energy.company'].sudo().create(company_data)

            request.session.clear()
            return request.render('energy_marketplace.registration_pending')

        values = {}
        values.update(request.session.get('step1', {}))
        values.update(request.session.get('step2', {}))
        values.update(request.session.get('step3', {}))
        values.update(request.session.get('step4', {}))
        return request.render('energy_marketplace.registration_review', {'values': values})
    
    @http.route('/register/thankyou', type='http', auth='public', website=True, sitemap=False, methods=['GET', 'POST'])
    def register_thankyou(self):
        
        return request.render('energy_marketplace.registration_pending')
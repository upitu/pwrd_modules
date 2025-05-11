from odoo import models, fields

class EnergyCompanyProfile(models.Model):
    _name = 'energy.company.profile'
    _description = 'Company and Supplier Profile'

    user_type = fields.Selection(
        [('company', 'Company'), ('supplier', 'Supplier')],
        default='company',
        required=True,
        string="User Type"
    )

    user_id = fields.Many2one('res.users', string="User", required=True)
    is_approved = fields.Boolean(string="Is Approved", default=False)

    # Step 1
    full_name = fields.Char(required=True)
    email = fields.Char(required=True)
    phone_number = fields.Char()
    position = fields.Char()

    # Step 2
    company_name = fields.Char(required=True)
    emirate = fields.Char()
    company_type = fields.Selection([
        ('retail', 'Retail'),
        ('wholesale', 'Wholesale'),
        ('government', 'Government'),
        ('other', 'Other')
    ])
    country_id = fields.Many2one('res.country')
    country_name = fields.Char(string="Country Name")

    # Step 3
    volume_required = fields.Float()
    frequency = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ])
    delivery_location = fields.Char()
    storage_capacity = fields.Float()
    current_supplier = fields.Char()
    specific_grade = fields.Char()

    # Step 4
    trade_license_attachment = fields.Binary(string="Trade License")
    trade_license_filename = fields.Char()
    vat_registration_attachment = fields.Binary(string="VAT Registration")
    vat_registration_filename = fields.Char()

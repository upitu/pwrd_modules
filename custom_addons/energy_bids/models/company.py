from odoo import models, fields

class EnergyCompany(models.Model):
    _name = 'energy.company'
    _description = 'Energy Company'

    full_name = fields.Char(string="Full Name")
    company_name = fields.Char(string="Company Name", required=True)
    email = fields.Char(string="Email", required=True)
    phone_number = fields.Char(string="Phone Number")
    position = fields.Char(string="Position")
    emirate = fields.Char(string="Emirate")
    company_type = fields.Selection([
        ('retail', 'Retail'),
        ('wholesale', 'Wholesale'),
        ('government', 'Government'),
        ('other', 'Other')
    ], string="Company Type")
    country_id = fields.Many2one('res.country', string="Country")
    volume_required = fields.Float(string="Volume Required", digits=(12, 2))
    frequency = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ], string="Frequency")
    delivery_location = fields.Char(string="Delivery Location")
    storage_capacity = fields.Float(string="Storage Capacity", digits=(12, 2))
    current_supplier = fields.Char(string="Current Supplier")
    specific_grade = fields.Char(string="Specific Grade")
    trade_license_attachment = fields.Binary(string="Trade License")
    trade_license_filename = fields.Char(string="Trade License Filename")
    vat_registration_attachment = fields.Binary(string="VAT Registration")
    vat_registration_filename = fields.Char(string="VAT Registration Filename")
    is_approved = fields.Boolean(string="Is Approved", default=False)
    user_id = fields.Many2one('res.users', string="User", required=True)
    is_company = fields.Boolean(string="Is Company", default=True)
    company_id = fields.Many2one('res.company', string="Odoo Company", default=lambda self: self.env.company, required=True)
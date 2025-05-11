from odoo import models, fields, api

class EnergyBid(models.Model):
    _name = 'energy.bid'
    _description = 'Energy Bid Request'
    _order = 'create_date desc'

    company_id = fields.Many2one('energy.company', string="Company", required=True, ondelete='cascade')

    real_company_id = fields.Many2one('res.company', compute='_compute_real_company_id', store=False)

    supplier_bid_ids = fields.One2many('supplier.bid', 'bid_id', string="Supplier Submissions")
    
    @api.depends('company_id')
    def _compute_real_company_id(self):
        for record in self:
            record.real_company_id = record.company_id.company_id

    def _get_mail_company_id(self):
        self.ensure_one()
        return self.real_company_id
    
    energy_type = fields.Selection([
        ('diesel', 'Diesel'),
        ('petrol', 'Petrol'),
        ('gas', 'Natural Gas')
    ], string="Energy Type", required=True)
    volume_requested = fields.Float(string="Volume Requested", required=True)
    location = fields.Many2one('res.country.state', string="Location", required=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('location') and vals.get('location_id'):
                vals['location'] = vals['location_id']
        return super().create(vals_list)
    payment_type = fields.Selection([
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('cheque', 'Cheque'),
        ('bank_transfer', 'Bank Transfer')
    ], string="Payment Type", required=True)
    supply_date = fields.Date(string="Supply Date", required=True)
    preferred_hours = fields.Selection([
        ('morning', '8 AM – 12 PM'),
        ('afternoon', '12 PM – 5 PM'),
        ('evening', '5 PM – 9 PM')
    ], string="Preferred Hours", required=True)
    frequency = fields.Selection([
        ('once', 'One-Time'),
        ('weekly', 'Every Week'),
        ('monthly', 'Every Month')
    ], string="Frequency", required=True)
    status = fields.Selection([
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], string="Status", default='pending', required=True)
    user_id = fields.Many2one('res.users', string="Submitted By", default=lambda self: self.env.user, readonly=True)

    @api.model
    def get_portal_url(self):
        self.ensure_one()
        return f"/my/bids/{self.id}"
    
    def get_base_url(self):
        self.ensure_one()
        return self.env['ir.config_parameter'].sudo().get_param('web.base.url') or 'http://localhost:8069'
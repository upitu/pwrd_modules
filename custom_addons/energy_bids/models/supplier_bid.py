from odoo import models, fields

class SupplierBid(models.Model):
    _name = 'supplier.bid'
    _description = 'Supplier Bid'

    bid_id = fields.Many2one('energy.bid', string='Bid', required=True, ondelete='cascade')
    supplier_id = fields.Many2one('res.users', required=True, default=lambda self: self.env.user)
    amount = fields.Float(string='Bid Amount', required=True)
    submitted_at = fields.Datetime(default=fields.Datetime.now, readonly=True)
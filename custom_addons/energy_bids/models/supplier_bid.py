from odoo import models, fields, api

class SupplierBid(models.Model):
    _name = 'supplier.bid'
    _description = 'Supplier Bid'

    bid_id = fields.Many2one('energy.bid', string='Bid', required=True, ondelete='cascade')
    supplier_id = fields.Many2one('res.users', required=True, default=lambda self: self.env.user)
    amount = fields.Float(string='Bid Amount', required=True)
    submitted_at = fields.Datetime(default=fields.Datetime.now, readonly=True)
    status = fields.Selection([
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='submitted', string='Status', required=True)

    @api.model
    def create(self, vals):
        bid = super().create(vals)
        # Ensure no more than one approved per bid
        if bid.status == 'approved':
            bid.reject_others()
        return bid

    def write(self, vals):
        result = super().write(vals)
        if 'status' in vals and vals['status'] == 'approved':
            self.reject_others()
        return result

    def reject_others(self):
        """Reject all other bids on the same bid_id except self."""
        self.ensure_one()
        other_bids = self.sudo().search([
            ('bid_id', '=', self.bid_id.id),
            ('id', '!=', self.id),
            ('status', '!=', 'rejected')
        ])
        other_bids.write({'status': 'rejected'})
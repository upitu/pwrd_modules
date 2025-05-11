from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    user_type = fields.Selection([
        ('company', 'Company'),
        ('supplier', 'Supplier'),
    ], string="User Type", default='company')
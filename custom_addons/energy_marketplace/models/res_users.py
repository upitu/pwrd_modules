from odoo import models, fields

EMIRATE_SELECTION = [
    ('abu_dhabi', 'Abu Dhabi'),
    ('dubai', 'Dubai'),
    ('sharjah', 'Sharjah'),
    ('ajman', 'Ajman'),
    ('umm_al_quwain', 'Umm Al Quwain'),
    ('ras_al_khaimah', 'Ras Al Khaimah'),
    ('fujairah', 'Fujairah'),
]

class ResUsers(models.Model):
    _inherit = 'res.users'

    user_type = fields.Selection([
        ('company', 'Company'),
        ('supplier', 'Supplier')
    ], string="User Type", default='company')

    emirates_allowed = fields.Many2many(
        'res.country.state',
        string='Allowed Emirates',
        domain="[('country_id.code', '=', 'AE')]"
    )
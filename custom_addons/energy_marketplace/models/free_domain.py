from odoo import models, fields

class FreeDomain(models.Model):
    _name = 'energy_marketplace.free_domain'
    _description = 'Free Email Domains Blocked for Registration'

    name = fields.Char(string="Domain Name", required=True, help="Example: gmail.com")
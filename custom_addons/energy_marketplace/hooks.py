from odoo.api import Environment, SUPERUSER_ID

def post_init_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})

    # Ensure UAE exists
    uae = env['res.country'].search([('code', '=', 'AE')], limit=1)
    if not uae:
        uae = env['res.country'].create({'name': 'United Arab Emirates', 'code': 'AE'})

    emirates = [
        ('Abu Dhabi', 'AD'),
        ('Dubai', 'DU'),
        ('Sharjah', 'SH'),
        ('Ajman', 'AJ'),
        ('Umm Al Quwain', 'UAQ'),
        ('Ras Al Khaimah', 'RAK'),
        ('Fujairah', 'FU'),
    ]

    for name, code in emirates:
        existing = env['res.country.state'].search([('code', '=', code), ('country_id', '=', uae.id)], limit=1)
        if not existing:
            env['res.country.state'].create({
                'name': name,
                'code': code,
                'country_id': uae.id,
            })

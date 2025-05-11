{
    "name": "Energy Bids",
    "version": "1.1.3",
    "summary": "Bidding system for energy supply companies",
    'author': 'Elias El Hajj',
    "website": 'https://www.digitaljunkies.ae',
    "depends": ["base", "website", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/supplier_bid_model.xml",
        "views/company_model.xml",
        "views/bid_templates.xml",
        "views/email_template.xml"
    ],
    "assets": {
        "web.assets_frontend": [
            "energy_bids/static/src/css/bids_full.css"
        ],
    },
    "installable": True,
    "application": True,
    "license": "LGPL-3"
}
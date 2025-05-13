{
    "name": "Energy Bids",
    "version": "1.1.3",
    "summary": "Bidding system for energy supply companies",
    "author": "Elias El Hajj",
    "website": "https://www.digitaljunkies.ae",
    "depends": ["base", "website", "mail", "portal"],
    "data": [
        "security/ir.model.access.csv",
        "views/supplier_bid_model.xml",
        "views/assets.xml",
        "views/company_model.xml",
        "views/bid_templates.xml",
        "views/email_template.xml",
        "views/portal_supplier_bids_template.xml",
        "views/performance_dashboard_template.xml",
        "views/performance_dashboard_supplier_template.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "energy_bids/static/src/css/bids_full.css",
            'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js',
            'https://unpkg.com/leaflet@1.9.3/dist/leaflet.css',
            'https://unpkg.com/leaflet@1.9.3/dist/leaflet.js',
            'energy_bids/static/src/js/leaflet_location_picker.js',
        ],
    },
    "installable": True,
    "application": True,
    "license": "LGPL-3"
}
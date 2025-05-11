from odoo import http

class TestHelloController(http.Controller):
    @http.route('/test/hello', type='http', auth='public', website=True)
    def test_hello(self, **kw):
        return "<h1>Hello from Odoo</h1>"
# -*- coding: utf-8 -*-
# from odoo import http


# class AlmoudiExtended(http.Controller):
#     @http.route('/almoudi_extended/almoudi_extended/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/almoudi_extended/almoudi_extended/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('almoudi_extended.listing', {
#             'root': '/almoudi_extended/almoudi_extended',
#             'objects': http.request.env['almoudi_extended.almoudi_extended'].search([]),
#         })

#     @http.route('/almoudi_extended/almoudi_extended/objects/<model("almoudi_extended.almoudi_extended"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('almoudi_extended.object', {
#             'object': obj
#         })

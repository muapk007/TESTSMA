from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import json
# from odoo.osv.orm import setup_modifiers

from lxml import etree
class SaleOrderWizard(models.TransientModel):
    _name = 'sale.order.wizard'

    def action_to_approved(self):
        model = self.env.context.get('active_model')
        rec_model = self.env[model].browse(self.env.context.get('active_id'))
         
#         obj = self.env['sale.order'].search([('id', '=', rec_model.id)])
#         if not obj:
        obj = self.env['sale.order'].search([('id', '=', self.env.context['sale_id'])])
        margin = obj.margin_percent * 100
        today = date.today()
        if((obj.amount_total<= obj.available_amount or obj.cr_approve == True ) and (float(margin) >= obj.allowed_margin or obj.margin_approve == True)\
           and (today <= obj.credit_date or obj.expiry_approve == True) and (today <= obj.baldiya_date or obj.baldiya_approve == True)):
            return obj.action_confirm()
        else:
            if self.env.context.get('message', False):
                con_message = self.env.context.get('message')
                if con_message == 'greater Amount':
                    obj.cr_approve = True
                    obj.state = "approved"
                    return obj.action_show_sale_products()
                elif con_message == 'cr expired':
                    obj.expiry_approve = True
                    obj.state = "date_approved"
                    return obj.action_show_sale_products()
    
                elif con_message == 'baldiya expired':
                    obj.baldiya_approve = True
                    obj.state = "baldiya_approved"
                    return obj.action_show_sale_products()
                elif con_message == 'greater margin':
                    obj.margin_approve = True
                    obj.state = "margin"
                    return obj.action_show_sale_products()


class AccountPaymentInh(models.Model):
    _inherit = 'account.payment'
    origin_no = fields.Char(string="Origin")

    def action_post(self):
        res = super(AccountPaymentInh, self).action_post()
        self._onchange_payments()
        return res

    def _onchange_payments(self):
        model = self.env.context.get('active_model')
        rec_model = self.env[model].browse(self.env.context.get('active_id'))
        obj = self.env['account.move'].sudo().search([('id', '=', rec_model.id)])
        if not self.origin_no:
            self.origin_no = obj.invoice_origin


class users_inherit(models.Model):
    _inherit = 'res.users'
    _description = 'adding to users table'

    allowed_margin = fields.Float(string='Allowed Margin %')
    default_stock_warehouse = fields.Many2one("stock.warehouse", string='Default Warehouse')

    @api.constrains("allowed_margin")
    def check_margin_percent(self):
        if self.allowed_margin > 100:
            raise UserError(
                _('Margin cannot be greater than 100%'))


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    available_qty = fields.Float('Available Quantity')

    @api.onchange("product_id")
    def onchange_available_qty(self):
        total = 0
        branch_id = self.order_id.logged_user_id.branch_id.default_stock_warehouse.code
        print("branch_id", branch_id)
        for i in self:
            obj = self.env['stock.quant'].search(
                [('product_id', '=', i.product_id.id), ('location_id.location_id.name', '=', branch_id)])
            for j in obj:
                print(j.location_id.location_id.name)
                total = total + j.available_quantity
            i.available_qty = total


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    credit_date = fields.Date('Expiry CR Date', related="partner_id.expiry_crdate")
    baldiya_date = fields.Date('Baldiya Expiry Date', related="partner_id.gov_number_expiry_date")
    credit_amount = fields.Float('Credit Limit', related="partner_id.credit_limit")
    total_sale_amount = fields.Float('Last Payments')
    available_amount = fields.Float('Available Credit')
    total_due = fields.Float('Total Due')
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('manager', 'Approval from Manager'), ('margin', 'Margin Approved'), ('approved', 'Credit Approved'),
        ('date_approved', 'Date Approved'), ('baldiya_approved', 'Baldiya Approved'),
        ('final_approve','Approved'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    allowed_margin = fields.Float(string='Allowed Margin %', related='logged_user_id.allowed_margin')
    logged_user_id = fields.Many2one('res.users', string='User', compute="compute_self_id", store="True")
    cr_approve = fields.Boolean("cr approve", default=False)
    baldiya_approve = fields.Boolean("baldiya approve", default=False)
    expiry_approve = fields.Boolean("expiry approve", default=False)
    margin_approve = fields.Boolean("margin approve", default=False)
    check = fields.Boolean("Check")
    btn_approved_check = fields.Boolean("btn Approved check")
    
    
    @api.model
    def create(self, values):
        res = super(SaleOrder, self).create(values)
        res.check=True
        res.btn_approved_check = True
        return res

    
    
    
    @api.onchange("partner_id")
    def _onchangethe_total_due(self):
        total = 0
        obj = self.env['account.move'].sudo().search(
            [('partner_id', '=', self.partner_id.id), ('state', 'in', ['posted'])])
        for j in obj:
            total = total + j.amount_residual
        self.total_due = total

    @api.onchange("partner_id")
    def _onchange_the_total_amount_received(self):
        today = date.today()
        last = today - timedelta(3 * 365.25 / 12)
        list = []
        total = 0
        obj = self.env['account.payment'].sudo().search(
            [('partner_id', '=', self.partner_id.id), ('state', 'in', ['posted'])])
        for j in obj:
            if j.date >= last and j.date <= today:
                total = total + j.amount
        self.total_sale_amount = total

    @api.onchange("total_due", "partner_id")
    def _onchange_the_total_amount(self):
        self.available_amount = self.credit_amount - self.total_due

    @api.depends("partner_id")
    def compute_self_id(self):
        self.logged_user_id = self.env.uid

    def from_manager_approval(self):
        self.state = 'manager'

    def mark_as_approved(self):
        self.state = 'approved'
    
    
    
  
    
    
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(SaleOrder, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if self.env.user.has_group('almoudi_extended.group_credit_sales_manager'):
            if view_type == 'form':
                  
     
                doc = etree.XML(res['arch'])
    #             for field in res['fields']:
                for node in doc.xpath("//button[@name='from_manager_approval']"):
    #                 node.set("invisible", "1")
                    modifiers = json.loads(node.get("modifiers"))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
                res['arch'] = etree.tostring(doc)
# 
        return res




    def action_confirm(self):
        # just confirming so
        res = super(SaleOrder, self).action_confirm()
        return res
     # just confirming so
#         margin = self.margin_percent * 100
#         today = date.today()
#         if self.partner_id.is_credit:
# 
#             if not self.env.user.has_group('almoudi_extended.group_credit_sales_manager'):
#                 if float(margin) <= self.allowed_margin and self.margin_approve == False:
#                     raise UserError(
#                         _('Your Margin is Less than allowed Margin.Click on "Ask for Approval" for approval.'))
# 
#             if not self.env.user.has_group(
#                     'almoudi_extended.group_credit_sales_manager') and self.amount_total >= self.available_amount and self.cr_approve == False:
#                 raise ValidationError(
#                     _('Sale Order Total amount exceeds Credit Limit. Please take approval from Manager.'))
# 
#             if not self.env.user.has_group(
#                     'almoudi_extended.group_credit_sales_manager') and today >= self.credit_date and self.expiry_approve == False:
#                 raise ValidationError(_('CR Date is expired. Please take approval from Manager.'))
# 
#             if not self.env.user.has_group(
#                     'almoudi_extended.group_credit_sales_manager') and today >= self.baldiya_date and self.baldiya_approve == False:
#                 raise ValidationError(_('Baldiya Date is expired. Please take approval from Manager.'))
# 
# 
#             else:
#                 return super(SaleOrder, self).action_confirm()
#         #
#         #             if self.state != 'approved' and not self.state =='baldiya_approved':
#         #                 if not self.env.user.has_group('almoudi_extended.group_credit_sales_manager') and self.amount_total >= self.available_amount:
#         #                     raise ValidationError(_('Sale Order Total amount exceeds Credit Limit. Please take approval from Manager.'))
#         #
#         #             if self.state != 'approved'  and not self.state =='baldiya_approved':
#         #                 if not self.env.user.has_group('almoudi_extended.group_credit_sales_manager') and today >= self.credit_date:
#         #                     raise ValidationError(_('CR Date is expired. Please take approval from Manager.'))
#         #
#         #             if self.state != 'approved'  and self.state =='baldiya_approved':
#         #                 if not self.env.user.has_group('almoudi_extended.group_credit_sales_manager') and today >= self.baldiya_date:
#         #                     raise ValidationError(_('Baldiya Date is expired. Please take approval from Manager.'))
#         #
#         #             if self.env.user.has_group('almoudi_extended.group_credit_sales_manager'):
#         #                 return  super(SaleOrder, self).action_confirm()
#         #             else:
#         #                 if today >= self.credit_date:
#         #                     self.state = 'date_approved'
#         #
#         #                 if today >= self.baldiya_date:
#         #                     self.state = 'baldiya_approved'
#         #                 return  super(SaleOrder, self).action_confirm()
#         else:
#             return super(SaleOrder, self).action_confirm()

    def action_show_sale_products(self):
        margin = self.margin_percent * 100
        today = date.today()
        name = "Approval"
        if self.partner_id.is_credit:
            if((self.amount_total<= self.available_amount or self.cr_approve == True ) and (float(margin) >= self.allowed_margin or self.margin_approve == True)\
               and (today <= self.credit_date or self.expiry_approve == True) and (today <= self.baldiya_date or self.baldiya_approve == True)):
#                 return self.action_confirm()
                self.state= 'final_approve'        
            else:
                if float(margin) <= self.allowed_margin and self.margin_approve == False:
                    name = "Margin Approval"
                    context = {'message': 'greater margin' ,'sale_id': self.id}
        
                    view_id = self.env.ref('almoudi_extended.view_sale_order_wizard_form', False).id
                elif self.amount_total >= self.available_amount and self.cr_approve == False:
                    context = {'message': 'greater Amount'  ,'sale_id': self.id}
                    name = "Sale Order Amount greater than available credit"
                    view_id = self.env.ref('almoudi_extended.view_credit_limit_wizard_form', False).id
                elif today >= self.credit_date and self.expiry_approve == False:
                    context = {'message': 'cr expired'  ,'sale_id': self.id}
                    name = "CR expired Approval"
                    view_id = self.env.ref('almoudi_extended.view_cr_expired_wizard_form', False).id
        
                elif today >= self.baldiya_date and self.baldiya_approve == False:
                    context = {'message': 'baldiya expired'  ,'sale_id': self.id}
                    name = "Expired Gov Document"
                    view_id = self.env.ref('almoudi_extended.view_govt_expired_wizard_form', False).id
        
                return {
                    'type': 'ir.actions.act_window',
                    'name': name,
                    'view_id': view_id,
                    'target': 'new',
                    'res_model': 'sale.order.wizard',
                    'view_mode': 'form',
                    'context': context
                }
        else:
            return  self.action_confirm()
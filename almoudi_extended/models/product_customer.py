from odoo import models, fields, api, _
from datetime import datetime, timedelta
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import exceptions


class TelenocProduct(models.Model):
    _inherit = "product.template"

    aswaq_code = fields.Char(string="ASWAQ CODE")
    categ_description_eng = fields.Char(string="Category Description English")
    series_cat_id = fields.Many2one("series.category", string="SERIES CAT.")
    radial_id = fields.Many2one("series.radial", string="Radial")
    pattern_id = fields.Many2one("series.pattern", string="Pattern")
    short_series_id = fields.Many2one("short.series.category", string="SHORT SERIES CAT")
    product_types_id = fields.Many2one("series.product.type", string="Item Type")
    brand_id = fields.Many2one("series.product.brand", string="Brand")
    manufacturer_id = fields.Many2one("fleet.vehicle.model.brand", string="Manufacturer")
    main_vendor = fields.Char(string="Main Vendor")
    c_unit_r = fields.Char(string="CUnitR")
    container_qty = fields.Integer(String="Container_qty")
    prd_standard_price = fields.Float(string="Product Standard Price ")
    prd_average_cost = fields.Float(string="Product Average Cost")
    five_digits = fields.Integer(string="5 Digits", size=5)
    eight_digits = fields.Integer(string="8 Digits", size=8)
    performance_categ_id = fields.Many2one("performance.category", string="Performance Category")
    speed_symbol_id = fields.Many2one("speed.symbol", string="Speed symbol")
    tread_depth = fields.Float(string="Original tread depth")
    tread_wear = fields.Char(string="Tread Wear")
    traction_id = fields.Many2one("traction.control.system", string="Traction")
    temperature_id = fields.Many2one("temperature.control.system", string="Temperature")
    oere_id = fields.Many2one("original.equipment", string="OE/RE")
    origin_id = fields.Many2one("product.origins", string="Origin")
    oe = fields.Float(string="O.D")
    tube_type_id = fields.Many2one("tube.type", string="Tube type")
    road_type_ids = fields.Many2many("road.type", 'road_product_rel', 'road_id', 'product_id', string="Road type")
    rim_one_id = fields.Many2one("rim.position.one", string="Rim Position One")
    rim_two_id = fields.Many2one("rim.position.two", string="Rim Position Two")
    inflation = fields.Char(string="Inflation")
    star_rating = fields.Selection([
        ('no_star', ''),
        ('one_star', '*'),
        ('two_stars', '**'),
        ('three_stars', '***'),
        ('four_stars', '****'),
        ('five_stars', '*****')],
        string='Star Rating')
    max_size = fields.Many2one("product.size", string="Main size")
    load_range = fields.Many2one("load.range", string="Load range")
    load_index_single = fields.Many2one("index.single", string="LOAD INDEX SINGLE")


class SeriesCateg(models.Model):
    _name = "series.category"

    name = fields.Char(string="name")


class SeriesRadial(models.Model):
    _name = "series.radial"

    name = fields.Char(string="name")


class SeriesPattern(models.Model):
    _name = "series.pattern"

    name = fields.Char(string="name")


class ShortSeriesCategory(models.Model):
    _name = "short.series.category"

    name = fields.Char(string="name")


class SeriesProductType(models.Model):
    _name = "series.product.type"

    name = fields.Char(string="name")


class SeriesProductBrand(models.Model):
    _name = "series.product.brand"

    name = fields.Char(string="name")


class PerformanceCategory(models.Model):
    _name = "performance.category"

    name = fields.Char(string="name")


class SpeedSymbol(models.Model):
    _name = "speed.symbol"

    name = fields.Char(string="name")


class TractionControlSystem(models.Model):
    _name = "traction.control.system"

    name = fields.Char(string="name")


class TemperatureControlSystem(models.Model):
    _name = "temperature.control.system"

    name = fields.Char(string="name")


class OeRe(models.Model):
    _name = "original.equipment"

    name = fields.Char(string="name")


class ProductOrigin(models.Model):
    _name = "product.origins"

    name = fields.Char(string="name")


class TubeType(models.Model):
    _name = "tube.type"

    name = fields.Char(string="name")


class RoadType(models.Model):
    _name = "road.type"

    name = fields.Char(string="name")


class RimPositionOne(models.Model):
    _name = "rim.position.one"

    name = fields.Char(string="name")


class RimPositionTwo(models.Model):
    _name = "rim.position.two"

    name = fields.Char(string="name")


class Showroom(models.Model):
    _name = "customer.showroom"

    name = fields.Char(string="name")


class BrandCategory(models.Model):
    _name = "brand.category"

    name = fields.Char(string="name")


class AccountManager(models.Model):
    _name = "account.manager"

    name = fields.Char(string="name")


class SubCategory(models.Model):
    _name = "sub.category"

    name = fields.Char(string="name")


class ProductMainSize(models.Model):
    _name = "product.size"

    name = fields.Char(string="MAIN SIZE (R)")
    width = fields.Float(string="Width")
    aspect_ratio = fields.Float(string="Aspect Ratio")
    rim = fields.Float(string="Rim inch")


class LoadRange(models.Model):
    _name = "load.range"

    name = fields.Char(string="Load Range")
    ply_rating = fields.Float(string="Ply Rating")


class LoadIndexSingle(models.Model):
    _name = "index.single"

    name = fields.Char(string="Load index single")
    max_load = fields.Float(string="Max load")
    load_index_dual = fields.Float(string="Load Index Dual")


class TelenocCustomer(models.Model):
    _inherit = "res.partner"

    showroom_id = fields.Many2one('customer.showroom', string="Showroom")
    years_of_relation = fields.Char('Years of relationship', compute="get_years_of_relation")
    customer_status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ],
        string='Customer Status')
    brand_id = fields.Many2one("series.product.brand", string="Brand")
    brand_category_id = fields.Many2one("brand.category", string="Brand category")
    account_manger_id = fields.Many2one("account.manager", string="Account Manager")
    sub_category_id = fields.Many2one("sub.category", string="Sub Category")
    is_credit = fields.Boolean(string="Credit")
    is_cash = fields.Boolean(string="Cash")
    cr_number = fields.Char(string="CR Number")
    start_crdate = fields.Date("Start CR Date")
    expiry_crdate = fields.Date("Expiry CR Date")
    gov_number = fields.Char(string="Gov number2")
    gov_number_expiry_date = fields.Date("Gov. number Expiry Date")
    credit_period = fields.Integer('Credit Period')
    credit_limit = fields.Float('Credit limit')
    create_date_cr = fields.Datetime("Create Date", default=lambda self: fields.Datetime.now())
    industry_sub_category_id = fields.Many2many("sub.category", string="Sub Category industry")
    
    @api.onchange('industry_id')
    def onchange_industry_id(self):
        for res in self:
            res.sub_category_id =False
            res.industry_sub_category_id 
            if res.industry_id:
                same_name_recs= res.industry_id.search([('name','=',res.industry_id.name)])
                sub_categories= same_name_recs.mapped('sub_category_id')
                res.industry_sub_category_id = sub_categories
                categ_domain = "[('id','in',sub_categories)]"
#                 res.industry_sub_category_id =  
#                 domain = {'domain': {'sub_category_id': [('id', 'in', sub_categories.ids)]}}
#                 domain = {'domain': {'industry_sub_category_id': [('id', 'in', sub_categories.ids)]}}
#                 return domain
#                 res.update({'industry_sub_category_id':})
                
    
    
    def get_years_of_relation(self):
        for rec in self:
            rec_create_date = rec.create_date_cr
            current_date = datetime.now()
            years_diff = (current_date.year - rec_create_date.year)
            year = int((current_date - rec_create_date).days / 365.2425)
            month_diff = (current_date.month - rec_create_date.month)
            rec.years_of_relation = '{0}Y{1}M'.format(year, month_diff)

    @api.constrains('start_crdate', 'expiry_crdate')
    def _check_validity_check_in_check_out(self):
        """ verifies if expiry_crdate is earlier than start_crdate. """
        #         if self.expiry_crdate <=self.start_crdate:
        #                 raise exceptions.ValidationError(_('Expiry CR Date cannot be less or  equal than Start CR Date.'))
        if self.start_crdate >= self.expiry_crdate:
            raise exceptions.ValidationError(_('Start CR Date cannot be greater or equal than Expiry CR Date.'))


class IndustrySubCategory(models.Model):
    _inherit = "res.partner.industry"

    sub_category_id = fields.Many2one("sub.category", string="Sub Category")



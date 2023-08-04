

from odoo import api, Command, fields, models, _
from odoo.exceptions import ValidationError, UserError

class Company(models.Model):
    _inherit = 'res.company'

    sale_unique_product = fields.Boolean(string="Activate Unique Sale order products")
    purchase_unique_product = fields.Boolean(string="Activate Unique purchase order products")
    invoice_unique_product = fields.Boolean(string="Activate Unique Invoice products")
    bill_unique_product = fields.Boolean(string="Activate Unique Bill products")

class SaleOrder(models.Model):
    _inherit = 'sale.order'


    def _compute_sale_unique_product(self):
        company = self.env.company
        if company.sale_unique_product:
            self.sale_unique_product = True
        else:
            self.sale_unique_product = False

    sale_unique_product = fields.Boolean(default='_compute_sale_unique_product',store=True,string="Activate Unique Sale order products",readonly=False)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    @api.constrains('product_id')
    def _check_product_id_unique(self):
        for move in self:
            if move.order_id.sale_unique_product:
                results = move.search_count([('product_id', '=', move.product_id.id), ('order_id', '=', move.order_id.id)])
                if results > 1:
                    raise ValidationError(_('product number already exists!. (Product Name: %s)', move.name))



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    def _compute_purchase_unique_product(self):
        company = self.env.company
        if company.purchase_unique_product:
            self.purchase_unique_product = True
        else:
            self.purchase_unique_product = False

    purchase_unique_product = fields.Boolean(default='_compute_purchase_unique_product',store=True,string="Activate Unique Purchase order products",readonly=False)

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.constrains('product_id')
    def _check_product_id_unique(self):
        for move in self:
            if move.order_id.purchase_unique_product:
                results = move.search_count([('product_id', '=', move.product_id.id), ('order_id', '=', move.order_id.id)])
                if results > 1:
                    raise ValidationError(_('product number already exists!. (Product Name: %s)', move.name))


class AccountMove(models.Model):
    _inherit = 'account.move'


    @api.model
    def compute_bill_unique_product(self):
        return self.env.company.bill_unique_product


    @api.model
    def compute_invoice_unique_product(self):
        return self.env.company.invoice_unique_product


    invoice_unique_product = fields.Boolean(default=compute_invoice_unique_product,store=True,string="Activate Unique Invoice products",readonly=False)


    bill_unique_product = fields.Boolean(default=compute_bill_unique_product,store=True,string="Activate Unique Bill products",readonly=False)


    @api.constrains('state','invoice_line_ids.product_id','invoice_unique_product','bill_unique_product','move_type')
    def _check_product_id_unique(self):
        for move in self:
            if move.is_sale_document(include_receipts=True) and move.state =='draft':
                if move.invoice_unique_product and  len(move.invoice_line_ids) > 0:
                    for line in move.invoice_line_ids.filtered(lambda x: x.display_type not in ('line_section', 'line_note')):
                        results1 = line.search_count([('product_id', '=', line.product_id.id), ('move_id', '=', line.move_id.id)])
                        if results1 > 1:
                            raise ValidationError(_('product number already exists!. (Product Name: %s)', line.product_id.name))
            if move.is_purchase_document(include_receipts=True) and move.state =='draft':
                if move.bill_unique_product and  len(move.invoice_line_ids) > 0:
                    for line in move.invoice_line_ids.filtered(lambda x: x.display_type not in ('line_section', 'line_note')):
                        results2 = line.search_count([('product_id', '=', line.product_id.id), ('move_id', '=', line.move_id.id)])
                        if results2 > 1:
                            raise ValidationError(_('product number already exists!. (Product Name: %s)', line.product_id.name))
                 

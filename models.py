from odoo import models, fields

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_authorized = fields.Boolean(string='Autorizado', default=False)


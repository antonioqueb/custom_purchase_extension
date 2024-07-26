from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_authorized = fields.Boolean(string='Autorizado', default=False)

    @api.multi
    def write(self, vals):
        if 'is_authorized' in vals:
            for record in self:
                old_value = record.is_authorized
                new_value = vals['is_authorized']
                if old_value != new_value:
                    message = "Authorization status changed from %s to %s" % (old_value, new_value)
                    record.message_post(body=message)
        return super(PurchaseOrder, self).write(vals)

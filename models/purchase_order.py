from odoo import models, fields, api, SUPERUSER_ID

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_authorized = fields.Boolean(string='Autorizado', default=False)

    @api.model
    def create(self, vals):
        record = super(PurchaseOrder, self).create(vals)
        if 'is_authorized' in vals:
            self._log_authorization_change(record)
        return record

    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        if 'is_authorized' in vals:
            for record in self:
                self._log_authorization_change(record)
        return res

    def _log_authorization_change(self, record):
        message = "Authorization status changed to: {}".format('Authorized' if record.is_authorized else 'Not Authorized')
        record.message_post(body=message)

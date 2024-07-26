from odoo import models, fields, api
from datetime import datetime

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_authorized = fields.Boolean(string='Autorizado', default=False)

    @api.model
    def create(self, vals):
        record = super(PurchaseOrder, self).create(vals)
        if 'is_authorized' in vals:
            self._log_authorization_change(record, vals['is_authorized'])
        return record

    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        if 'is_authorized' in vals:
            for record in self:
                self._log_authorization_change(record, vals['is_authorized'])
        return res

    def _log_authorization_change(self, record, new_value):
        user = self.env.user
        timestamp = fields.Datetime.now()
        message = "El estado de autorización cambió a: {} por {} el {}".format(
            'Autorizado' if new_value else 'No Autorizado',
            user.name,
            timestamp
        )
        record.message_post(body=message)

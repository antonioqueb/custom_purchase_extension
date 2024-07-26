from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_authorized = fields.Boolean(string='Autorizado', default=False)

    @api.model
    def create(self, vals):
        record = super(PurchaseOrder, self).create(vals)
        if 'is_authorized' in vals:
            self._log_authorization_change(record, vals['is_authorized'])
        self._update_sequence_prefix(record)
        return record

    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        if 'is_authorized' in vals:
            for record in self:
                self._log_authorization_change(record, vals['is_authorized'])
        for record in self:
            self._update_sequence_prefix(record)
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

    def _update_sequence_prefix(self, record):
        if not record.is_authorized:
            record.name = self.env['ir.sequence'].next_by_code('purchase.order.draft') or 'RDM'
        elif record.state == 'purchase':
            record.name = self.env['ir.sequence'].next_by_code('purchase.order.confirmed') or 'OC'
        elif record.state == 'done':
            record.name = self.env['ir.sequence'].next_by_code('purchase.order.done') or 'PC'

    def action_set_done(self):
        for order in self:
            order.state = 'done'
            order._update_sequence_prefix()

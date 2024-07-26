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
        if self.env.context.get('skip_update_prefix'):
            return super(PurchaseOrder, self).write(vals)

        res = super(PurchaseOrder, self).write(vals)
        if 'is_authorized' in vals:
            for record in self:
                old_prefix = self._get_current_prefix(record)
                self._log_authorization_change(record, vals['is_authorized'])
                self._update_sequence_prefix(record)
                new_prefix = self._get_current_prefix(record)
                if old_prefix != new_prefix:
                    self._log_prefix_change(record, old_prefix, new_prefix)
        else:
            for record in self:
                old_prefix = self._get_current_prefix(record)
                self._update_sequence_prefix(record)
                new_prefix = self._get_current_prefix(record)
                if old_prefix != new_prefix:
                    self._log_prefix_change(record, old_prefix, new_prefix)
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
        new_name = None
        current_prefix = self._get_current_prefix(record)

        if not record.is_authorized and current_prefix != 'RDM':
            new_name = self.env['ir.sequence'].next_by_code('purchase.order.draft')
        elif record.is_authorized and current_prefix == 'RDM':
            new_name = record.name.replace('RDM', 'OC')
        elif record.state == 'purchase' and current_prefix == 'OC':
            new_name = record.name.replace('OC', 'PC')

        if new_name:
            record.with_context(skip_update_prefix=True).write({'name': new_name})
            record.message_post(body="Nombre actualizado a: {}".format(new_name))

    def _get_current_prefix(self, record):
        if record.name.startswith('RDM'):
            return 'RDM'
        elif record.name.startswith('OC'):
            return 'OC'
        elif record.name.startswith('PC'):
            return 'PC'
        return ''

    def _log_prefix_change(self, record, old_prefix, new_prefix):
        user = self.env.user
        timestamp = fields.Datetime.now()
        message = "El prefijo de la orden cambió de: {} a {} por {} el {}".format(
            old_prefix,
            new_prefix,
            user.name,
            timestamp
        )
        record.message_post(body=message)

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            old_prefix = self._get_current_prefix(order)
            self._update_sequence_prefix(order)
            new_prefix = self._get_current_prefix(order)
            if old_prefix != new_prefix:
                self._log_prefix_change(order, old_prefix, new_prefix)
        return res

    def action_set_done(self):
        for order in self:
            order.state = 'done'
            old_prefix = self._get_current_prefix(order)
            self._update_sequence_prefix(order)
            new_prefix = self._get_current_prefix(order)
            if old_prefix != new_prefix:
                self._log_prefix_change(order, old_prefix, new_prefix)

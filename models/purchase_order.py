from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_authorized = fields.Boolean(string='Autorizado', default=False)
    planta = fields.Selection([
        ('planta_1', 'Planta 1'),
        ('planta_2', 'Planta 2'),
        ('planta_3', 'Planta 3'),
        ('planta_4', 'Planta 4'),
        ('planta_5', 'Planta 5'),
        ('planta_6', 'Planta 6'),
    ], string='Planta', default='planta_1')

    @api.model
    def create(self, vals):
        record = super(PurchaseOrder, self).create(vals)
        self._update_sequence_prefix(record)
        if 'planta' in vals:
            self._log_planta_change(record, vals['planta'])
        return record

    def write(self, vals):
        if self.env.context.get('skip_update_prefix'):
            return super(PurchaseOrder, self).write(vals)

        old_prefixes = {record.id: self._get_current_prefix(record) for record in self}

        res = super(PurchaseOrder, self).write(vals)

        for record in self:
            if 'is_authorized' in vals:
                self._log_authorization_change(record, vals['is_authorized'])

            if 'planta' in vals:
                self._log_planta_change(record, vals['planta'])

            new_prefix = self._get_current_prefix(record)
            if old_prefixes[record.id] != new_prefix:
                self._log_prefix_change(record, old_prefixes[record.id], new_prefix)
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

    def _log_planta_change(self, record, new_value):
        user = self.env.user
        timestamp = fields.Datetime.now()
        message = "La planta se cambió a: {} por {} el {}".format(
            dict(record._fields['planta'].selection).get(new_value),
            user.name,
            timestamp
        )
        record.message_post(body=message)

    def _update_sequence_prefix(self, record):
        new_name = None
        if not record.is_authorized and not record.name.startswith('RDM'):
            new_name = self.env['ir.sequence'].next_by_code('purchase.order.draft')
        elif record.is_authorized and record.name.startswith('RDM'):
            new_name = record.name.replace('RDM', 'OC')
        elif record.state == 'purchase' and record.name.startswith('OC'):
            new_name = record.name.replace('OC', 'PC')

        if new_name and new_name != record.name:
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
        res = super(PurchaseOrder, self).action_set_done()
        for order in self:
            old_prefix = self._get_current_prefix(order)
            self._update_sequence_prefix(order)
            new_prefix = self._get_current_prefix(order)
            if old_prefix != new_prefix:
                self._log_prefix_change(order, old_prefix, new_prefix)
        return res

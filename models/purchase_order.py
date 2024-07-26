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
                self._log_authorization_change(record, vals['is_authorized'])
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
        if not record.name:
            if not record.is_authorized:
                new_name = self.env['ir.sequence'].next_by_code('purchase.order.draft') or 'RDM'
            elif record.state == 'purchase':
                new_name = self.env['ir.sequence'].next_by_code('purchase.order.confirmed') or 'OC'
            elif record.state == 'done':
                new_name = self.env['ir.sequence'].next_by_code('purchase.order.done') or 'PC'
            else:
                new_name = 'RDM'  # Default prefix for drafts

            record.with_context(skip_update_prefix=True).write({'name': new_name})

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

    def action_set_done(self):
        for order in self:
            order.state = 'done'
            old_prefix = self._get_current_prefix(order)
            self._update_sequence_prefix(order)
            new_prefix = self._get_current_prefix(order)
            if old_prefix != new_prefix:
                self._log_prefix_change(order, old_prefix, new_prefix)

# Agregar las secuencias directamente en el método de inicialización del modelo
def _create_sequences(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    if not env['ir.sequence'].search([('code', '=', 'purchase.order.draft')]):
        env['ir.sequence'].create({
            'name': 'Purchase Order Draft',
            'code': 'purchase.order.draft',
            'prefix': 'RDM',
            'padding': 4,
        })
    if not env['ir.sequence'].search([('code', '=', 'purchase.order.confirmed')]):
        env['ir.sequence'].create({
            'name': 'Purchase Order Confirmed',
            'code': 'purchase.order.confirmed',
            'prefix': 'OC',
            'padding': 4,
        })
    if not env['ir.sequence'].search([('code', '=', 'purchase.order.done')]):
        env['ir.sequence'].create({
            'name': 'Purchase Order Done',
            'code': 'purchase.order.done',
            'prefix': 'PC',
            'padding': 4,
        })

def post_init_hook(cr, registry):
    _create_sequences(cr, registry)

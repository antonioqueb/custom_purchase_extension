from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # Definir los campos KPI
    kpi_total_amount = fields.Monetary(string="Importe Total", compute="_compute_kpi_total_amount", currency_field="currency_id", store=True)
    kpi_order_count = fields.Integer(string="Número de Órdenes", compute="_compute_kpi_order_count", store=True)

    @api.depends('amount_total')
    def _compute_kpi_total_amount(self):
        for order in self:
            order.kpi_total_amount = order.amount_total

    @api.depends('partner_id')
    def _compute_kpi_order_count(self):
        for order in self:
            order.kpi_order_count = self.search_count([('partner_id', '=', order.partner_id.id)])

    is_authorized = fields.Boolean(string='Autorizado', default=False)
    planta = fields.Selection([
        ('none', 'Selecciona Planta...'),  
        ('planta_1', 'Planta 1'),
        ('planta_2', 'Planta 2'),
        ('planta_3', 'Planta 3'),
        ('planta_4', 'Planta 4'),
        ('planta_5', 'Planta 5'),
        ('planta_6', 'Planta 6'),
        ('planta_7', 'Planta 7'),
    ], string='Planta', default='none', required=False)  

    tipo = fields.Selection([
        ('none', 'Selecciona Tipo...'),
        ('tipo_1', 'Mantenimiento'),
        ('tipo_2', 'Materia prima'),
        ('tipo_3', 'Consumibles'),
    ], string='Tipo', default='none', required=False)

    # Nuevo campo calculado para mostrar el estado personalizado
    custom_state_display = fields.Char(string='Estado Compra', compute='_compute_custom_state_display')
    custom_delivery_address = fields.Char(string='Dirección de Entrega')
    custom_area = fields.Selection([
        ('none', 'Selecciona un área...'),  
        ('dg', 'Dirección'),
        ('rh', 'Recursos Humanos'),
        ('seguridad', 'Seguridad'),
        ('almacen_general', 'Almacén General'),
        ('mantenimiento_oper', 'Mantenimiento Operativo'),
        ('mantenimiento_gral', 'Mantenimiento General'),
        ('sac', 'Servicio de Atención al Cliente'),
    ], string='Área', default='none', required=False)

        # **Nuevo campo: Método de Pago**
    metodo_pago = fields.Selection([
        ('transferencia', 'Transferencia'),
        ('efectivo', 'Efectivo'),
        ('tarjeta_rh', 'Tarjeta RH'),
        ('tarjeta_a', 'Tarjeta A'),
    ], string='Método de Pago', required=False)

    @api.model
    def create(self, vals):
        if 'planta' not in vals:
            vals['planta'] = 'planta_1'
        if 'tipo' not in vals:
            vals['tipo'] = 'tipo_2'

        record = super(PurchaseOrder, self).create(vals)
        self._update_sequence_prefix(record)
        self._log_planta_change(record, vals['planta'])
        self._log_tipo_change(record, vals['tipo'])

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
            if 'tipo' in vals:
                self._log_tipo_change(record, vals['tipo'])
            if 'custom_area' in vals:
                self._log_custom_area_change(record, vals['custom_area'])

            new_prefix = self._get_current_prefix(record)
            if old_prefixes[record.id] != new_prefix:
                self._log_prefix_change(record, old_prefixes[record.id], new_prefix)
            self._update_sequence_prefix(record)

        return res

    def _log_authorization_change(self, record, new_value):
        if self.env.user.id == 1:  # Verificar si el usuario es OdooBot
            return
        user = self.env.user
        timestamp = fields.Datetime.now()
        message = "El estado de autorización cambió a: {} por {} el {}".format(
            'Autorizado' if new_value else 'No Autorizado',
            user.name,
            timestamp
        )
        record.message_post(body=message)

    def _log_planta_change(self, record, new_value):
        if self.env.user.id == 1:  # Verificar si el usuario es OdooBot
            return
        user = self.env.user
        timestamp = fields.Datetime.now()
        message = "La planta se cambió a: {} por {} el {}".format(
            dict(record._fields['planta'].selection).get(new_value),
            user.name,
            timestamp
        )
        record.message_post(body=message)

    def _log_tipo_change(self, record, new_value):
        if self.env.user.id == 1:  # Verificar si el usuario es OdooBot
            return
        user = self.env.user
        timestamp = fields.Datetime.now()
        message = "El tipo de orden se cambió a: {} por {} el {}".format(
            dict(record._fields['tipo'].selection).get(new_value),
            user.name,
            timestamp
        )
        record.message_post(body=message)

    def _log_custom_area_change(self, record, new_value):
        if self.env.user.id == 1:  # Verificar si el usuario es OdooBot
            return
        user = self.env.user
        timestamp = fields.Datetime.now()
        message = "El área se cambió a: {} por {} el {}".format(
            dict(record._fields['custom_area'].selection).get(new_value),
            user.name,
            timestamp
        )
        record.message_post(body=message)

    def _update_sequence_prefix(self, record):
        new_name = None

        if not record.is_authorized and record.state != 'purchase':
            if not record.name.startswith('RDM'):
                new_name = self.env['ir.sequence'].next_by_code('purchase.order.draft')

        elif (record.is_authorized or record.state == 'purchase') and record.name.startswith('RDM'):
            new_name = record.name.replace('RDM', 'OC')

        if record.is_authorized and record.state == 'purchase' and not record.name.startswith('PC'):
            if record.name.startswith('RDM'):
                new_name = record.name.replace('RDM', 'PC')
            elif record.name.startswith('OC'):
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
        if self.env.user.id == 1:  # Verificar si el usuario es OdooBot
            return
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

    @api.depends('name')
    def _compute_custom_state_display(self):
        for record in self:
            if record.name.startswith('RDM'):
                record.custom_state_display = "Requisición de Mercancías"
            elif record.name.startswith('OC'):
                record.custom_state_display = "Orden de Compra"
            elif record.name.startswith('PC'):
                record.custom_state_display = "Pedido de Compra"
            else:
                record.custom_state_display = "Borrador"

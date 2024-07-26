from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_authorized = fields.Boolean(string='Autorizado', default=False)

    @api.multi
    def write(self, vals):
        _logger.info("Escribiendo en Purchase Order con vals: %s", vals)
        if 'is_authorized' in vals:
            for record in self:
                old_value = record.is_authorized
                new_value = vals['is_authorized']
                _logger.info("Valor antiguo: %s, Valor nuevo: %s", old_value, new_value)
                if old_value != new_value:
                    message = "El estado de autorización ha cambiado de %s a %s" % (
                        'Autorizado' if old_value else 'No Autorizado', 
                        'Autorizado' if new_value else 'No Autorizado'
                    )
                    _logger.info("Publicando mensaje: %s", message)
                    record.message_post(body=message)
        return super(PurchaseOrder, self).write(vals)

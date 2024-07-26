from . import models
from .models.purchase_order import post_init_hook

def pre_init_hook(cr):
    pass

def uninstall_hook(cr, registry):
    pass

def post_init_hook(cr, registry):
    _create_sequences(cr, registry)

from odoo import api, SUPERUSER_ID

def _create_sequences(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    if not env['ir.sequence'].search([('code', '=', 'purchase.order.draft')]):
        env['ir.sequence'].create({
            'name': 'Purchase Order Draft',
            'code': 'purchase.order.draft',
            'prefix': 'RDM',
            'padding': 4,
            'implementation': 'no_gap',
        })
    if not env['ir.sequence'].search([('code', '=', 'purchase.order.confirmed')]):
        env['ir.sequence'].create({
            'name': 'Purchase Order Confirmed',
            'code': 'purchase.order.confirmed',
            'prefix': 'OC',
            'padding': 4,
            'implementation': 'no_gap',
        })
    if not env['ir.sequence'].search([('code', '=', 'purchase.order.done')]):
        env['ir.sequence'].create({
            'name': 'Purchase Order Done',
            'code': 'purchase.order.done',
            'prefix': 'PC',
            'padding': 4,
            'implementation': 'no_gap',
        })

def post_init_hook(cr, registry):
    _create_sequences(cr, registry)

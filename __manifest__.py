{
    'name': 'Custom Purchase Extension',
    'version': '1.4',
    'summary': 'Extension to add is_authorized field to Purchase Order',
    'description': 'This module adds a custom field to indicate if the purchase order is authorized.',
    'author': 'ALPHAQUEB CONSULTING S.A.S.',
    'depends': ['purchase'],
    'data': [
    'views/purchase_order_view_inherit.xml',
    ],
    'installable': True,
    'application': False,
}

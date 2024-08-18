# Custom Purchase Extension

Este módulo extiende la funcionalidad del modelo `purchase.order` en Odoo, añadiendo campos adicionales a las vistas de formulario y lista.

## Instalación

1. Descarga o clona este repositorio en tu carpeta de módulos de Odoo.
2. Reinicia el servicio de Odoo para que detecte el nuevo módulo.
3. Activa el modo desarrollador en tu base de datos de Odoo.
4. Ve al menú de aplicaciones, actualiza la lista de módulos, y luego instala el módulo `custom_purchase_extension`.

## Vista de Formulario

```xml
<form string="Orden de Compra" class="o_purchase_order">
    <header>
        <button name="action_rfq_send" invisible="state != 'draft'" string="Enviar por Correo" type="object" context="{'send_rfq':True}" class="oe_highlight" data-hotkey="g"/>
        <button name="print_quotation" string="Imprimir RFQ" type="object" invisible="state != 'draft'" class="oe_highlight" groups="base.group_user" data-hotkey="k"/>
        <button name="button_confirm" type="object" invisible="state != 'sent'" string="Confirmar Orden" context="{'validate_analytic': True}" class="oe_highlight" id="bid_confirm" data-hotkey="q"/>
        <button name="button_approve" type="object" invisible="state != 'to approve'" string="Aprobar Orden" class="oe_highlight" groups="purchase.group_purchase_manager" data-hotkey="z"/>
        <button name="action_create_invoice" string="Crear Factura" type="object" class="oe_highlight" context="{'create_bill':True}" invisible="state not in ('purchase', 'done') or invoice_status in ('no', 'invoiced')" data-hotkey="w"/>
        <button name="action_rfq_send" invisible="state != 'sent'" string="Reenviar por Correo" type="object" context="{'send_rfq':True}" data-hotkey="g"/>
        <button name="print_quotation" string="Imprimir RFQ" type="object" invisible="state != 'sent'" groups="base.group_user" data-hotkey="k"/>
        <button name="button_confirm" type="object" invisible="state != 'draft'" context="{'validate_analytic': True}" string="Confirmar Orden" id="draft_confirm" data-hotkey="q"/>
        <button name="action_rfq_send" invisible="state != 'purchase'" string="Enviar PO por Correo" type="object" context="{'send_rfq':False}" data-hotkey="g"/>
        <button name="confirm_reminder_mail" string="Confirmar Fecha de Recepción" type="object" invisible="state not in ('purchase', 'done') or mail_reminder_confirmed or not date_planned" groups="base.group_no_one" data-hotkey="o"/>
        <button name="action_create_invoice" string="Crear Factura" type="object" context="{'create_bill':True}" invisible="state not in ('purchase', 'done') or invoice_status not in ('no', 'invoiced') or not order_line" data-hotkey="w"/>
        <button name="button_draft" invisible="state != 'cancel'" string="Establecer a Borrador" type="object" data-hotkey="o"/>
        <button name="button_cancel" invisible="state not in ('draft', 'to approve', 'sent', 'purchase')" string="Cancelar" type="object" data-hotkey="x"/>
        <button name="button_done" type="object" string="Bloquear" invisible="state != 'purchase'" data-hotkey="l"/>
        <button name="button_unlock" type="object" string="Desbloquear" invisible="state != 'done'" groups="purchase.group_purchase_manager" data-hotkey="l"/>
        <field name="state" widget="statusbar" statusbar_visible="draft,sent,purchase" readonly="1"/>
    </header>
    <sheet>
        <div class="oe_button_box" name="button_box">
            <button type="object" name="action_view_invoice" class="oe_stat_button" icon="fa-pencil-square-o" invisible="invoice_count == 0 or state in ('draft', 'sent', 'to approve')">
                <field name="invoice_count" widget="statinfo" string="Facturas de Proveedor"/>
                <field name="invoice_ids" invisible="1"/>
            </button>
        </div>
        <div class="oe_title">
            <span class="o_form_label" invisible="state not in ('draft', 'sent')">Solicitud de Cotización </span>
            <span class="o_form_label" invisible="state in ('draft', 'sent')">Orden de Compra </span>
            <h1 class="d-flex">
                <field name="priority" widget="priority" class="me-3"/>
                <field name="name" readonly="1"/>
            </h1>
        </div>
        <group>
            <group>
                <field name="partner_id" widget="res_partner_many2one" context="{'res_partner_search_mode': 'supplier', 'show_vat': True}" placeholder="Nombre, RFC, Correo, o Referencia" readonly="state in ['cancel', 'done', 'purchase']"/>
                <field name="partner_ref"/>
                <field name="currency_id" groups="base.group_multi_currency" force_save="1" readonly="state in ['cancel', 'done', 'purchase']"/>
                <field name="id" invisible="1"/>
                <field name="company_id" invisible="1" readonly="state in ['cancel', 'done', 'purchase']"/>
                <field name="currency_id" invisible="1" readonly="state in ['cancel', 'done', 'purchase']" groups="!base.group_multi_currency"/>
                <field name="tax_calculation_rounding_method" invisible="1"/>
            </group>
            <group>
                <field name="date_order" invisible="state in ('purchase', 'done')" readonly="state in ['cancel', 'done', 'purchase']"/>
                <label for="date_approve" invisible="state not in ('purchase', 'done')"/>
                <div name="date_approve" invisible="state not in ('purchase', 'done')" class="o_row">
                    <field name="date_approve"/>
                    <field name="mail_reception_confirmed" invisible="1"/>
                    <span class="text-muted" invisible="not mail_reception_confirmed">(confirmado por el proveedor)</span>
                </div>
                <label for="date_planned"/>
                <div name="date_planned_div" class="o_row">
                    <field name="date_planned" readonly="state not in ('draft', 'sent', 'to approve', 'purchase')"/>
                    <field name="mail_reminder_confirmed" invisible="1"/>
                    <span class="text-muted" invisible="not mail_reminder_confirmed">(confirmado por el proveedor)</span>
                </div>
                <label for="receipt_reminder_email" class="d-none" groups="purchase.group_send_reminder"/>
                <div name="reminder" class="o_row" groups="purchase.group_send_reminder" title="Enviar automáticamente un correo de confirmación al proveedor X días antes de la fecha prevista de recepción, pidiéndole que confirme la fecha exacta.">
                    <field name="receipt_reminder_email"/>
                    <span>Pedir confirmación</span>
                    <div class="o_row oe_inline" invisible="not receipt_reminder_email">
                        <field name="reminder_date_before_receipt"/>
                        día(s) antes
                        <widget name="toaster_button" button_name="send_reminder_preview" title="Previsualizar el correo recordatorio enviándolo a ti mismo." invisible="not id"/>
                    </div>
                </div>
                <field name="is_authorized" widget="boolean_toggle" class="oe_inline"/>
                <field name="planta"/>
            </group>
        </group>
        <notebook>
            <page string="Productos" name="products">
                <field name="tax_country_id" invisible="1"/>
                <field name="order_line" widget="section_and_note_one2many" mode="tree,kanban" context="{'default_state': 'draft'}" readonly="state in ('done', 'cancel')">
                    <tree string="Líneas de Orden de Compra" editable="bottom">
                        <control>
                            <create name="add_product_control" string="Agregar un producto"/>
                            <create name="add_section_control" string="Agregar una sección" context="{'default_display_type': 'line_section'}"/>
                            <create name="add_note_control" string="Agregar una nota" context="{'default_display_type': 'line_note'}"/>
                            <button name="action_add_from_catalog" string="Catálogo" type="object" class="px-4 btn-link" context="{'order_id': parent.id}"/>
                        </control>
                        <field name="tax_calculation_rounding_method" column_invisible="True"/>
                        <field name="display_type" column_invisible="True"/>
                        <field name="company_id" column_invisible="True"/>
                        <field name="currency_id" column_invisible="True"/>
                        <field name="state" column_invisible="True"/>
                        <field name="product_type" column_invisible="True"/>
                        <field name="product_uom" column_invisible="True" groups="!uom.group_uom"/>
                        <field name="product_uom_category_id" column_invisible="True"/>
                        <field name="invoice_lines" column_invisible="True"/>
                        <field name="sequence" widget="handle"/>
                        <field name="product_id" readonly="state in ('purchase', 'to approve', 'done', 'cancel')" required="not display_type" width="35%" context="{'partner_id':parent.partner_id, 'quantity':product_qty, 'company_id': parent.company_id}" force_save="1" domain="[('purchase_ok', '=', True)]"/>
                        <field name="name" widget="section_and_note_text"/>
                        <field name="date_planned" optional="hide" required="not display_type" force_save="1"/>
                        <field name="analytic_distribution" widget="analytic_distribution" optional="hide" groups="analytic.group_analytic_accounting" options="{'product_field': 'product_id', 'business_domain': 'purchase_order', 'amount_field': 'price_subtotal'}"/>
                        <field name="product_qty"/>
                        <field name="qty_received_manual" column_invisible="True"/>
                        <field name="qty_received_method" column_invisible="True"/>
                        <field name="qty_received" string="Recibido" column_invisible="parent.state not in ('purchase', 'done')" readonly="qty_received_method != 'manual'" optional="show"/>
                        <field name="qty_invoiced" string="Facturado" column_invisible="parent.state not in ('purchase', 'done')" optional="show"/>
                        <field name="product_uom" string="UoM" groups="uom.group_uom" readonly="state in ('purchase', 'done', 'cancel')" required="not display_type" options="{'no_open': True}" force_save="1" optional="show"/>
                        <field name="product_packaging_qty" invisible="not product_id or not product_packaging_id" groups="product.group_stock_packaging" optional="show"/>
                        <field name="product_packaging_id" invisible="not product_id" context="{'default_product_id': product_id, 'tree_view_ref':'product.product_packaging_tree_view', 'form_view_ref':'product.product_packaging_form_view'}" groups="product.group_stock_packaging" optional="show"/>
                        <field name="price_unit" readonly="qty_invoiced != 0"/>
                        <button name="action_purchase_history" type="object" icon="fa-history" title="Historial de Compras" invisible="not id"/>
                        <field name="taxes_id" widget="many2many_tags" domain="[('type_tax_use', '=', 'purchase'), ('company_id', 'parent_of', parent.company_id), ('country_id', '=', parent.tax_country_id), ('active', '=', True)]" context="{'default_type_tax_use': 'purchase', 'search_view_ref': 'account.account_tax_view_search'}" options="{'no_create': True}" optional="show"/>
                        <field name="discount" string="Desc.%" readonly="qty_invoiced != 0" optional="hide"/>
                        <field name="price_subtotal" string="Impuestos excl."/>
                        <field name="price_total" string="Impuestos incl." column_invisible="parent.tax_calculation_rounding_method == 'round_globally'" optional="hide"/>
                    </tree>
                    <form string="Línea de Orden de Compra">
                        <field name="tax_calculation_rounding_method" invisible="1"/>
                        <field name="state" invisible="1"/>
                        <field name="display_type" invisible="1"/>
                        <field name="company_id" invisible="1"/>
                        <group invisible="display_type">
                            <group>
                                <field name="product_uom_category_id" invisible="1"/>
                                <field name="product_id" context="{'partner_id': parent.partner_id}" widget="many2one_barcode" domain="[('purchase_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', parent.company_id)]" readonly="state in ('purchase', 'to approve', 'done', 'cancel')"/>
                                <label for="product_qty"/>
                                <div class="o_row">
                                    <field name="product_qty"/>
                                    <field name="product_uom" groups="uom.group_uom" required="not display_type"/>
                                </div>
                                <field name="qty_received_method" invisible="1"/>
                                <field name="qty_received" string="Cantidad Recibida" invisible="parent.state not in ('purchase', 'done')" readonly="qty_received_method != 'manual'"/>
                                <field name="qty_invoiced" string="Cantidad Facturada" invisible="parent.state not in ('purchase', 'done')"/>
                                <field name="product_packaging_qty" invisible="not product_id or not product_packaging_id" groups="product.group_stock_packaging"/>
                                <field name="product_packaging_id" invisible="not product_id" context="{'default_product_id': product_id, 'tree_view_ref':'product.product_packaging_tree_view', 'form_view_ref':'product.product_packaging_form_view'}" groups="product.group_stock_packaging"/>
                                <field name="price_unit"/>
                                <field name="discount"/>
                                <field name="taxes_id" widget="many2many_tags" domain="[('type_tax_use', '=', 'purchase'), ('company_id', 'parent_of', parent.company_id), ('country_id', '=', parent.tax_country_id)]" options="{'no_create': True}"/>
                            </group>
                            <group>
                                <field name="date_planned" widget="date" required="not display_type"/>
                                <field name="analytic_distribution" widget="analytic_distribution" groups="analytic.group_analytic_accounting" options="{'product_field': 'product_id', 'business_domain': 'purchase_order'}"/>
                            </group>
                            <group>
                                <notebook colspan="4">
                                    <page string="Notas" name="notes">
                                        <field name="name"/>
                                    </page>
                                    <page string="Facturas y Envíos" name="invoices_incoming_shiptments">
                                        <field name="invoice_lines"/>
                                    </page>
                                </notebook>
                            </group>
                        </group>
                        <label for="name" string="Nombre de la Sección (por ejemplo, Productos, Servicios)" invisible="display_type != 'line_section'"/>
                        <label for="name" string="Nota" invisible="display_type != 'line_note'"/>
                        <field name="name" nolabel="1" invisible="not display_type"/>
                    </form>
                    <kanban class="o_kanban_mobile">
                        <field name="name"/>
                        <field name="product_id"/>
                        <field name="product_qty"/>
                        <field name="product_uom" groups="uom.group_uom"/>
                        <field name="price_subtotal"/>
                        <field name="price_tax"/>
                        <field name="price_total"/>
                        <field name="price_unit"/>
                        <field name="discount"/>
                        <field name="display_type"/>
                        <field name="taxes_id"/>
                        <field name="tax_calculation_rounding_method"/>
                        <templates>
                            <t t-name="kanban-box">
                                <div t-attf-class="oe_kanban_card oe_kanban_global_click {{ record.display_type.raw_value ? 'o_is_' + record.display_type.raw_value : '' }}">
                                    <t t-if="!record.display_type.raw_value">
                                        <div class="row">
                                            <div class="col-8">
                                                <strong>
                                                    <span t-esc="record.product_id.value"/>
                                                </strong>
                                            </div>
                                            <div class="col-4">
                                                <strong>
                                                    <span>
                                                        Imp. excl.: <t t-esc="record.price_subtotal.value" class="float-end text-end"/>
                                                    </span>
                                                </strong>
                                            </div>
                                        </div>
                                        <div class="row">
                                            <div class="col-8 text-muted">
                                                <span>
                                                    Cantidad:
                                                    <t t-esc="record.product_qty.value"/>
                                                    <small> <t t-esc="record.product_uom.value" groups="uom.group_uom"/></small>
                                                </span>
                                            </div>
                                            <div class="col-4" t-if="record.tax_calculation_rounding_method.raw_value === 'round_per_line'">
                                                <strong>
                                                   <span>
                                                       Imp. incl.: <t t-esc="record.price_total.value"/>
                                                   </span>
                                                </strong>
                                            </div>
                                        </div>
                                        <div class="row">
                                            <div class="col-12 text-muted">
                                                <span>
                                                    Precio Unitario:
                                                    <t t-esc="record.price_unit.value"/>
                                                </span>
                                            </div>
                                        </div>
                                        <div class="row" t-if="record.discount.raw_value">
                                            <div class="col-12 text-muted">
                                               <span>
                                                   Descuento: <t t-out="record.discount.value"/>%
                                               </span>
                                            </div>
                                        </div>
                                    </t>
                                    <div t-elif="record.display_type.raw_value === 'line_section' || record.display_type.raw_value === 'line_note'" class="row">
                                        <div class="col-12">
                                            <span t-esc="record.name.value"/>
                                        </div>
                                    </div>
                                </div>
                            </t>
                        </templates>
                    </kanban>
                </field>
                <group>
                    <group>
                        <field colspan="2" name="notes" nolabel="1" placeholder="Defina sus términos y condiciones ..."/>
                    </group>
                    <group class="oe_subtotal_footer">
                        <field name="tax_totals" widget="account-tax-totals-field" nolabel="1" colspan="2" readonly="1"/>
                    </group>
                </group>
                <div class="clearfix"/>
            </page>
            <page string="Otra Información" name="purchase_delivery_invoice">
                <group>
                    <group name="other_info">
                        <field name="user_id" domain="[('share', '=', False)]" widget="many2one_avatar_user"/>
                        <field name="company_id" groups="base.group_multi_company" options="{'no_create': True}" readonly="state in ['cancel', 'done', 'purchase']"/>
                        <field name="origin"/>
                    </group>
                    <group name="invoice_info">
                        <field name="invoice_status" invisible="state in ('draft', 'sent', 'to approve', 'cancel')"/>
                        <field name="payment_term_id" readonly="invoice_status == 'invoiced' or state == 'done'" options="{'no_create': True}"/>
                        <field name="fiscal_position_id" options="{'no_create': True}" readonly="invoice_status == 'invoiced' or state == 'done'"/>
                    </group>
                </group>
            </page>
        </notebook>
    </sheet>
    <div class="oe_chatter">
        <field name="message_follower_ids"/>
        <field name="activity_ids"/>
        <field name="message_ids"/>
    </div>
</form>
```

## Vista de Lista

```xml
<tree string="Purchase Order" decoration-info="state in ['draft', 'sent']" decoration-muted="state == 'cancel'" class="o_purchase_order" js_class="purchase_dashboard_list" sample="1">
    <header>
        <button name="action_create_invoice" type="object" string="Create Bills"/>
    </header>
    <field name="priority" optional="show" widget="priority" nolabel="1"/>
    <field name="partner_ref" optional="hide"/>
    <field name="name" string="Reference" readonly="1" decoration-bf="1"/>
    <field name="date_approve" column_invisible="context.get('quotation_only', False)" optional="show"/>
    <field name="partner_id" readonly="1"/>
    <field name="company_id" readonly="1" options="{'no_create': True}" groups="base.group_multi_company" optional="show"/>
    <field name="company_id" groups="!base.group_multi_company" column_invisible="True" readonly="state in ['cancel', 'done', 'purchase']"/>
    <field name="date_planned" column_invisible="context.get('quotation_only', False)" optional="show"/>
    <field name="user_id" optional="show" widget="many2one_avatar_user"/>
    <field name="date_order" invisible="state == 'purchase' or state == 'done' or state == 'cancel'" column_invisible="not context.get('quotation_only', False)" readonly="state in ['cancel', 'done', 'purchase']" widget="remaining_days" optional="show"/>
    <field name="activity_ids" widget="list_activity" optional="show"/>
    <field name="origin" optional="show"/>
    <field name="amount_untaxed" sum="Total Untaxed amount" string="Untaxed" widget="monetary" optional="hide"/>
    <field name="amount_total" sum="Total amount" widget="monetary" optional="show" decoration-bf="state in ['purchase', 'done']"/>
    <field name="currency_id" column_invisible="True" readonly="state in ['cancel', 'done', 'purchase']"/>
    <field name="state" optional="show" widget="badge" decoration-success="state == 'purchase' or state == 'done'" decoration-warning="state == 'to approve'" decoration-info="state == 'draft' or state == 'sent'"/>
    <field name="invoice_status" optional="hide"/>
    <field name="planta" string="Planta" optional="show"/> <!-- Aquí se agrega el campo para la planta -->
    <field name="is_authorized" string="Autorizado" widget="boolean" optional="show"/> <!-- Aquí se agrega el campo para el estado de autorización -->
</tree>
```
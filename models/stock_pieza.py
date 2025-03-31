from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class StockPieza(models.Model):
    _name = 'stock.pieza'
    _description = 'Unidad Física de Producto'
    _order = 'codigo_unico'

    codigo_sistema = fields.Char(
        string="Código Interno", required=True, copy=False, readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('stock.pieza')
    )
    lote_id = fields.Many2one('stock.lot', string="Lote", required=True)
    codigo_consecutivo = fields.Integer(string="Consecutivo", readonly=True)
    codigo_unico = fields.Char(string="Código Único", compute='_compute_codigo_unico', store=True, readonly=True)

    product_id = fields.Many2one('product.product', string="Producto", required=True, ondelete="cascade")
    tipo_material = fields.Char(string="Tipo de Mármol/Material", required=True)
    descripcion_bundle = fields.Char(string="Descripción", required=True)

    alto = fields.Float(string="Alto (m)", required=True)
    ancho = fields.Float(string="Ancho (m)", required=True)
    area_m2 = fields.Float(string="Área (m²)", compute='_compute_area', store=True)

    ubicacion_id = fields.Many2one('stock.location', string="Ubicación", required=True)
    estado_operativo = fields.Selection([
        ('disponible', 'Disponible'),
        ('reservada', 'Reservada'),
        ('entregada', 'Entregada'),
        ('transito', 'En tránsito'),
        ('baja', 'Baja'),
    ], default='disponible', required=True)

    cliente_id = fields.Many2one('res.partner', string="Cliente")
    fecha_ingreso = fields.Datetime(default=fields.Datetime.now)
    fecha_modificacion = fields.Datetime(auto_now=True)
    fecha_entrega = fields.Datetime()

    _sql_constraints = [
        ('codigo_sistema_uniq', 'unique(codigo_sistema)', 'El código interno debe ser único.'),
        ('codigo_unico_uniq', 'unique(codigo_unico)', 'El código único ya existe.'),
    ]

    @api.depends('lote_id.name', 'codigo_consecutivo')
    def _compute_codigo_unico(self):
        for rec in self:
            if rec.lote_id and rec.codigo_consecutivo:
                rec.codigo_unico = f"{rec.lote_id.name}-{rec.codigo_consecutivo}"

    @api.depends('alto', 'ancho')
    def _compute_area(self):
        for rec in self:
            rec.area_m2 = rec.alto * rec.ancho

    @api.model
    def create(self, vals):
        # Asignar consecutivo automático por lote
        if 'lote_id' in vals:
            existing = self.search([('lote_id', '=', vals['lote_id'])])
            vals['codigo_consecutivo'] = len(existing) + 1

        pieza = super(StockPieza, self).create(vals)

        if pieza.estado_operativo == 'disponible':
            picking_type = self.env.ref('stock.picking_type_in')  # Recepción
            supplier_location = self.env.ref('stock.stock_location_suppliers')
            dest_location = pieza.ubicacion_id

            # Crear operación de recepción (picking)
            picking = self.env['stock.picking'].sudo().create({
                'picking_type_id': picking_type.id,
                'location_id': supplier_location.id,
                'location_dest_id': dest_location.id,
                'origin': f'AutoEntrada-{pieza.codigo_unico}',
            })

            # Crear movimiento dentro del picking
            move = self.env['stock.move'].sudo().create({
                'name': f"Entrada pieza {pieza.codigo_unico}",
                'picking_id': picking.id,
                'product_id': pieza.product_id.id,
                'product_uom_qty': 1,
                'product_uom': pieza.product_id.uom_id.id,
                'location_id': supplier_location.id,
                'location_dest_id': dest_location.id,
            })

            # Confirmar picking y asignar
            picking.action_confirm()
            picking.action_assign()

            # Crear línea de movimiento (con lote)
            self.env['stock.move.line'].sudo().create({
                'move_id': move.id,
                'picking_id': picking.id,
                'product_id': pieza.product_id.id,
                'product_uom_id': pieza.product_id.uom_id.id,
                'quantity': 1,
                'location_id': supplier_location.id,
                'location_dest_id': dest_location.id,
                'lot_id': pieza.lote_id.id,
            })

            # Validar la recepción
            picking.button_validate()

        return pieza


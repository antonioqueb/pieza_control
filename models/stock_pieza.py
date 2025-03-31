from odoo import models, fields, api

class StockPieza(models.Model):
    _name = 'stock.pieza'
    _description = 'Unidad Física de Producto'
    _order = 'codigo_unico'

    codigo_sistema = fields.Char(string="Código Interno", required=True, copy=False, readonly=True,
                                 default=lambda self: self.env['ir.sequence'].next_by_code('stock.pieza'))
    lote_id = fields.Many2one('stock.lot', string="Lote", required=True)
    codigo_consecutivo = fields.Integer(string="Consecutivo", required=True)
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

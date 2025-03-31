from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    pieza_ids = fields.One2many('stock.pieza', 'product_id', string="Piezas Físicas")
    total_m2_disponibles = fields.Float(string="Total m² disponibles", compute='_compute_total_m2', store=True)

    @api.depends('pieza_ids.area_m2', 'pieza_ids.estado_operativo')
    def _compute_total_m2(self):
        for rec in self:
            piezas_validas = rec.pieza_ids.filtered(lambda p: p.estado_operativo == 'disponible')
            rec.total_m2_disponibles = sum(p.area_m2 for p in piezas_validas)

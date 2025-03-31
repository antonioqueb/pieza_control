{
    "name": "Control por Pieza Física",
    "version": "1.0",
    "depends": ["stock", "product"],
    "category": "Inventory",
    "author": "Alphaqueb Consulting",
    "summary": "Trazabilidad y control de inventario por unidad física con cálculo de área",
    "data": [
        "security/pieza_security.xml",
        "security/ir.model.access.csv",
        "data/pieza_sequence.xml",
        "views/stock_pieza_views.xml",
        "views/product_product_views.xml",
    ],
    "installable": True,
    "application": False,
}

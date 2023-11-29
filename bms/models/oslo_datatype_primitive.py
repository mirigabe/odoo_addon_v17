from odoo import models, fields

class OsloDatatypePrimitive(models.Model):
    """
    """
    _name = "bms.oslo_datatype_primitive"
    _description = "awv OSLODatatypePrimitive table"

    name = fields.Char("name")
    uri = fields.Char("uri")
    definition_nl = fields.Char("definition_nl")
    label_nl = fields.Char("label_nl")	
    usagenote_nl = fields.Char("usagenote_nl")
    deprecated_version = fields.Char("deprecated_version")

    
from odoo import models, fields


class OsloDataTypeComplex(models.Model):
    _name = "bms.oslo_datatype_complex"
    _description = "awv OSLODatatypeComplex table"

    name = fields.Char("name")
    uri = fields.Char("uri")
    usagenote_nl = fields.Char("usagenote_nl")
    definition_nl = fields.Char("definition_nl")
    label_nl = fields.Char("label_nl")
    deprecated_version = fields.Char("deprecated_version")

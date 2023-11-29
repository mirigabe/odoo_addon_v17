from odoo import models, fields

class OsloEnumeration(models.Model):
    """
    """
    _name = "bms.oslo_enumeration"
    _description = "awv OSLOEnumeration table"

    name = fields.Char("name")
    uri = fields.Char("uri")
    usagenote_nl = fields.Char("usagenote_nl")
    definition_nl = fields.Char("definition_nl")
    label_nl = fields.Char("label_nl")
    codelist = fields.Char("codelist")
    deprecated_version = fields.Char("deprecated_version")


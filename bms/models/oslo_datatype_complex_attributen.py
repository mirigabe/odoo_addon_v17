from odoo import models, fields


class OsloDatatypeComplexAttributen(models.Model):
    _name = "bms.oslo_datatype_complex_attributen"
    _description = "awv OSLODatatypeComplexAttributen table"

    name = fields.Char("name")
    label_nl = fields.Char("label_nl")
    definition_nl = fields.Char("definition_nl")
    class_uri = fields.Char("class_uri")
    kardinaliteit_min = fields.Char("kardinaliteit_min")
    kardinaliteit_max = fields.Char("kardinaliteit_max")
    uri = fields.Char("uri")
    type = fields.Char("type")
    overerving = fields.Integer("overerving")
    constraints = fields.Char("constraints")
    readonly = fields.Integer("readonly")
    usagenote_nl = fields.Char("usagenote_nl")
    deprecated_version = fields.Char("deprecated_version")
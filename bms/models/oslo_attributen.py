from odoo import models, fields

class OsloAttributen(models.Model):
    """
    Type of an object
    """

    _name = "bms.oslo_attributen"
    _description = "awv OSLOAttributen table"

    name = fields.Char("name")
    label_nl = fields.Char("label_nl")
    definition_nl = fields.Char("definition_nl")
    kardinaliteit_min = fields.Char("kardinaliteit_min")
    kardinaliteit_max = fields.Char("kardinaliteit_max")
    class_uri = fields.Char("class_uri")
    uri = fields.Char("uri")
    type = fields.Char("type")
    overerving = fields.Integer("overerving")
    constraints = fields.Char("constraints")
    readonly = fields.Integer("readonly")
    usagenote_nl = fields.Char("usagenote_nl")
    deprecated_version = fields.Char("deprecated_version")

# internal foreign key (no use of uri)
    oslo_class_id = fields.Many2one(comodel_name="bms.oslo_class")
    

    
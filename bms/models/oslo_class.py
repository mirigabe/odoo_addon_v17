from odoo import api, models, fields


class OsloClass(models.Model):
    """
    Type of an object
    """

    _name = "bms.oslo_class"
    _description = "awv OSLOClass table"

    msa_otl_type_id = fields.Integer("msa_otl_type_id")
    label_nl = fields.Char("label_nl")
    name = fields.Char("name")
    uri = fields.Char("uri")
    definition_nl = fields.Char("definition_nl")
    usagenote_nl = fields.Char("usagenote_nl")
    abstract = fields.Integer("abstract")
    deprecated_version = fields.Char("deprecated version")

    #relatonal fields (not part of the AWV OSLO model)
    oslo_attributen_id = fields.One2many(comodel_name="bms.oslo_attributen", inverse_name="oslo_class_id")

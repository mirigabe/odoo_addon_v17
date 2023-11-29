from odoo import api, models, fields


class ObjectType(models.Model):
    """
    Type of an object
    """

    _name = "bms.object_type"
    _description = "maintenance object type"

    name = fields.Char("type name")
    definition = fields.Char("definition")
    otl_type_internal_id = fields.Char("internal id")

    otl_name = fields.Char(related="otl_id.name")

    otl_id = fields.Many2one(comodel_name="bms.object_type_library")
    oslo_attributen_value_id = fields.One2many(comodel_name="bms.oslo_attributen_value", inverse_name="object_type_id")

    object_id = fields.Many2many(
        comodel_name="bms.maintainance_object",
        relation="bms_objects_to_types",
        column1="object_type_id",
        column2="object_id"
    )


    @api.model
    def get_object_type(self, ids):
        result = self.browse(ids)
        return result

    @api.model
    def get_oslo_attr_def(self, id):
        """
        Function not loosly coupled. Take the assumption that the OTL type is AWV OSLO. 
        TODO:fixme
        """

        object_type_rec = self.browse(id)
        domain=[('oslo_class_uri', '=', object_type_rec.type_internal_id)]
        attributen_recs = self.env["bms.awv_attributen_primitive_datatype"].search(domain)
        return attributen_recs
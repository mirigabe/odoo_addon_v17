from odoo import models, fields, api


class MSAObject(models.Model):
    """
    Temp table to import table object from MS Databq
    """

    _name = "bms.msa_object"
    _description = "msaccess table object"

    object_id = fields.Integer()
    name = fields.Char()
    parent_id = fields.Integer()
    oslo_class_uri = fields.Char()
    otl_type_id = fields.Integer()
    tree_level = fields.Integer()
    awv_type_not_found = fields.Boolean()
    bo_temporary_type = fields.Char()
    tree_node_order = fields.Integer()


   

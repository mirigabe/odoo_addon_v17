from odoo import models, fields, api
from odoo.exceptions import ValidationError


class OsloAttributenValue(models.Model):
    """
    As the attributes are function of the object type, creatie of mechanism of
    attribute definition <-> attibute value to store in the database with the
    right native primary field type (string, float, date, ....)
    Cardinality chain
    object 1 <-> * type 1 <-> * attributes_def 1 <-> * attributes values 1 <-> 1 object

    Only to use with OTL AWV 
    """

    _name = "bms.oslo_attributen_value"
    _description = "bms.oslo_attributen_value: store values of attribute of an object type for the AWV OTL"
   
    value_type = fields.Char(string="value type")
    value_char = fields.Char("value", default=None)
    value_boolean = fields.Boolean("value", default=False)
    value_date = fields.Date("value", default=None)
    value_datetime = fields.Datetime("value", default=None)
    value_float = fields.Float("value", default=None)
    value_non_negative_integer = fields.Integer("value", default=None)
    value_enumeration  = fields.Char(related="enumeration_value_id.selection_id", string="choice", default=None, store=True)

    # relational fields
    object_id = fields.Many2one(comodel_name="bms.maintainance_object", string="Maintainance Object", required=True, ondelete="cascade")
    object_type_id = fields.Many2one(comodel_name="bms.object_type")
    attr_def_id = fields.Many2one(comodel_name="bms.attribute_definition")
    enumeration_value_id = fields.Many2one(comodel_name="bms.oslo_enumeration_values")

    #related field
    otl_type_internal_id = fields.Char(related="object_type_id.otl_type_internal_id", string="otl_type_internal_id")    
    # otl_id = fields.Many2one(comodel_name="bms.object_type_library")
    otl_name = fields.Char(related="object_type_id.otl_name", string="OTL name" )
    
    @api.constrains('value_non_negative_integer')
    def _check_description(self):
        for rec in self:
            if rec.value_non_negative_integer < 0:
                raise ValidationError("The expected value has to be a non negative integer")
    
    

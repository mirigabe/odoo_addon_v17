from odoo import models, fields


class MaintainanceObjectTypeLibrary(models.Model):
    '''
        Maintenance object type
    '''
    _name = 'bms.object_type_library'
    _description = 'Maintenance object type library'

    name = fields.Char('name', required=True)
    description = fields.Char("Description")

    object_type_ids = fields.One2many(comodel_name="bms.object_type",
                                      inverse_name="otl_id")
    
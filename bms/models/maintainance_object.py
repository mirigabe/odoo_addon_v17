from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class MaintainanceObject(models.Model):
    """
    Maintenance object table
    """

    _name = "bms.maintainance_object"
    _description = "Maintenance object"

    name = fields.Char("name", required=True)
    lantis_unique_id = fields.Char("Lantis MS Access ID")
    lantis_internal_id = fields.Integer("Lantis internal id")
    lantis_id = fields.Char(compute="_compute_lantis_id", store=True, string="lantis ID")
    bo_temporary_type = fields.Char()

    awv_type_not_found = fields.Boolean(compute="_compute_awv_type_not_found", string="AWV type not found",store=True)

    # relational fields
    object_type_ids = fields.Many2many(
        comodel_name="bms.object_type",
        relation="bms_objects_to_types",
        column1="object_id",
        column2="object_type_id",
    )
    decomposition_ids = fields.One2many(comodel_name="bms.decomposition_relationship", inverse_name="object_id")  
    oslo_attributen_value_id = fields.One2many(comodel_name="bms.oslo_attributen_value", inverse_name="object_id")

    @api.depends("object_type_ids")
    def _compute_awv_type_not_found(self):
        for rec in self:
            domain = [("object_id", "=", rec.id),("otl_id", "=", 1)]
            record = self.env["bms.object_type"].search(domain)
            if len(record) < 1:
                rec.awv_type_not_found = True
            else:
                rec.awv_type_not_found = False
       
    @api.depends("lantis_internal_id")
    def _compute_lantis_id(self):
        for rec in self:
            rec.lantis_id = "MO-" + str(rec.lantis_internal_id)

    @api.constrains("decomposition_ids")
    def _constraints_decomposition_ids(self):
        print("constraints decompostion")
        for rec in self:
            if not rec.decomposition_ids:
                raise ValidationError("You have to assign at least one decomposition")

    @api.model
    def create(self, vals_list):
        # create the right value for lantis_unique_id
        print("create maintainace", vals_list)
        max_lantis_internal_id_rec = self.env["bms.maintainance_object"].read_group([], ["lantis_internal_id:max(lantis_internal_id)"], [])
        max_id = max_lantis_internal_id_rec[0].get("lantis_internal_id")
        
        if type(vals_list) == dict:
            # assign lantis_internal_id
            max_id +=  1
            vals_list.update(lantis_internal_id=max_id)
            return super(MaintainanceObject,self).create(vals_list)
        if type(vals_list) == list:
            for vals in vals_list:
                max_id +=  1
                vals.update(lantis_internal_id=max_id)
                print("create maintainace after update list", vals)
                return super(MaintainanceObject,self).create(vals)
                


    def get_view(self, view_id=None, view_type='form', **options):
        res = super().get_view(view_id, view_type, **options)
        # print(res)
        
        from pprint import pprint
        print("/n", view_id, view_type, options, "/n")
        pprint(res)

        return res
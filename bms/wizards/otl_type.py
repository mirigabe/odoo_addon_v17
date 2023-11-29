from odoo import models, fields, api, Command


class OtlAndType(models.TransientModel):
    _name = "bms.otl_type"
    _description = "Transient model for the assignation of an otl and a type to an existing object."

    object_ids = fields.Many2one("bms.maintainance_object", string="maintainance object")
    otl = fields.Many2one("bms.object_type_library", string="OTL")
    object_type = fields.Many2one("bms.object_type", string="object type")


    def write(self, vals):
        self._change_object_type(vals)
        return super(OtlAndType, self).write(vals)

    @api.model
    def create(self, vals):
        self._change_object_type(vals)
        return super(OtlAndType, self).create(vals)

    def _change_object_type(self, vals):
        """
        self._context["default_object_ids"] is not None.
        Must be managed by Client side!!!
        """
        maintainance_object_id = self._context["default_object_ids"]
        current_object_type_id = self._context["default_object_type"] if "default_object_type" in self._context else vals["object_type"]
        new_object_type_id = vals["object_type"]

        rec_maintainance_object = self.env["bms.maintainance_object"].browse([maintainance_object_id])

        # unlink current object type en link new object type
        unlink_command = Command.unlink(current_object_type_id)
        link_command = Command.link(new_object_type_id)
        result_1 = rec_maintainance_object.write({"object_type_ids": [unlink_command, link_command]})
        # delete existing attribute_values (if any)
        result_2 = self._delete_attr_values(maintainance_object_id, current_object_type_id)
        return result_1 & result_2

    def _delete_attr_values(self, object_id, object_type_id):
        domain = [
            ("object_id", "=", object_id),
            ("object_type_id", "=", object_type_id),
        ]
        attr_value_recs = self.env["bms.oslo_attributen_value"].search(domain)

        for attr_value_rec in attr_value_recs:
            attr_value_rec.unlink()

        return True

    

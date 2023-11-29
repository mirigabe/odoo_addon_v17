from odoo import fields, models, tools, api


class Attributes(models.Model):
    _name = "bms.attributes"
    _description = "Help to display the definitions and values of the attributes for an object type"
    _auto = False
    # _rec_name = 'name'
    # _order = 'invoice_date desc'
    
    attr_def_id = fields.Integer(readonly=True)
    attr_def_name = fields.Char(readonly=True)
    attr_def_description = fields.Char(readonly=True)
    object_type_id = fields.Integer()
    otl_id = fields.Integer()
    object_type_name = fields.Char()
    otl_type_internal_id = fields.Char()
    value_type = fields.Char()
    attr_value_id = fields.Integer()
    value_char = fields.Char(default=None)
    value_boolean = fields.Boolean(default=None)
    value_date = fields.Date(default=None)
    value_float = fields.Float(default=None)
    value_integer = fields.Integer(default=None)
    object_id = fields.Integer()

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute(
                    """
            CREATE view %s as
                SELECT %s
                FROM %s
                ORDER BY %s ASC
                ;
                """
            % (self._table, self._select(), self._from(), self._order_by())
        )
        # print(   """
        #     CREATE view %s as
        #         SELECT %s
        #         FROM %s
        #         ORDER BY %s ASC
        #         """
        #     % (self._table, self._select(), self._from(), self._order_by())
        # )

    @api.model
    def _select(self):
        return """
             row_number() OVER () as id
            , attr_def.id as attr_def_id
            , attr_def.name as attr_def_name
            , attr_def.description as attr_def_description
            , ot.id as object_type_id
            , ot.otl_id as otl_id
            , ot.name as object_type_name
            , ot.otl_type_internal_id
            , attr_def.value_type
            , attr_val.id as attr_value_id
            , value_char
            , value_boolean
            , value_date
            , value_float
            , value_integer
            , mo.id as object_id
                
            """

    @api.model
    def _from(self):
        return """
                bms_maintainance_object mo
                left join bms_objects_to_types o2t on o2t.object_id = mo.id
                left join bms_object_type ot on ot.id = o2t.object_type_id
                left join bms_attributes_to_types at on at.object_type_id = ot.id
                left join bms_attribute_definition attr_def on attr_def.id = at.attribute_id
                left join bms_attribute_value attr_val on attr_val.object_id = mo.id and attr_val.attr_def_id = attr_def.id
                """
 
    @api.model
    def _where(self):
        return """
                """
    @api.model
    def _order_by(self):
        return """
               attr_def.name 
               """
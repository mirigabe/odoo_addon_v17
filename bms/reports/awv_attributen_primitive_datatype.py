from odoo import fields, models, tools, api


class AWVPrimitiveDatypeAttributes(models.Model):
    _name = "bms.awv_attributen_primitive_datatype"
    _description = "Help to display the definitions and the attributes of primitive datatype for AWV classes"
    _auto = False

    osloclass_name = fields.Char("osloclass_name")
    osloattributen_name = fields.Char("osloattributen_name")
    osloattributen_definition = fields.Char("osloattributen_definition")
    oslodatatype_primitive_definition_nl = fields.Char("oslodataype_primitive_definition_nl")
    oslo_type = fields.Char("oslo_type")
    oslodatatype_primitive_attributen_constraints = fields.Char("oslodatatype_primitive_attributen_constraints")
    oslo_value_type = fields.Char("value type")
    value_type = fields.Char(compute="_compute_odoo_value_type")
    osloclass_uri = fields.Char("osloclass_uri")
    osloattributen_uri = fields.Char("osloattributen_uri")
    oslodatatype_primitive_uri = fields.Char("oslodatatype_primitive_uri")
    oslodatatype_primitive_attributen_uri = fields.Char("oslodatatype_primitive_attributen_uri  ")
    
    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute(
            """
            CREATE view %s as
                SELECT %s
                FROM %s
                ;
            """
            % (self._table, self._select(), self._from())
        )
        # import pprint
        # print("""
        
        #         SELECT %s
        #         FROM %s

        #         ;
        #     """
        #     % (self._select(), self._from()))

    @api.model
    def _select(self):
        return """
            row_number() OVER () as id
			, c.name as osloclass_name
			, a.name as osloattributen_name
			, a.definition_nl as osloattributen_definition
            , case when dpa.type is null then dp.uri else dpa.type end as oslo_value_type
			, dp.definition_nl as oslodatatype_primitive_definition_nl
			, case when dpa.type is null then dp.uri else dpa.type end as oslo_type
			, dpa2.constraints as oslodatatype_primitive_attributen_constraints
			, c.uri as osloclass_uri
			, a.uri as osloattributen_uri
            , dp.uri as oslodatatype_primitive_uri
            , dpa.uri as oslodatatype_primitive_attributen_uri            
        """
    
    @api.model
    def _from(self):
        return """ 
           bms_oslo_class c
            inner join bms_oslo_attributen a on a.class_uri = c.uri
            inner join bms_oslo_datatype_primitive dp on dp.uri = a.type
            left join bms_oslo_datatype_primitive_attributen dpa on dpa.class_uri = dp.uri and dpa.name = 'waarde'
			left join bms_oslo_datatype_primitive_attributen dpa2 on dpa2.class_uri = dp.uri and dpa2.name = 'standaardEenheid'
        """


    @api.depends("oslo_value_type")
    def _compute_odoo_value_type(self):
        for rec in self:
            match rec.oslo_value_type:
                case "http://www.w3.org/2001/XMLSchema#anyURI":
                    rec.value_type = "char"
                case "http://www.w3.org/2001/XMLSchema#boolean":
                    rec.value_type = "boolean"
                case "http://www.w3.org/2001/XMLSchema#date":
                    rec.value_type = "date"
                case "http://www.w3.org/2001/XMLSchema#dateTime":
                    rec.value_type = "datetime"
                case "http://www.w3.org/2001/XMLSchema#decimal":
                    rec.value_type = "float"
                case "http://www.w3.org/2001/XMLSchema#nonNegativeInteger":
                    rec.value_type = "integer"
                case "http://www.w3.org/2001/XMLSchema#string":
                    rec.value_type = "char"
                case _:
                    rec.value_type = ""   # TODO raise error
        

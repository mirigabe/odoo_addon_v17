from typing import Any
from odoo import models, fields, api


class AttributeDefinition(models.Model):
    _name = "bms.attribute_definition"
    _description = """ Centralize all the attributes types with a child-parent patter
         """

    uri = fields.Char("uri")
    name = fields.Char("name")
    label_nl = fields.Char("label_nl")
    definition_nl = fields.Char("definition_nl")
    type = fields.Char("type")
    value_type = fields.Char("attribute value type")
    oslo_datatype = fields.Char("oslo data type")
    constraints = fields.Char("constraints")
    parent_id = fields.Many2one(comodel_name="bms.attribute_definition",
                                string="parent_id")
    parent_uri = fields.Char("parent_uri")

    @api.model
    def populate_table_with_awv_otl(self, oslo_class_id):
        """use to populte the table with the awv tables :
        oslo_class, oslo_attributen, oslo_datatype_primitive, oslo_datatype_primitive_attributen,
        oslo_enumeration, oslo_datatype_complex, oslo_datatype_complex_attributen
        If other OTL than awv are considered, this method has to be adapted.
        """
        awv_attributen = AWVAttributen(self, oslo_class_id)
        awv_attributen.populate()

    @api.model
    def get_att_def(self, class_id):
        data = JSONAttrDef(self, class_id).get_data()
        return data

# utility classes

import logging
logger = logging.getLogger(__name__)


def get_datatype(model, attribute_uri):
    """note: model is the self of self.env[my_table]"""
    domain = [("item_uri", "=", attribute_uri)]
    attribute_datatype = model.env["bms.oslo_type_link_tabel"].search(domain).item_tabel
    return attribute_datatype

def _get_attr_value_type(attr_type):
     match attr_type:
        case "http://www.w3.org/2001/XMLSchema#anyURI":
            return "char"
        case "http://www.w3.org/2001/XMLSchema#boolean":
            return "boolean"
        case "http://www.w3.org/2001/XMLSchema#date":
            return "date"
        case "http://www.w3.org/2001/XMLSchema#dateTime":
            return "datetime"
        case "http://www.w3.org/2001/XMLSchema#decimal":
            return "float"
        case "http://www.w3.org/2001/XMLSchema#nonNegativeInteger":
            return "non_negative_integer"
        case "http://www.w3.org/2001/XMLSchema#string":
            return "char"
        case default:
            # print(attr_type)
            return None
            

class AttributeDefinitionRecord:
    def __init__(
        self, model, record, parent_id=None, parent_uri=None, oslo_datatype=None, value_type=None
    ):
        """kwargs is an odoo record"""
        self.model = model
        self.attr_def = {
            "uri": record.uri,
            "name": record.name,
            "label_nl": record.label_nl,
            "definition_nl": record.definition_nl,
            "type": record.type if hasattr(record, "type") else None,
            "value_type": value_type, 
            "oslo_datatype": oslo_datatype,
            "constraints": record.constraints if hasattr(record, "constraints") else None,
            "parent_id": parent_id,
            "parent_uri": parent_uri,
        }

    def create(self):
        created_rec = self.model.env["bms.attribute_definition"].create(
            [self.attr_def]
        )
        return (created_rec.id, created_rec.uri)


class AwvDatatypePrimitive(AttributeDefinitionRecord):
    def __init__(self, model, datatype_primitive_rec, parent_id, parent_uri, oslo_datatype):
        # breakpoint()
        super().__init__(model,
                         datatype_primitive_rec, parent_id, parent_uri,
                         oslo_datatype, 
                         _get_attr_value_type(datatype_primitive_rec['uri']))

    def populate(self):
        # create datatype_primitive record in attribute defintion table
        parent_id, parent_uri = self.create()
        
        # create datatype_primitive_attributen records in attribute definiton table
        domain = [("class_uri", "=", self.attr_def['uri'])]
        datatype_primitive_attr_recs = self.model.env["bms.oslo_datatype_primitive_attributen"].search(domain)
        for datatype_primitive_attr_rec in datatype_primitive_attr_recs:
            # breakpoint()
            AttributeDefinitionRecord(
                self.model,
                datatype_primitive_attr_rec, parent_id, parent_uri,
                "OSLODatatypePrimitiveAttributen",
                _get_attr_value_type(datatype_primitive_attr_rec['type'])
            ).create()


class AwvEnumeration(AttributeDefinitionRecord):
    def __init__(self, model, enumeration_record, parent_id, parent_uri, oslo_datatype):
        super().__init__(
            model, enumeration_record, parent_id, parent_uri, oslo_datatype, value_type="enumeration")

    def populate(self):
        # create enumeration record in attribute definition table
        _, _ = self.create()
        # the choices of the choise lists (keuzelijst) are not added to the attribute definition table
        pass


class AwvDatatypeIterative(AttributeDefinitionRecord):
    """ Cover the oslo datatype Complex and the oslo datatype Union"""
    def __init__(self, model, datatype_complex_record, parent_id, parent_uri, oslo_datatype):
        super().__init__(model, datatype_complex_record, parent_id, parent_uri, oslo_datatype)
        match oslo_datatype:
            case "OSLODatatypeComplex": 
                self.table = "bms.oslo_datatype_complex_attributen"
                self.attribute_datatype = "OSLODatatypeComplexAttributen"
            case "OSLODatatypeUnion": 
                self.table = "bms.oslo_datatype_union_attributen"
                self.attribute_datatype = "OSLODatatypeUnionAttributen"
            case default: 
                raise Exception(msg="oslo dataype unknown")

    def populate(self):
        # create datatype complex record
        iterative_parent_id, iterative_parent_uri = self.create()

        # datatypecomplex attributen
        domain = [("class_uri", "=", self.attr_def["uri"])]
        oslo_datatype_iterative_attributen_recs = self.model.env[self.table].search(domain, [])

        for oslo_datatype_iterative_attributen_rec in oslo_datatype_iterative_attributen_recs:
            
            attribute_datatype = get_datatype(self.model, oslo_datatype_iterative_attributen_rec.type)
            parent_id, parent_uri = AttributeDefinitionRecord(self.model, oslo_datatype_iterative_attributen_rec, iterative_parent_id, iterative_parent_uri, self.attribute_datatype).create()
            AWVAttributen.getDatatypePopulator(self.model,attribute_datatype, oslo_datatype_iterative_attributen_rec, parent_id, parent_uri).populate()
            

class AWVAttributen:
    def __init__(self, model, oslo_class_id):
        self.model = model  # odoo model self of self.env["my_model"]
        self.oslo_class_id = oslo_class_id  # item of table bms.oslo_class

    def populate(self):
        """
        Take all the attributes link to a class id, and populate with a factory of populators based on the type of each attribute
        """
        # create OSLOClass item
        oslo_class_rec = self.model.env["bms.oslo_class"].browse(self.oslo_class_id)
        parent_id, parent_uri = AttributeDefinitionRecord(self.model, oslo_class_rec, oslo_datatype="OSLOclass").create()
        
        domain = [("class_uri", "=", oslo_class_rec.uri)]
        oslo_attributen_recs = self.model.env["bms.oslo_attributen"].search(domain, [])

        for oslo_attributen_rec in oslo_attributen_recs:
            # create OSLOAttributen item
            attr_id, attr_uri = AttributeDefinitionRecord(self.model, oslo_attributen_rec, parent_id, parent_uri, "OSLOAttributen").create()
            attribute_datatype = get_datatype(self.model, oslo_attributen_rec.type)
            # create datatype and datatype attributen
            self.getDatatypePopulator(self.model, attribute_datatype, oslo_attributen_rec, attr_id, attr_uri).populate()

    @classmethod
    def getDatatypePopulator(cls, model, attribute_datatype, attributen_record, parent_id, parent_uri):
        """Factory based on attribute_datatype"""
        match attribute_datatype:
            case "OSLODatatypePrimitive":
                domain = [("uri", "=", attributen_record.type)]
                datatype_primitive_rec = model.env["bms.oslo_datatype_primitive"].search(domain)
                return AwvDatatypePrimitive(model, datatype_primitive_rec, parent_id, parent_uri, attribute_datatype)

            case "OSLOEnumeration":
                domain = [("uri", "=", attributen_record.type)]
                datatype_enumeration_rec = model.env["bms.oslo_enumeration"].search(domain)
                return AwvEnumeration(model, datatype_enumeration_rec, parent_id, parent_uri, attribute_datatype)

            case "OSLODatatypeComplex":
                domain = [("uri", "=", attributen_record.type)]
                datatype_complex_rec = model.env["bms.oslo_datatype_complex"].search(domain)
                return AwvDatatypeIterative(model, datatype_complex_rec, parent_id, parent_uri, attribute_datatype)

            case "OSLODatatypeUnion":
                domain = [("uri", "=", attributen_record.type)]
                datatype_union_rec = model.env["bms.oslo_datatype_union"].search(domain)
                return AwvDatatypeIterative(model, datatype_union_rec, parent_id, parent_uri, attribute_datatype)

            case default:
                msg = """Oslo attribute_type '{0}' unknown. Check TypeLinkTabel in OSLO sqlite database. Tip: 'select distinct item_tabel
                         from TypeLinkTabel' """.format(str(attribute_datatype))
                raise Exception(msg)


class JSONAttrDef:
    def __init__(self, model, oslo_class_uri):
        """class_id is an oslo identifier of an object type"""
        self.model = model
        self.oslo_class_uri = oslo_class_uri  # TODO [0] only for testing
        self.attr_def = self._generate_json()

    def get_data(self):
        import json
        return json.dumps(self.attr_def)

    def _generate_json(self):
        attr_defs = {"oslo_class_uri": self.oslo_class_uri,
                     "attributes": []} #OSLOClass
        attribute_recs = self._get_attributes()
        if len(attribute_recs) == 0:
            return attr_defs
        for attribute_rec in attribute_recs:
            attr_def = { #OSLOAttributen
                "attr_name": attribute_rec.label_nl,
                "attr_definition_nl": attribute_rec.definition_nl,
                "attr_datatype": attribute_rec.oslo_datatype,
                "attr_datatype_def":[]
            }
            datatype_rec = self._get_children(attribute_rec.id)
            
            # for datatype_rec in datatype_recs:
            match datatype_rec.oslo_datatype:#OSLODatatype
                case "OSLODatatypePrimitive":
                    attr_def["attr_datatype_def"] = self._format_datatype_primitive(datatype_rec)

                case "OSLOEnumeration":
                    attr_def["attr_datatype_def"] = self._format_datatype_enumeration(datatype_rec)

                case "OSLODatatypeComplex":
                    attr_def["attr_datatype_def"] = self._format_datatype_iterative(datatype_rec)

                case "OSLODatatypeUnion":
                    attr_def["attr_datatype_def"] = self._format_datatype_iterative(datatype_rec) 

                case default:
                    msg = """Oslo attribute_type '{0}' unknown. ('{1}')  Check TypeLinkTabel in OSLO sqlite database. Tip: 'select distinct item_tabel
                        from TypeLinkTabel' """.format(
                        str(attribute_rec.oslo_datatype, attribute_rec.uri)
                    )
                    raise Exception(msg)

            attr_defs["attributes"].append(attr_def)

        return attr_defs


    def _format_datatype_primitive(self, datatype_rec):
        # datatype primitive
        datatype_def = {
            "attr_name": datatype_rec.label_nl,
            "attr_definition_nl": datatype_rec.definition_nl,
            "attr_datatype": datatype_rec.oslo_datatype,
        }
        datatype_att_recs = self._get_children(datatype_rec.id)
        if (len(datatype_att_recs) < 1):  # datatype of kind http://www.w3.org/2001/XMLSchema#xxx
            datatype_def = {
                **datatype_def,
                "attr_def_id": datatype_rec.id,
                "attr_value_type": _get_attr_value_type(datatype_rec.uri),
                "unit": None
            }
        else:
            for datatype_att_rec in datatype_att_recs: # datatype primitive attributen
                if datatype_att_rec.name == "waarde":
                    datatype_def = {
                        **datatype_def,
                        "attr_def_id": datatype_att_rec.id,
                        "attr_value_type": _get_attr_value_type(datatype_att_rec.type),
                    }
                if datatype_att_rec.name == "standaardEenheid":
                    datatype_def = {
                        **datatype_def,
                        "unit": datatype_att_rec.constraints,
                    }
        return datatype_def

    def _format_datatype_enumeration(self, datatype_rec):
        datatype_def = {
            "attr_name": datatype_rec.label_nl,
            "attr_definition_nl": datatype_rec.definition_nl,
            "attr_datatype": datatype_rec.oslo_datatype,
            "attr_def_id": datatype_rec.id,
            "selection_values": [],
            "attr_value_type": "enumeration"
        }
        enumeration_value_recs = self._get_enumeration_values(datatype_rec.uri)
        if len(enumeration_value_recs) == 0:
            pass  # TODO give advices to submit new proposal to AWV

        for enumeration_value_rec in enumeration_value_recs:
            selection_value = {
                "status": enumeration_value_rec.status,
                "definition": enumeration_value_rec.definition,
                "notation": enumeration_value_rec.notation,
                "selection_id": enumeration_value_rec.selection_id,
            }
            
            datatype_def["selection_values"].append(selection_value)
        return datatype_def

    def _format_datatype_iterative(self, datatype_rec):
        """datatype_rec: a datatype Complex or datatypeUnion (ex: DtcIdentificator of attribute Asset Id)
        
            for each ComplexAttributes (datatype_attr_rec) (ex Identificator, toegekendDoor)
                for each datatype of any king (datatype_child_rec) (ex Datatype Primitive, DatatypePrimitive)  
                    append attributes to complex attribute
                    create ComplexAttribute dict (datatype_child_def) and append iterative_attributes {Identificator, attributes=[DatatypePrimitive]}
                Create Complex dict and append iteratives attributes {DtcIdentificator, iterative_attributes: [{Identificator,...}, {ToegekendDoor,...}]
        """

        iterative_attributes = []
        datatype_attr_recs = self._get_children(datatype_rec.id)  #datatypeComplexAttributen or DatatypeUnionAttributen

        for datatype_attr_rec in datatype_attr_recs:     
            attributes = {}
            datatype_child_recs = self._get_children(datatype_attr_rec.id) # datatype composing datatyepComplexAttributen or DatatpeUnionAttributen
            for datatype_child_rec in datatype_child_recs: 
                match datatype_child_rec.oslo_datatype :
                    case "OSLODatatypePrimitive": 
                        # attributes.append(self._format_datatype_primitive(datatype_child_rec))
                        attributes = self._format_datatype_primitive(datatype_child_rec)

                    case "OSLOEnumeration":
                        # attributes.append(self._format_datatype_enumeration(datatype_child_rec))
                        attributes = self._format_datatype_enumeration(datatype_child_rec)

                    case "OSLODatatypeComplex":
                        # attributes.append(self._format_datatype_iterative(datatype_child_rec))
                        attributes = self._format_datatype_iterative(datatype_child_rec)

                    case "OSLODatatypeUnion":
                        # attributes.append(self._format_datatype_iterative(datatype_child_rec))
                        attributes = self._format_datatype_iterative(datatype_child_rec)

                    case default:
                        msg = """Oslo attribute_type '{0}' unknown. ('{1}')  Check TypeLinkTabel in OSLO sqlite database. Tip: 'select distinct item_tabel
                            from TypeLinkTabel' """.format(
                            datatype_attr_rec.oslo_datatype, datatype_attr_rec.uri)
                        raise Exception(msg)    
            datatype_child_def = {
                "attr_name": datatype_attr_rec.label_nl,
                "attr_definition_nl": datatype_attr_rec.definition_nl,
                "attr_datatype": datatype_attr_rec.oslo_datatype, # DatatypeComplexAttributen or DatatypeUnionAttributen
                "attr_datatype_def":attributes
            }
            iterative_attributes.append(datatype_child_def)

        datatype_def={
            "attr_name": datatype_rec.label_nl,
            "attr_definition_nl": datatype_rec.definition_nl,
            "attr_datatype": datatype_rec.oslo_datatype, #DatatypeComplex or DatatypeUnion
            "iterative_attributes": iterative_attributes
            }
        return datatype_def

    def _get_children(self, parent_id):
        domain = [("parent_id", "=", parent_id)]
        return self.model.env["bms.attribute_definition"].search(domain)

    def _get_enumeration_values(self, enumeration_uri):
        domain = [("uri", "=", enumeration_uri)]
        return self.model.env["bms.oslo_enumeration_values"].search(domain)

    def _get_attributes(self):
        """ Get OSLOAttributen of OSLOClass based on class_uri"""
        domain = [("parent_uri", "=", self.oslo_class_uri)]
        attr_def_recs = self.model.env["bms.attribute_definition"].search(domain)
        return attr_def_recs

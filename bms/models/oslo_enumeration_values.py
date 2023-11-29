from odoo import models, fields, api

class OsloEnumerationValues(models.Model):
    """
    """
    _name = "bms.oslo_enumeration_values"
    _description = "awv OSLOEnumeration values table"
    _inherits = {"bms.oslo_enumeration": "enumeration_id"}

    enumeration_id = fields.Many2one('bms.oslo_enumeration', 'enumeration_id',auto_join=True)
    selection_id = fields.Char("selection_id")
    status = fields.Char("status")
    definition = fields.Char("definition")
    notation = fields.Char("notation")

    def name_get(self): 
        """display the notation insteand of enumeration name if context item 
           'enum_display_notation is true. 
        """
        
        res = []
        if self.env.context.get('enum_display_notation', False):
            for rec in self:
                res.append((rec.id, rec.notation ))
        else:
            for rec in self:
                res.append((rec.id, rec.name))
        return res

    @api.model
    def import_value_list(self, enumeration_id):
        """
            Import thte values list on github 'https://github.com/Informatievlaanderen/OSLOthema-wegenenverkeer/tree/master/codelijsten'
            which are exposed under Turtle fiel (.tt) by iterating on the codelist of the  bms_oslo_enumeration table.
        """

        domain = [('enumeration_id', "=", enumeration_id)]
        self.env["bms.oslo_enumeration_values"].search(domain).unlink()
        
        domain = [('id', "=", enumeration_id)]
        enumeration_rec = self.env["bms.oslo_enumeration"].search(domain)
        
        awv_enum_values = AwvEnumerationValues(enumeration_rec.name)
        records = awv_enum_values.get_values_list(enumeration_rec.id)

        self.env["bms.oslo_enumeration_values"].create(records)
        return True


# utility class 
from rdflib import Graph, term, URIRef
import requests
from pprint import pprint

import logging
logger = logging.getLogger(__name__)


class AwvEnumerationValues():
    """
        Create a representation of all the possible values fron an OsloEnumeration.codelist element. 
    """
    PREDICATES = ["definition", "notation"]
    PREDICATE_PREFIX = "http://www.w3.org/2004/02/skos/core#"
    PREDICATE_IN_SCHEME = term.URIRef("http://www.w3.org/2004/02/skos/core#inScheme")
    PREDICATE_STATUS = term.URIRef("https://www.w3.org/ns/adms#status")
    PREDICATE_STATUS_NOTATION = term.URIRef(
        "http://www.w3.org/2004/02/skos/core#notation"
    )
    CODELIST_PREFIX = "https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/"

    def __init__(self, enum_name):
        self.enum_name = enum_name
        self.values_list = []
        self.git_hub_url = "https://raw.githubusercontent.com/Informatievlaanderen/OSLOthema-wegenenverkeer/master/codelijsten/{0}.ttl".format(
            enum_name
        )
        self.graph = self._instantiate_graph()
        self._parse()

    def _get_data_from_github(self):
        request = requests.get(self.git_hub_url)
        
        if request.status_code != 200:
            msg = "Enumeration file for code list '{0}' has not been loaded. Import failed.\nRequest error msg: {1}".format(
                self.enum_name, request.reason
            )
            logger.critical(msg)
            return None
        return request.text

    def _instantiate_graph(self):
        graph = Graph()

        graph.parse(data=self._get_data_from_github())
        return graph

    def _parse(self):
        for subject, _ in self.graph.subject_objects(self.PREDICATE_IN_SCHEME):
            value = {}
            value["selection_id"] = subject.toPython()
            value["status"] = self._get_object(
                subject=subject, predicate=term.URIRef(self.PREDICATE_STATUS)
            )
            for p in self.PREDICATES:
                predicate = term.URIRef(self.PREDICATE_PREFIX + p)
                value[p] = self._get_object(subject=subject, predicate=predicate)
            self.values_list.append(value)

    def _get_object(self, subject, predicate):
        objects = [
            o.toPython()
            for o in self.graph.objects(subject=subject, predicate=predicate)
        ]
        if len(objects) != 1:
            msg = "More or less than 1 item found for the (subject, predicate) : ({0}, {1}) for enumeration '{2}'.\n{3}".format(
                subject, predicate, self.enum_name, str(objects)
            )
            raise Exception(msg)
        return objects[0]

    def get_values_list(self, enumeration_id):
        """ returns values under a format ready to use with RM write method"""
        records = []
        for values in self.values_list:
            values = {"enumeration_id": enumeration_id, **values}
            records.append(values)
        return records

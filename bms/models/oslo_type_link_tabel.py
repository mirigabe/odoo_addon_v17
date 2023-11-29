from odoo import models, fields

class OsloTypeLinkTabel(models.Model):
    """
    """
    _name = "bms.oslo_type_link_tabel"
    _description = "awv OSLOTypeLinkTabel table"

    item_uri = fields.Char("item_uri")
    item_tabel = fields.Char("item_tabel")
    deprecated_version = fields.Char("deprecated_version")
    
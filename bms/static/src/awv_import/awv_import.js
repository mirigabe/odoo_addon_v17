/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState } from "@odoo/owl";

class AwvImportAction extends Component {
    setup(){
        this.orm = useService("orm");
        this.state_import_awv_enum_values = useState({processed: 0, total_to_process: 0});
        this.state_populate_att_def_table = useState({processed: 0, total_to_process: 0});
    }

    async import_awv_enumeration_values() {
        this.state_import_awv_enum_values.processed = 0;
        this.state_import_awv_enum_values.total_to_process = await this.orm.searchCount("bms.oslo_enumeration", []);
        const enumeration_ids = await this.orm.searchRead("bms.oslo_enumeration",[],["id"]);
        var rpc = require('web.rpc');
        
        Object.values(enumeration_ids).forEach((enumeration_id) => {
        const is_done = rpc.query({
            model: 'bms.oslo_enumeration_values',
            method: 'import_value_list',
            args: [enumeration_id.id],
        }).then(() => {this.state_import_awv_enum_values.processed += 1}) // }
    })
    }

    async populate_table_with_awv_otl(){
        this.state_populate_att_def_table.processed = 0;
        this.state_populate_att_def_table.total_to_process = await this.orm.searchCount("bms.oslo_class", []);

        const class_ids = await this.orm.searchRead("bms.oslo_class",[],["id"]);w
        
        var rpc = require('web.rpc');

        Object.values(class_ids).forEach((class_id) => {
            const is_done = rpc.query({
                model: 'bms.attribute_definition',
                method: 'populate_table_with_awv_otl',
                args: [class_id.id],
            }).then(() => {this.state_populate_att_def_table.processed += 1}) // }

    })
    }

}   

AwvImportAction.template = "bms.awv_import_action";
registry.category("actions").add("bms.AwvImportAction", AwvImportAction);
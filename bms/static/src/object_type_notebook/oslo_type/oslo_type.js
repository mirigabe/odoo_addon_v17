// /** @odoo-module */
import { useService} from "@web/core/utils/hooks";
const { Component, onWillStart, onWillUpdateProps } = owl;
import { OsloDatatypePrimitiveEnumeration } from "./oslo_datatype_primitive_enumeration";
import { OsloDatatypeIterative } from "./oslo_datatype_iterative";
var rpc = require('web.rpc');

export class OsloType extends Component {
    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");

        this.otlId = this.props.otlId;
        this.classUri = this.props.classUri;
        this.className = this.props.className;
        this.objectTypeId = this.props.objectTypeId; 
        this.objectId = this.props.objectId;

        this.currentObjectId = this.objectId;
        this.attrDefValueRecs;

        onWillStart(async () => {
            const data = await this._loadAttrDefinition(this.classUri);
            this.attrDefs = JSON.parse(data)
        })

        onWillUpdateProps(async (nextProps) => {  
            this.objectId = nextProps.objectId;
            if (this.currentObjectId != this.objectId) {// rerender OTL notebook if parent object has changed
                this.otlId = nextProps.otlId;
                this.objectTypeId = nextProps.objectTypeId;
                this.classUri = nextProps.classUri;
                this.className = nextProps.className;
                
                const data = await this._loadAttrDefinition(this.classUri);
                this.attrDefs = JSON.parse(data)

                this.render();
                this.currentObjectId = this.objectId;       
            }
        })      

    }

    _loadAttrDefinition(osloclass_uri){
        const attrDefs = rpc.query({
            model: 'bms.attribute_definition',
            method: 'get_att_def',
            args: [osloclass_uri],
            }
        )
        return attrDefs   
    }

    changeOtlAndType() {
        if (this.objectId == null) { // maintainance object is new => first must be saved
            var Dialog = require('web.Dialog')
            Dialog.alert(
                this,
                "You have to save your new asset first",
                {onForceClose: function () {},confirm_callback: function () {}}
            );
        }
        else {
            var context = {
                'default_object_ids': this.objectId,
                'default_otl': this.otlId
            };
            if (this.objectTypeId) {
                context = {
                    'default_object_type': this.objectTypeId,
                    ...context
                };
            };
            const action = {
                "type": "ir.actions.act_window",
                "res_model": "bms.otl_type",
                "views": [[false, "form"]],
                "target": "current",
                "context": context,
            }
            this.actionService.doAction(action);
        }
    }

    changeAttrValue(attrDefValueRec) {
        const context = {
            'default_object_id': this.objectId,
            'default_object_type_id': this.objectTypeId,
            'default_oslo_attributen_uri': attrDefValueRec.osloattributen_uri,
            'default_attr_name': attrDefValueRec.osloattributen_name,
            'default_attr_def': attrDefValueRec.osloattributen_definition,
            'default_att_def_value_type_definition': attrDefValueRec.oslodatatype_primitive_definition_nl,
            'default_attr_def_value_type': attrDefValueRec.value_type,
            'default_value_char': attrDefValueRec.value_char,
            'default_value_boolean': attrDefValueRec.value_boolean,
            'default_value_date': attrDefValueRec.value_date,
            'default_value_datetime': attrDefValueRec.value_datetime,
            'default_value_float': attrDefValueRec.value_float,
            'default_value_integer': attrDefValueRec.value_integer,
            'form_view_initial_mode': "edit",
        }
        this.actionService.doAction(
            {
                "type": "ir.actions.act_window",
                "res_model": "bms.oslo_attributen_value_edit",
                "views": [[false, "form"]],
                "target": "inline",
                "context": context,
            }
        );
    }

    formatUnit(datatype_attr_unit_constraints) {
        if (datatype_attr_unit_constraints) {
            const r = RegExp(/(")(.*)(")/);
            const unit = r.exec(datatype_attr_unit_constraints)[2]
            return "[" + unit + "]";
        }
        else {
            return ""
        }
    }

    getValue(attrDefValueRec){
        const key = 'value_' + attrDefValueRec.value_type
        if (key in attrDefValueRec){
            return attrDefValueRec[key];
        }
        else {
            return "";
        }
    }

}

OsloType.template = "bms.oslo_type";
OsloType.components={OsloDatatypePrimitiveEnumeration, OsloDatatypeIterative};


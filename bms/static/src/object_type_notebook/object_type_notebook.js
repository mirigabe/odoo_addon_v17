// /** @odoo-module */

import { registry } from "@web/core/registry";
import { useService, useBus } from "@web/core/utils/hooks";
import { OsloType } from "./oslo_type/oslo_type";
const { Component, onMounted, onWillUpdateProps } = owl;
var core = require('web.core');


export class ObjectTypeNotebook extends Component {
    // only 1 type admitted and of AWV OTL. IF more than one type nothing is displayed !!!
    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        
        
        this.objectId = this.props.record.data.id;
        this._setup_objectType(this.props.record.data.object_type_ids.records)
      
        //this.currentObjectId = this.objectId //keep delta in case of change of object_id
        this.currentData = this.props.record.data
        
        this.existingOtls;
        
        onWillUpdateProps(async nextProps => {
            //this.objectId = nextProps.record.data.id;
            if (this.objectId != nextProps.record.data.id) {// rerender OTL notebook if another object has been changed
                this._setup_objectType(nextProps.record.data.object_type_ids.records)
                this.render()
                this.objectId = nextProps.record.data.id
                this.currentObjectId = this.objectId
                
                //console.log("object_type_notebook component - willUpdateProps done", this.objectId,  this.objectTypeId)
            }
            else if (this.currentData != nextProps.record.data) {
                console.log("object type bus triggered", nextProps.record.data.id)
                core.bus.trigger('maintainance_object_changed', nextProps.record.data.id);
                this.currentData = nextProps.record.data
            }
            
        })

        onMounted(() => {
            // monkey patching to remove class="o_field_widget o_field_object_type_notebook" automatically added for the widget by odoo an disturbing the layouting
            var element = $('[name="object_type_ids"]')
            element.removeClass()
        }
        )
    }

    changeOtlAndType() {
        //console.log("changeOtlAndType called");
        if (this.objectId == null) { // maintainance object is new => first must be saved
            var Dialog = require('web.Dialog')
            Dialog.alert(
                this,
                "You have to save your new asset first",
                {
                    onForceClose: function () {
                    },
                    confirm_callback: function () {
                    }
                }
            );
        }
        else {
            var context = { 'default_object_ids': this.objectId };
            if ((this.otlId) && (this.objectTypeId)) {
                context = {'default_otl': this.otlId,
                           'default_object_type': this.objectTypeId,
                            ...context};
            }
            else if ((this.otlId)) {
                context = { 'default_otl': this.otlId,
                            ...context};
            }
            //console.log("this", this)
            const action = {"type": "ir.actions.act_window",
                            "res_model": "bms.otl_type",
                            "views": [[false, "form"]],
                            "target": "current",
                            "context": context,}

            this.actionService.doAction(action);
        }
    }

    _setup_objectType(objectTypeIds){
        this.only1AWVtype = true
        this.hasAWVtype = true
        if (objectTypeIds.length > 1) {this.only1AWVtype = false }
        if (objectTypeIds.length == 0) {
            this.hasAWVtype = false 
            console.warn("use of hard-coded OTL ID for AWV library !!!")
            this.otlId = 1
        }
        if (objectTypeIds.length == 1) {
            this.otlId = objectTypeIds[0].data.otl_id[0]
            this.objectTypeId = objectTypeIds[0].data.id
            this.classUri = objectTypeIds[0].data.otl_type_internal_id
            this.className = objectTypeIds[0].data.name
        }
    }    

}

ObjectTypeNotebook.template = "bms.object_type_notebook";
ObjectTypeNotebook.components = { OsloType };
registry.category("fields").add("object_type_notebook", ObjectTypeNotebook)



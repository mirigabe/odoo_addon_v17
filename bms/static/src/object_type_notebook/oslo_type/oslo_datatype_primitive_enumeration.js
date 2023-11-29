// /** @odoo-module */

import { useService } from "@web/core/utils/hooks"
const { Component, onWillStart,onWillUpdateProps } = owl


export class OsloDatatypePrimitiveEnumeration extends Component {
    setup(){
        this.actionService = useService("action")
        this.ormService = useService("orm")

        this.attrValueToDisplay;       

        onWillStart(async () =>{
            this._asssign_props_value(this.props)
            const attrValueRecs = await this._load_attribute_value()
            // console.log("primitive onWillStart", this.objectId, "attValueRecs", attrValueRecs)
            this._setup_value(this.props, attrValueRecs)
            this.currentObjectId = this.objectId
            
        })
        onWillUpdateProps(async (nextProps) => {         
            this._asssign_props_value(nextProps)
            if (this.currentObjectId != this.objectId){
                const attrValueRecs = await this._load_attribute_value()
                this._setup_value(this.props, attrValueRecs)
                this.currentObjectId = this.objectId
                // console.log("primitive onWillUpdateProps", "attValueRecs", attrValueRecs)
            }
        })
    }

    changeAttrValue(){
        var context = {
            'default_object_id': this.objectId,
            'default_object_type_id': this.objectTypeId,
            'default_attr_def_id': this.attrDefId,
            'default_attr_name': this.attrName,
            'default_attr_def': this.attrDefinitionNl,
            'default_attr_def_datatype_definition': this.attrDefDatatypeDef,
            'default_attr_def_value_type': this.attrDefValueType,
            // "default_enumeration_selection_values": [],
            'form_view_initial_mode': "new",
        }
        if (this.attrValueRec) { //attribute has already a value
            context = {...context,
                    'default_value_char': this.attrValueRec.value_char,
                    'default_value_boolean': this.attrValueRec.value_boolean,
                    'default_value_date': this.attrValueRec.value_date,
                    'default_value_datetime': this.attrValueRec.value_datetime,
                    'default_value_float': this.attrValueRec.value_float,
                    'default_value_non_negative_integer': this.attrValueRec.value_non_negative_integer,
                    'default_enumeration_value_id':  this.attrValueRec.enumeration_value_id? this.attrValueRec.enumeration_value_id[0]:false}
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

    _asssign_props_value(props){
        this.objectId = props.objectId
        this.objectTypeId = props.objectTypeId
        this.attrDefId = props.attr.attr_datatype_def.attr_def_id

        this.attrName = props.attr.attr_name
        this.attrDefinitionNl = props.attr.attr_definition_nl
        this.unit = this._format_unit(props.attr.attr_datatype_def.unit) 
       
        this.attrDefDatatypeDef = props.attr.attr_datatype_def.attr_name
        this.attrDefValueType = props.attr.attr_datatype_def.attr_value_type
        this.attrOsloDatatype = props.attr.attr_datatype_def.attr_datatype
    }

    _setup_value(props, attrValueRecs){

        var valueField = "value_" + this.attrDefValueType
       
        if (attrValueRecs){ 
            this.attrValueRec = attrValueRecs[0]
            if (this.attrValueRec && this.attrDefValueType != "boolean" && this.attrValueRec[valueField] == false){
                this.attrValueRec[valueField] = ""
            }// treat case of value is false (null) in field other than boolean
        }   
        this.attrValueToDisplay = this.attrValueRec? this.attrValueRec[valueField]: ""
        
        if (this.attrOsloDatatype == "OSLOEnumeration"){// create selectionValues list useful for the form + notation to display
            Object.values(this.props.attr.attr_datatype_def.selection_values).forEach(
                (selection_value) => {                        
                    if (this.attrValueToDisplay === selection_value.selection_id){
                        // don't display the selection_id of the existing value but its notation
                        this.attrValueToDisplay = selection_value.notation
                    }
            })
        } 

    }
    _format_unit(unit){
        if(unit){
            const r = RegExp(/(")(.*)(")/);
            const formatted_unit = r.exec(unit)[2]
            return " [" + formatted_unit + "]";
        }
        else{
            return ""
        }
    }

    _load_attribute_value(){ //explicit objectId even if this.objectId to avoid caching side effects
        const domain=[["object_id", "=", this.objectId], 
                ["object_type_id","=",this.objectTypeId],
                ["attr_def_id", "=", this.attrDefId]];
        //console.log("primitive load attr domain", domain)
        const attValueRec = this.ormService.searchRead("bms.oslo_attributen_value", domain) 
        return attValueRec
    }
}

OsloDatatypePrimitiveEnumeration.template = "bms.oslo_datatype_primitive_enumeration"
// /** @odoo-module */

import { OsloDatatypePrimitiveEnumeration } from "./oslo_datatype_primitive_enumeration"
const { Component, onWillUpdateProps } = owl


export class OsloDatatypeIterative extends Component {
    setup(){

        this._assign_props_values(this.props)
        
        onWillUpdateProps(async (nextProps) => {       
            this._assign_props_values(nextProps)        
        })}

    _assign_props_values(props){
        this.attrName = props.attr.attr_name
        this.iterativeAttributes = props.attr.attr_datatype_def.iterative_attributes
        this.objectId = props.objectId
        this.objectTypeId = props.objectTypeId
    }
}

OsloDatatypeIterative.template = "bms.oslo_datatype_iterative"
OsloDatatypeIterative.components = {OsloDatatypePrimitiveEnumeration, OsloDatatypeIterative}
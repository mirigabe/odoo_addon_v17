# MS Access migration #

## Objects ##


1. Export object table from MS Access
```
SELECT object.OBJECT_ID, object.NAME, object.PARENT_ID, object.OTL_TYPE_ID, OSLOClass.uri, object.Tree_Level, object.AWV_type_not_found, object.BO_temporary_type, object.Tree_node_order
FROM [object] INNER JOIN OSLOClass ON object.OTL_TYPE_ID = OSLOClass.ID;
````

2. Import object into table bms.msa_object
```
insert into bms_maintainance_object(name, lantis_unique_id, is_active, awv_type_not_found, bo_temporary_type)
(select name, object_id as lantis_unique_id, 't' as is_active, awv_type_not_found, bo_temporary_type from bms_msa_object);
```

3. Import oslo class from MS Access db (after having created the table in Odoo)
via Odoo user interface

4. link objects with object_type base on bms_msa_object table

```
insert into bms_objects_to_types (object_id, object_type_id)
(select mo.id as mo_id
--, mo.lantis_unique_id as mo_lantis_unique_id,  object_id as msa_object_id 
--, msa_o.otl_type_id as msa_otl_type_id, oc.id as osloclass_id, oc.uri as oslo_class_uri
, ot.id as obj_type_id
from bms_msa_object msa_o
inner join bms_maintainance_object mo on cast(mo.lantis_unique_id as Integer) = msa_o.object_id 
left join bms_oslo_class oc on oc.msa_otl_type_id = msa_o.otl_type_id
left join bms_object_type ot on ot.otl_type_internal_id = msa_o.oslo_class_uri
where msa_o.otl_type_id is not null and msa_o.otl_type_id <> 0
)
;
```

## Attributen ##
1. Load attributen table with model oslo_attributen

# TODO # 
## technical ##
- [x] lazy loading for the decomposition to improve loading performance
- [X] create new object
- [ ] refresh button of decompostion
- [ ] automatic refresh of decomposition
- [ ] change parent via dropdown list
- [ ] change parent via drag&drop on decomposition
- [ ] look&feel attributes
- [ ] hover defintion attibutes
- [ ] Make the import mechanism of awv list ("keuzelijsten") better by taking into account the status change (don't  know if it happens but 
theoritically it could)
- [ ] fix tree_level which should be filled in (after having checked it's still useful)

## Governance ##
1. Unique ID asset format
2. Quid awv type not found -> use OTL lantis (and potentially create a new type? ) + problem no attribute in Relatics (no meta-model)
3. quid versionning AWV type ? by object or by "sqlite" model
4. check status of values for the value lists (oslo enumeration)?

## Refactoring ##
- [x] delete modle oslo_generic_model
- [x] attribute_value.py + views + menus + security
- [x] delte demo_agent.py
- [ ] change oslo datatype in CONSTANT VALUE defined on one place
- [ ] owl components implments props validation
- [ ] use of AWV OWL library type hardcoded in .js code
- [ ] store json of get_att_def() instead of recalulate on the fly to increase loading speed
- [ ] change res_id by default of `bms_decomposition_action`
- [ ] `get_oslo_attr_def` of `object_type.py`
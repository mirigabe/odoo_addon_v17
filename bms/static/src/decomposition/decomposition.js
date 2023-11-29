/** @odoo-module */
import { useService } from "@web/core/utils/hooks";
import { loadCSS, loadJS } from "@web/core/assets";
import { memoize } from "@web/core/utils/functions";
var core = require("web.core");
var rpc = require('web.rpc');

const { Component, onMounted, onWillStart, onWillUpdateProps } = owl;

export class Decomposition extends Component {

    setup() {
        this.ormService = useService("orm");
        this.rpcService = useService("rpc");
        this.decompositionTree;
        this.model = this.props.model;
        this.resId = this.props.resId;
        core.bus.on('maintainance_object_changed', this, this._refreshDecomposition); //record event trigger in object_type_notebook

        onWillStart(async () => {
            loadJS("/bms/static/lib/fancytree/js/jquery.fancytree-all-deps.js")
            loadJS("/bms/static/lib/fancytree/js/jquery.fancytree.dnd5.js")
            loadCSS(["/bms/static/lib/fancytree/css/skin-odoo-bms/ui.fancytree.css"]);

            this.decompositionTypeRecords = await this._loadDecompositionTypes();
            this.lazyTreeString = await this._loadLazyTree(this.resId);            
            this.lazyTreeJson = JSON.parse(this.lazyTreeString);

        })
        
        onWillUpdateProps( (nextProps) => {
            // this.resId = this.props.resId
        })

        onMounted(async () => {
            this.decompositionTree1 = $.ui.fancytree.createTree(
                '#decompositionTree_1',
                {extensions: ["dnd5"], //'edit', 'filter',
                 source: this.lazyTreeJson, 
                 click: this.loadClickedObjectId.bind(this),
                 autoScroll: true,
                 lazyLoad: (event, data) => {this._lazyLoad(event, data)},
                 dnd5:{
                    autoExpandMS: 400,
                    preventRecursion: true, // Prevent dropping nodes on own descendants
                    preventVoidMoves: true,
                    dropEffectDefault: "move", 
                    dragStart: (sourceNode, data) => { return this._dragStart(sourceNode, data)}, // must return true to enable draggin
                    dragEnd: (sourceNode, data) => { return this._dragEnd(sourceNode, data)},
                    dragEnter: (targetNode, data) => { return this._dragEnter(targetNode, data)}, // must return true to enable dropping
                    dragOver: (targetNode, data) => { return this._dragOver(targetNode, data)},
                    dragDrop: (targetNode, data) => { return this._dragDrop(targetNode, data)}
                 }

                }
            );
            this.decompositionTree1.activateKey(this.resId);

        })
    }

    loadClickedObjectId(ev, data){
        //console.log("decompostion click objectId", data.node.key)
        this.model.load({resId: parseInt(data.node.key)});

     }

    _loadDecompositionTypes() {
        return this.ormService.searchRead("bms.decomposition_type", [], []);
    }

    _loadLazyTree(object_id){
        return rpc.query({model: 'bms.decomposition_relationship',
                                   method: 'get_lazy_tree_for_object',
                                   args: [object_id], });       
    }
    
    _lazyLoad(event, data){
        var node = data.node
        var nextTree = rpc.query({
            model: 'bms.decomposition_relationship',
            method: 'get_lazy_tree',
            args: [node.key],
            }).then((tree) => {return JSON.parse(tree);});
        data.result = nextTree
        console.log("_lazyload", nextTree)

    }

    async _refreshDecomposition(objectId){
        const lazyTreeString = await this._loadLazyTree(objectId)
        const lazyTreeJson = JSON.parse(lazyTreeString)
        this.decompositionTree1.reload(lazyTreeJson)
        this.decompositionTree1.activateKey(objectId)
    }


    // function for drag&drop support on the treeview
    // --- Drag Support --------------------------------------------------------

    _dragStart(node, data){
        // Called on source node when user starts dragging `node`.
        // This method MUST be defined to enable dragging for tree nodes!
        // We can
        //   - Add or modify the drag data using `data.dataTransfer.setData()`.
        //   - Call `data.dataTransfer.setDragImage()` and set `data.useDefaultImage` to false.
        //   - Return false to cancel dragging of `node`.
  
        // Set the allowed effects (i.e. override the 'effectAllowed' option)
        //data.effectAllowed = "all";  // or 'copyMove', 'link'', ...
  
        // Set a drop effect (i.e. override the 'dropEffectDefault' option)
        // One of 'copy', 'move', 'link'.
        // In order to use a common modifier key mapping, we can use the suggested value:
        //data.dropEffect = data.dropEffectSuggested;
  
        // We could also define a custom image here (not on IE though):
        //data.dataTransfer.setDragImage($("<div>TEST</div>").appendTo("body")[0], -10, -10);
        //data.useDefaultImage = false;
  
        // Return true to allow the drag operation
        // if( node.isFolder() ) { return false; }
        data.effectAllowed = "all";
        // console.log("dragStart", data.dropEffectSuggested, data)
        return true; 
      }

    // --- Drop Support --------------------------------------------------------
    _dragEnter(node, data) {
        // Called on target node when s.th. is dragged over `node`.
        // `data.otherNode` may be a Fancytree source node or null for 
        // non-Fancytree droppables.
        // This method MUST be defined to enable dropping over tree nodes!
        //
        // We may
        //   - Set `data.dropEffect` (defaults to '')
        //   - Call `data.setDragImage()`
        //
        // Return
        //   - true to allow dropping (calc the hitMode from the cursor position)
        //   - false to prevent dropping (dragOver and dragLeave are not called)
        //   - a list (e.g. ["before", "after"]) to restrict available hitModes
        //   - a string "over", "before, or "after" to force a hitMode
        //   - Any other return value will calc the hitMode from the cursor position.
  
        // Example:
        // Prevent dropping a parent below another parent (only sort nodes under
        // the same parent):
        //if(node.parent !== data.otherNode.parent){
        //  return false;
        //}
        // Example:
        // Don't allow dropping *over* a node (which would create a child). Just
        // allow changing the order:
        //return ["before", "after"];
  
        // Accept everything:
        //data.node.info("dragEnter", data, true);
        //console.log("_dragEnter", node, data.node);
        // data.dropEffect = "move";
        // return ["over", "before", "after"];
        return true

      }
    
    _dragOver(node, data) {
        // Called on target node every few milliseconds while some source is 
        // dragged over it.
        // `data.hitMode` contains the calculated insertion point, based on cursor
        // position and the response of `dragEnter`.
        //
        // We may
        //   - Override `data.hitMode`
        //   - Set `data.dropEffect` (defaults to the value that of dragEnter)
        //     (Note: IE will ignore this and use the value from dragenter instead!)
        //   - Call `data.dataTransfer.setDragImage()`
  
        // Set a drop effect (i.e. override the 'dropEffectDefault' option)
        // One of 'copy', 'move', 'link'.
        // In order to use a common modifier key mapping, we can use the suggested value:
        // data.dropEffect = data.dropEffectSuggested;
        data.dropEffect = data.dropEffectSuggested;
      }

    _dragEnd(sourceNode, data) {
        var newParentId
        var childrenNodes

        if (data.hitMode == "over" && data.node.key != data.node.parent.key){
            newParentId = (data.node.key == 'root_1') ? null : parseInt(data.node.key)
            childrenNodes = data.node.children
        }
        else{
            newParentId = (data.node.parent.key == 'root_1') ? null : parseInt(data.node.parent.key)
            childrenNodes = data.node.parent.children
        }
 
        var newSiblingOrder = -1
        for (const idx in childrenNodes) {// store the new siblingorder and new parent_id
            var siblingId = parseInt(childrenNodes[idx].key)
            newSiblingOrder = newSiblingOrder + 1
            this._updateSiblingOrder(siblingId, newParentId, newSiblingOrder)
        }
    }

     _dragDrop(node, data) {
        // This function MUST be defined to enable dropping of items on the tree.
        //
        // The source data is provided in several formats:
        //   `data.otherNode` (null if it's not a FancytreeNode from the same page)
        //   `data.otherNodeData` (Json object; null if it's not a FancytreeNode)
        //   `data.dataTransfer.getData()`
        //
        // We may access some meta data to decide what to do:
        //   `data.hitMode` ("before", "after", or "over").
        //   `data.dataTransfer.dropEffect`,`.effectAllowed`
        //   `data.originalEvent.shiftKey`, ...
        //

        if( data.otherNode ) {
          // Drop another Fancytree node from same frame
          // (maybe from another tree however)
          var sameTree = (data.otherNode.tree === data.tree);
          data.otherNode.moveTo(node, data.hitMode);
        }

        node.setExpanded();
      }

      _updateSiblingOrder(objectId, parentId,  siblingOrder){
            this.ormService.call("bms.decomposition_relationship", "update_sibling_order", [objectId, parentId, siblingOrder], {})
            console.log("updateSiblingOrder")
      }
}

Decomposition.template = "bms.Decomposition";



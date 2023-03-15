window.cy.wheelSensitivity = 0.1

// // force single select: https://github.com/cytoscape/cytoscape.js/issues/2101
// window.cy.on('select', 'node, edge', e => window.cy.elements().not(e.target).unselect())

window.cy.on('cxttap', 'node', function (evt) {
    const hide_class = "CYTO_MESSAGE_NODE_TMP_HIDE";
    const has_child_hidden_class = "CYTO_MESSAGE_NODE_HAS_CHILD_TMP_HIDDEN"
    let node = evt.target
    let successors = node.successors()
    let children = node.outgoers()

    // escape leafs
    if (children.length === 0) {
        return
    }

    let child_already_hidden = children[0].hasClass(hide_class)
    if (child_already_hidden){
        node.removeClass(has_child_hidden_class)
    } else {
        node.addClass(has_child_hidden_class)
    }

    for (let i = 0, len = successors.length; i < len; i++) {
        let successor = successors[i]
        successor.removeClass(hide_class)
        successor.removeClass(has_child_hidden_class)
        if (child_already_hidden) {
        } else {
            successor.addClass(hide_class)
        }
    }
});
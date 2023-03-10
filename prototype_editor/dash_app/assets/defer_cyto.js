window.cy.on('cxttap', 'node', function (evt) {
    const hide_class = "CYTO_MESSAGE_NODE_TMP_HIDE"
    let node = evt.target
    let successors = node.successors()
    let children = node.outgoers()

    // escape leafs
    if (children.length === 0) {
        return
    }

    let child_already_hidden = children[0].hasClass(hide_class)

    for (let i = 0, len = successors.length; i < len; i++) {
        let successor = successors[i]
        if (child_already_hidden) {
            successor.removeClass(hide_class)
        } else {
            successor.addClass(hide_class)
        }
    }
});
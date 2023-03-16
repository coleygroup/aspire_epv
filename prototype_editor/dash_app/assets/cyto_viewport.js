const mtt_layout = {
    name: 'dagre',
    nodeDimensionsIncludeLabels: true,
    animate: true,
    animationDuration: 1000,
    align: 'UL',
};

const mot_layout = {
    name: 'dagre',
    nodeDimensionsIncludeLabels: true,
    align: 'UL',
};

const hide_class = "CYTO_MESSAGE_NODE_TMP_HIDE";

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside_viewport: {
        // pan to graph center
        cy_fit: function () {
            window.cy.fit()  // this is pan and fit
        },

        // pan to the geo center of selected nodes
        cy_center_selected: function () {
            window.cy.center(
                window.cy.$(':selected')
            )
        },
        // run layout
        cy_run_mtt_layout: function () {
            // if layout has animation then `run` just trigger the animation,
            // so there will be problem if `zoom` and `pan` executed right after it
            window.cy.layout(mtt_layout).run()
        },

        // run layout
        cy_run_mot_layout: function (n_clicks) {
            let current_zoom = window.cy.zoom()
            let current_pan = {...window.cy.pan()}
            window.cy.layout(mot_layout).run()
            window.cy.zoom(current_zoom)
            window.cy.pan(current_pan)
        },

        // select element by data id
        cy_select_element_by_id: function (data_id) {
            if (data_id) {
                window.cy.elements(`[ id="${data_id}" ]`).select()
            }
        },

        // pan to element by data id
        cy_pan_to_element: function (data_id, n_clicks) {
            if (data_id) {
                let ele = window.cy.elements(`[ id="${data_id}" ]`)
                window.cy.elements().removeClass("CYTO_MESSAGE_NODE_NAV_FOCUS")
                ele.addClass("CYTO_MESSAGE_NODE_NAV_FOCUS")
                window.cy.center(ele)
            }
        },


        cy_hide_non_successors: function (n_clicks) {
            let nodes = window.cy.$('node')
            if (n_clicks) {
                let selected_nodes = window.cy.$('node:selected')
                if (selected_nodes.length < 1) {
                    return
                }
                let selected_node = selected_nodes[0]

                let successors = selected_node.successors()
                let non_successors0 = nodes.difference(successors)
                let non_successors = non_successors0.difference(selected_node)
                for (let i = 0, len = non_successors.length; i < len; i++) {
                    let non_successor = non_successors[i]
                    if (!non_successor.hasClass(hide_class)) {
                        non_successor.addClass(hide_class)
                    }
                }
            }
        },

        cy_show_all: function (n_clicks) {
            let eles = window.cy.elements()
            if (n_clicks) {
                for (let i = 0, len = eles.length; i < len; i++) {
                    let ele = eles[i]
                    if (ele.hasClass(hide_class)) {
                        ele.removeClass(hide_class)
                    }
                }
            }
        },

        cy_derive_relations: function (dummy) {
            let nodes = window.cy.elements('node')
            for (let i = 0, len = nodes.length; i < len; i++) {
                let n = nodes[i]
                let edges_incoming_to_n = n.incomers('edge')
                if (edges_incoming_to_n.length === 0) {
                    n.data('relation', '\<ROOT\>')
                } else {
                    let edge = edges_incoming_to_n[0]  // we got a tree
                    let parent = n.incomers('node')[0]
                    let relation = edge.data('ele_attrs')['mot_value']
                    let prefix = ""
                    if (parent.data('ele_attrs')['mot_class_string'] === 'builtins.list') {
                        prefix += '\<ListIndex\>'
                    }
                    if (parent.data('ele_attrs')['mot_class_string'] === 'builtins.dict') {
                        prefix += '\<DictKey\>'
                    }
                    n.data('relation', prefix + relation)
                }
            }
        },
    }
});

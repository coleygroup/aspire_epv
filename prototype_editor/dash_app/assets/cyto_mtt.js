// functions supporting mtt
const mtt_layout = {
        name: 'dagre',
        nodeDimensionsIncludeLabels: true,
        animate: true,
        animationDuration: 1000,
        align: 'UL',
    }

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        // pan to graph center
        cy_fit: function() {
            window.cy.fit()  // this is pan and fit
        },

        // pan to the geo center of selected nodes
        cy_center_selected: function() {
            window.cy.center(
                window.cy.$(':selected')
            )
        },
        // run layout
        cy_run_mtt_layout: function() {
            // let current_zoom = window.cy.zoom()
            // let current_pan = {...window.cy.pan()}
            window.cy.layout(mtt_layout).run()
            // window.cy.zoom(current_zoom)
            // window.cy.pan(current_pan)
        },

        // select element by data id
        cy_select_element: function(data_id) {
            if (data_id){
                window.cy.elements(`[ id="${data_id}" ]`).select()
            }
        },

        // pan to element by data id
        cy_pan_to_element: function(data_id) {
            if (data_id){
                let ele = window.cy.elements(`[ id="${data_id}" ]`)
                window.cy.center(ele)
            }
        },
    }
});
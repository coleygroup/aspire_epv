window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        // pan to graph center
        cy_fit: function(x, y) {
            window.cy.fit()  // this is pan and fit
        },
        // pan to the geo center of selected nodes
        cy_center_selected: function() {
            window.cy.center(
                window.cy.$(':selected')
            )
        },
        // run layout
        cy_run_layout: function(layout_options, n_clicks) {
            let current_zoom = window.cy.zoom()
            let current_pan = {...window.cy.pan()}
            window.cy.layout(layout_options).run()
            window.cy.zoom(current_zoom)
            window.cy.pan(current_pan)
        },
        // select element by data id
        cy_select_element: function(data_id) {
            window.cy.elements(`[ id="${data_id}" ]`).select()
        },
    }
});
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        // pan to graph center
        cy_fit: function(x, y) {
            window.cy.fit()  // this is pan and fit
        },
        // pan to the geo center of selected nodes
        cy_center_selected: function(){
            window.cy.center(
                window.cy.$(':selected')
            )
        }
    }
});
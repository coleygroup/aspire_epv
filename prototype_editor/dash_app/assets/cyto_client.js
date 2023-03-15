// const placeholder_class = "CYTO_PLACEHOLDER_CLASS";
// const preset_class = "CYTO_PRESET_CLASS";
// const literal_node_class = "CYTO_LITERAL_NODE_CLASS";
// const edge_can_edit_class = "CYTO_MESSAGE_EDGE_CAN_EDIT_CLASS";
//
// window.dash_clientside = Object.assign({}, window.dash_clientside, {
//     clientside_client: {
//         cy_mot_editor: function (is_placeholder, value_value, state_id, value_id) {
//             // let state_dict = JSON.stringify(state_id[0], Object.keys(state_id[0]).sort())
//             // let value_dict = JSON.stringify(value_id[0], Object.keys(value_id[0]).sort())
//             if (state_id.length === 0) {
//                 return
//             }
//             let state_dict = state_id[0]
//             let element_id = '' + state_dict['index']
//             let element = window.cy.elements(`[ id="${element_id}" ]`)
//             // let ele = element[0]
//             let new_attrs = {...element.data('ele_attrs')}
//             let state_value = "PT_PRESET"
//             if (is_placeholder[0] === true){
//                 state_value = "PT_PLACEHOLDER"
//             }
//             new_attrs['mot_state'] = state_value
//             new_attrs['mot_value'] = value_value[0]
//             element.data('ele_attrs', new_attrs)
//
//             let can_edit = element.hasClass(literal_node_class) || element.hasClass(edge_can_edit_class)
//
//             if (state_value === 'PT_PLACEHOLDER') {
//                 element.removeClass(preset_class)
//                 element.addClass(placeholder_class)
//                 if (!can_edit){
//                     let successors0 = element.successors()
//                     let successors = successors0.difference(element)
//                     successors.remove()
//                 }
//             } else {
//                 if (can_edit){
//                     element.addClass(preset_class)
//                     element.removeClass(placeholder_class)
//                 }
//                 else {
//                     element.removeClass(preset_class)
//                     element.removeClass(placeholder_class)
//                 }
//                 // let remove_both_state_classes = true
//                 // let literals = ['builtins.str', 'builtins.float', 'builtins.int', 'builtins.bytes']
//                 // if (class_string.startsWith('builtins.')){
//                 //     if (class_string !== 'builtins.list' || class_string !== 'builtins.dict') or
//                 // }
//
//                 // if new_attrs['mot_class_string']
//             }
//         }
//     }
// });

# cyto element classes for style sheet
CYTO_LITERAL_NODE_CLASS = ".CYTO_LITERAL_NODE_CLASS"
CYTO_MUTABLE_NODE_CLASS = ".CYTO_MUTABLE_NODE_CLASS"
CYTO_MESSAGE_NODE_CLASS = ".CYTO_MESSAGE_NODE_CLASS"

CYTO_MESSAGE_EDGE_CAN_EDIT_CLASS = ".CYTO_MESSAGE_EDGE_CAN_EDIT_CLASS"

CYTO_MESSAGE_NODE_TMP_HIDE = ".CYTO_MESSAGE_NODE_TMP_HIDE"
CYTO_MESSAGE_NODE_NAV_FOCUS = ".CYTO_MESSAGE_NODE_NAV_FOCUS"

CYTO_PRESET_CLASS = ".CYTO_PRESET_CLASS"
CYTO_PLACEHOLDER_CLASS = ".CYTO_PLACEHOLDER_CLASS"

CYTO_STYLE_SHEET_MTT = [
    {
        'selector': 'edge',
        'style': {
            'opacity': 1,
            'curve-style': 'taxi',
            # 'curve-style': 'unbundled-bezier',  # this also works
            'taxi-direction': 'vertical',
        }
    },
    {
        'selector': 'edge[edge_color]',
        'style': {
            'color': 'data(edge_color)',
        }
    },
    {
        'selector': 'node',
        'style': {
            'content': 'data(label)',
            'border-width': 2,
            'text-valign': 'center',
            'padding': "10px",
            'width': 'label',
            'height': '18px',
            'font-size': '18px'
        }
    },
    {
        'selector': '[oneof_color]',
        'style': {
            'border-color': 'data(oneof_color)',
        }
    },

    # class selectors
    {
        'selector': CYTO_LITERAL_NODE_CLASS,
        'style': {
            'shape': 'rectangle',
            # 'background-color': 'none',
            'text-background-color': 'black',
        }
    },
    {
        'selector': CYTO_MUTABLE_NODE_CLASS,
        'style': {
            'shape': 'round-octagon',
            'background-color': 'white',
        }
    },
    {
        'selector': CYTO_MESSAGE_NODE_CLASS,
        'style': {
            'shape': 'rectangle',
            'background-color': 'white',
        }
    },

    {
        'selector': CYTO_MESSAGE_EDGE_CAN_EDIT_CLASS,
        'style': {
            'width': '10',
        }
    },
    {
        'selector': CYTO_MESSAGE_NODE_TMP_HIDE,
        'style': {
            'display': 'none',
            'visibility': 'hidden',
        }
    },

    {
        'selector': ':selected',
        'style': {
            'z-index': 1000,
            'background-color': 'SteelBlue',
            'line-color': 'SteelBlue',
        }
    },
]

CYTO_STYLE_SHEET_MOT = [
    {
        'selector': 'edge',
        'style': {
            'opacity': 1,
            'curve-style': 'taxi',
            'taxi-direction': 'vertical',
        }
    },
    {
        'selector': 'node',
        'style': {
            'content': 'data(label)',
            'border-width': 2,
            'font-size': "30px",
            'text-valign': 'bottom',
            'text-margin-y': "4px",
        }
    },

    # class selectors
    {
        'selector': CYTO_LITERAL_NODE_CLASS,
        'style': {
            'shape': 'rectangle',
            'text-background-color': 'black',
        }
    },
    {
        'selector': CYTO_MUTABLE_NODE_CLASS,
        'style': {
            'shape': 'round-octagon',
            'background-color': 'white',
        }
    },
    {
        'selector': CYTO_MESSAGE_NODE_CLASS,
        'style': {
            'shape': 'rectangle',
            'background-color': 'white',
        }
    },

    {
        'selector': f'node{CYTO_PLACEHOLDER_CLASS}',
        'style': {
            'border-width': '5',
            'border-color': 'red',
        }
    },

    {
        'selector': f'node{CYTO_PRESET_CLASS}',
        'style': {
            'border-width': '5',
            'border-color': 'green',
        }
    },

    {
        'selector': CYTO_MESSAGE_EDGE_CAN_EDIT_CLASS,
        'style': {
            'width': '10',
        }
    },
    {
        'selector': f"edge{CYTO_PLACEHOLDER_CLASS}",
        'style': {
            'line-color': 'red',
        }
    },

    {
        'selector': f"edge{CYTO_PRESET_CLASS}",
        'style': {
            'line-color': 'green',
        }
    },

    {
        'selector': CYTO_MESSAGE_NODE_TMP_HIDE,
        'style': {
            'display': 'none',
            'visibility': 'hidden',
        }
    },

    {
        'selector': f'node{CYTO_MESSAGE_NODE_NAV_FOCUS}',
        'style': {
            'background-color': 'yellow',
        }
    },

    {
        'selector': f'edge{CYTO_MESSAGE_NODE_NAV_FOCUS}',
        'style': {
            'line-color': 'yellow',
            'width': 10,
        }
    },

    {
        'selector': ':selected',
        'style': {
            'z-index': 1000,
            'background-color': 'SteelBlue',
            'line-color': 'SteelBlue',
        }
    },
]

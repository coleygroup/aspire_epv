from .style_class import *

CYTO_STYLE_SHEET_MTT = [
    {
        'selector': 'edge',
        'style': {
            'opacity': 1,
            'curve-style': 'taxi',  # or 'unbundled-bezier'
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
        'selector': "." + CYTO_LITERAL_NODE_CLASS,
        'style': {
            'shape': 'rectangle',
            # 'background-color': 'none',
            'text-background-color': 'black',
        }
    },

    {
        'selector': "." + CYTO_MUTABLE_NODE_CLASS,
        'style': {
            'shape': 'round-octagon',
            'background-color': 'white',
        }
    },

    {
        'selector': "." + CYTO_MESSAGE_NODE_CLASS,
        'style': {
            'shape': 'rectangle',
            'background-color': 'white',
        }
    },

    {
        'selector': "." + CYTO_MESSAGE_EDGE_CAN_EDIT_CLASS,
        'style': {
            'width': '10',
        }
    },

    {
        'selector': "." + CYTO_MESSAGE_NODE_TMP_HIDE,
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

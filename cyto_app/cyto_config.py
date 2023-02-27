# plotly component ID
DASH_CID_NAVBAR = "CID_NAVBAR"

DASH_CID_MTT_CYTO = "CID_MTT_CYTO"
DASH_CID_MTT_DIV_INFO_ELEMENT = "CID_MTT_DIV_INFO_ELEMENT"
DASH_CID_MTT_DIV_INFO_TREE = "CID_MTT_DIV_INFO_TREE"
DASH_CID_MTT_SELECTOR = "CID_MTT_SELECTOR"
DASH_CID_MTT_SWITCHES = "CID_MTT_SWITCHES"

DASH_CID_MOT_CYTO = "CID_MOT_CYTO"
DASH_CID_MOT_DIV_EDITOR = "CID_MOT_DIV_EDITOR"
DASH_CID_MOT_DIV_EDITOR_ELEMENT_STATE = "CID_MOT_DIV_EDITOR_ELEMENT_STATE"
DASH_CID_MOT_SWITCHES = "CID_MOT_SWITCHES"
DASH_CID_MOT_BTN_DOWNLOAD = "CID_MOT_BTN_DOWNLOAD"
DASH_CID_MOT_BTN_SAVETODB = "CID_MOT_BTN_SAVETODB"
DASH_CID_MOT_BTN_PT_EXTEND = "CID_MOT_BTN_PT_EXTEND"
DASH_CID_MOT_BTN_PT_DETACH = "CID_MOT_BTN_PT_DETACH"
DASH_CID_MOT_BTN_PT_DELETE = "CID_MOT_BTN_PT_DELETE"
DASH_CID_MOT_BTN_PT_HIDE = "CID_MOT_BTN_PT_HIDE"
DASH_CID_MOT_BTN_PT_SHOWONLY = "CID_MOT_BTN_PT_SHOWONLY"
DASH_CID_MOT_INPUT_PT_ELEMENT_STATE = "CID_MOT_INPUT_PT_ELEMENT_STATE"
DASH_CID_MOT_INPUT_PT_ELEMENT_VALUE = "CID_MOT_INPUT_PT_ELEMENT_VALUE"
DASH_CID_MOT_STORE_INIT = "CID_MOT_STORE_INIT"
DASH_CID_MOT_STORE_LIVE = "CID_MOT_STORE_LIVE"

# cyto element classes for style sheet
CYTO_LITERAL_NODE_CLASS = ".CYTO_LITERAL_NODE_CLASS"
CYTO_MUTABLE_NODE_CLASS = ".CYTO_MUTABLE_NODE_CLASS"
CYTO_MESSAGE_NODE_CLASS = ".CYTO_MESSAGE_NODE_CLASS"
# CYTO_ONEOF_EDGE_CLASS = ".CYTO_ONEOF_EDGE_CLASS"

CYTO_MESSAGE_NODE_LITERAL_CLASS = ".CYTO_MESSAGE_NODE_LITERAL_CLASS"
CYTO_MESSAGE_NODE_HAS_LITERAL_CHILDREN_CLASS = ".CYTO_MESSAGE_NODE_HAS_LITERAL_CHILDREN_CLASS"
CYTO_MESSAGE_NODE_HAS_LITERAL_CHILDREN_PRESET_CLASS = ".CYTO_MESSAGE_NODE_HAS_LITERAL_CHILDREN_PRESET_CLASS"
CYTO_MESSAGE_NODE_HAS_LITERAL_CHILDREN_PLACEHOLDER_CLASS = ".CYTO_MESSAGE_NODE_HAS_LITERAL_CHILDREN_PLACEHOLDER_CLASS"

CYTO_MESSAGE_EDGE_CAN_EDIT_CLASS = ".CYTO_MESSAGE_EDGE_CAN_EDIT_CLASS"
CYTO_MESSAGE_EDGE_PRESET_CLASS = ".CYTO_MESSAGE_EDGE_PRESET_CLASS"
CYTO_MESSAGE_EDGE_PLACEHOLDER_CLASS = ".CYTO_MESSAGE_EDGE_PLACEHOLDER_CLASS"

CYTO_STYLE_SHEET_MTT = [
    {
        'selector': 'edge',
        'style': {
            # 'content': 'data(label)',
            'color': 'data(edge_color)',
            'opacity': 1,
            'curve-style': 'taxi',
            # 'curve-style': 'unbundled-bezier',  # this also works
            'taxi-direction': 'vertical',
        }
    },
    {
        'selector': 'node',
        'style': {
            'content': 'data(label)',
            'border-color': 'data(oneof_color)',
            'border-width': 2,
            # 'text-halign': 'right',
            # 'text-valign': 'center',
            # 'text-margin-x': 2,
        }
    },

    # class selectors
    {
        'selector': CYTO_LITERAL_NODE_CLASS,
        'style': {
            'shape': 'triangle',
        }
    },
    {
        'selector': CYTO_MUTABLE_NODE_CLASS,
        'style': {
            'shape': 'rectangle',
        }
    },
    {
        'selector': CYTO_MESSAGE_NODE_CLASS,
        'style': {
            'shape': 'round-octagon',
        }
    },

    {
        'selector': CYTO_MESSAGE_NODE_HAS_LITERAL_CHILDREN_CLASS,
        'style': {
            'border-width': '10',
        }
    },

    {
        'selector': CYTO_MESSAGE_NODE_HAS_LITERAL_CHILDREN_PLACEHOLDER_CLASS,
        'style': {
            'border-color': 'red',
        }
    },

    {
        'selector': CYTO_MESSAGE_NODE_HAS_LITERAL_CHILDREN_PRESET_CLASS,
        'style': {
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
        'selector': CYTO_MESSAGE_EDGE_PLACEHOLDER_CLASS,
        'style': {
            'line-color': 'red',
        }
    },

    {
        'selector': CYTO_MESSAGE_EDGE_PRESET_CLASS,
        'style': {
            'line-color': 'green',
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

# plotly component ID
DASH_CID_CYTO = "CID_CYTO"
DASH_CID_NAVBAR = "CID_NAVBAR"
DASH_CID_MTT_DIV_INFO_ELEMENT = "CID_MTT_DIV_INFO_ELEMENT"
DASH_CID_MTT_DIV_INFO_TREE = "CID_MTT_DIV_INFO_TREE"
DASH_CID_MTT_SELECTOR = "CID_MTT_SELECTOR"
DASH_CID_MTT_SWITCHES = "CID_MTT_SWITCHES"

# cyto element classes for style sheet
CYTO_LITERAL_NODE_CLASS = ".CYTO_LITERAL_NODE_CLASS"
CYTO_MUTABLE_NODE_CLASS = ".CYTO_MUTABLE_NODE_CLASS"
CYTO_MESSAGE_NODE_CLASS = ".CYTO_MESSAGE_NODE_CLASS"
CYTO_ONEOF_EDGE_CLASS = ".CYTO_ONEOF_EDGE_CLASS"

CYTO_STYLE_SHEET = [
    {
        'selector': 'edge',
        'style': {
            # 'content': 'data(label)',
            'color': 'data(edge_color)',
            # 'curve-style': 'taxi',
            'opacity': 0.4,
            # 'curve-style': 'haystack',
            # 'curve-style': 'bezier',
            # 'curve-style': 'cubic-bezier',
            'curve-style': 'unbundled-bezier',
            # 'curve-style': 'segments',
        }
    },
    {
        'selector': 'node',
        'style': {
            'content': 'data(label)',
            'border-color': 'data(oneof_color)',
            'border-width': 2,
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
    }
]

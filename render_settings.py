# render_settings.py
import plot_tools

VERTICAL_OFFSET = 0.1       # Offset for drawing parasite nodes above host nodes
COSPECIATION_OFFSET = 0.8   # Offest for drawing parasite nodes closer to host 
                            # nodes for speciation events
                        
LEAF_NODE_COLOR = plot_tools.MAROON
COSPECIATION_NODE_COLOR = plot_tools.BLUE
DUPLICATION_NODE_COLOR = plot_tools.GREEN
TRANSFER_NODE_COLOR = plot_tools.RED
HOST_NODE_COLOR = plot_tools.BLACK
HOST_EDGE_COLOR = plot_tools.BLACK
PARASITE_EDGE_COLOR = plot_tools.GRAY
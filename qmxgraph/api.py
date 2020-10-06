import weakref

import qmxgraph.debug
import qmxgraph.js


class QmxGraphApi(object):
    """
    Python binding for API used to control underlying JavaScript's mxGraph
    graph drawing library.
    """

    SOURCE_TERMINAL_CELL = 'source'
    TARGET_TERMINAL_CELL = 'target'

    LAYOUT_ORGANIC = 'organic'
    LAYOUT_COMPACT = 'compact'
    LAYOUT_CIRCLE = 'circle'
    LAYOUT_COMPACT_TREE = 'compact_tree'
    LAYOUT_EDGE_LABEL = 'edge_label'
    LAYOUT_PARALLEL_EDGE = 'parallel_edge'
    LAYOUT_PARTITION = 'partition'
    LAYOUT_RADIAL_TREE = 'radial_tree'
    LAYOUT_STACK = 'stack'

    def __init__(self, graph):
        """
        :param qmxgraph.widget.QmxGraph graph: A graph drawing widget.
        """
        self._graph = weakref.ref(graph)

    def insert_vertex(self, result_callback, x, y, width, height, label,
                      style=None, tags=None, id=None):
        """
        Inserts a new vertex in graph.

        :param Callable[[str],None] result_callback: This call receives the id
            of new vertex.
        :param int x: X coordinate in screen coordinates.
        :param int y: Y coordinate in screen coordinates.
        :param int width: Width in pixels.
        :param int height: Height in pixels.
        :param str label: Label of vertex.
        :param str|None style: Name of style to be used. Styles
            available are all default ones provided by mxGraph plus additional
            ones configured in initialization of this class.
        :param dict[str,str]|None tags: Tags are basically custom attributes
            that may be added to a cell that may be later queried (or even
            modified), with the objective of allowing better inspection and
            interaction with cells in a graph.
        :param Optional[str] id: The id of the edge. If omitted (or non
            unique) an id is generated.
        """
        return self.call_api(
            result_callback, 'insertVertex', x, y, width, height, label,
            style, tags, id)

    def insert_port(self, result_callback, vertex_id, port_name, x, y, width,
                    height, label=None, style=None, tags=None):
        """
        Inserts a new port in vertex.

        :param Callable[[Any],None] result_callback: This is called after the
            underlying method executes.
        :param str vertex_id: The id of the vertex to witch add this port.
        :param str port_name: The name used to refer to the new port.
        :param float x: The normalized (0-1) X coordinate for the port
            (relative to vertex bounds).
        :param float y: The normalized (0-1) Y coordinate for the port
            (relative to vertex bounds).
        :param int width: Width of port.
        :param int height: Height of port.
        :param str|None label: Label of port.
        :param str|None style: Name of style to be used. Styles
            available are all default ones provided by mxGraph plus additional
            ones configured in initialization of this class.
        :param dict[str,str]|None tags: Tags are basically custom attributes
            that may be added to a cell that may be later queried (or even
            modified), with the objective of allowing better inspection and
            interaction with cells in a graph.
        """
        return self.call_api(
            result_callback, 'insertPort', vertex_id, port_name, x, y, width,
            height, label, style, tags)

    def insert_edge(self, result_callback, source_id, target_id, label,
                    style=None, tags=None, source_port_name=None,
                    target_port_name=None, id=None):
        """
        Inserts a new edge between two vertices in graph.

        :param Callable[[str],None] result_callback: This call receives the id
            of new edge.
        :param str source_id: Id of source vertex in graph.
        :param str target_id: Id of target vertex in graph.
        :param str label: Label of edge.
        :param str|None style: Name of style to be used. Styles
            available are all default ones provided by mxGraph plus additional
            ones configured in initialization of this class.
        :param dict[str,str]|None tags: Tags are basically custom attributes
            that may be added to a cell that may be later queried (or even
            modified), with the objective of allowing better inspection and
            interaction with cells in a graph.
        :param str|None source_port_name: The name of the port used to connect
            to source vertex.
        :param str|None target_port_name: The name of the port used to connect
            to target vertex.
        :param Optional[str] id: The id of the edge. If omitted (or non
            unique) an id is generated.
        """
        return self.call_api(
            result_callback, 'insertEdge', source_id, target_id, label, style,
            tags, source_port_name, target_port_name, id)

    def insert_decoration(self, result_callback, x, y, width, height, label,
                          style=None, tags=None, id=None):
        """
        Inserts a new decoration over an edge in graph. A decoration is
        basically an overlay object that is representing some entity over the
        path of an edge.

        Note that x and y must be inside the bounds of an edge, otherwise this
        call will raise.

        :param Callable[[str],None] result_callback: This call receives the id
            of new decoration.
        :param int x: X coordinate in screen coordinates.
        :param int y: Y coordinate in screen coordinates.
        :param int width: Width in pixels.
        :param int height: Height in pixels.
        :param str label: Label of decoration.
        :param str|None style: Name of style to be used. Styles
            available are all default ones provided by mxGraph plus additional
            ones configured in initialization of this class.
        :param dict[str,str]|None tags: Tags are basically custom attributes
            that may be added to a cell that may be later queried (or even
            modified), with the objective of allowing better inspection and
            interaction with cells in a graph.
        :param Optional[str] id: The id of the decoration. If omitted (or non
            unique) an id is generated.
        """
        return self.call_api(
            result_callback, 'insertDecoration', x, y, width, height, label,
            style, tags, id)

    def insert_decoration_on_edge(self, result_callback, edge_id, position,
                                  width, height, label, style=None, tags=None,
                                  id=None):
        """
        Inserts a new decoration over an edge in graph. A decoration is
        basically an overlay object that is representing some entity over the
        path of an edge.

        Note that x and y must be inside the bounds of an edge, otherwise this
        call will raise.

        :param Callable[[str],None] result_callback: This call receives the id
            of new decoration.
        :param str edge_id: Id of an edge in graph.
        :param float position: The normalized position in the edge.
        :param int width: Width in pixels.
        :param int height: Height in pixels.
        :param str label: Label of decoration.
        :param str|None style: Name of style to be used. Styles
            available are all default ones provided by mxGraph plus additional
            ones configured in initialization of this class.
        :param dict[str,str]|None tags: Tags are basically custom attributes
            that may be added to a cell that may be later queried (or even
            modified), with the objective of allowing better inspection and
            interaction with cells in a graph.
        :param Optional[str] id: The id of the decoration. If omitted (or non
            unique) an id is generated.
        """
        return self.call_api(
            result_callback, 'insertDecorationOnEdge', edge_id, position,
            width, height, label, style, tags, id)

    def insert_table(self, result_callback, x, y, width, contents, title,
                     tags=None, style=None, parent_id=None, id=None):
        """
        Inserts a new table in graph. A table is an object that can be used
        in graph to display tabular information about other cells, for
        instance. Tables can't be connected to other cells like vertices,
        edges nor decorations.

        :param Callable[[str],None] result_callback: This call receives the id
            of new table.
        :param int x: X coordinate in screen coordinates.
        :param int y: Y coordinate in screen coordinates.
        :param int width: Width in pixels.
        :param qmxgraph.decoration_contents.Table contents:
            The table contents.
        :param str title: Title of table.
        :param dict[str,str]|None tags: Tags are basically custom attributes
            that may be added to a cell that may be later queried (or even
            modified), with the objective of allowing better inspection and
            interaction with cells in a graph.
        :param str|None style: Name of style to be used (Note that the
            `'table'` style is always used, options configured with this style
            have greater precedence). Styles available are all default ones
            provided by mxGraph plus additional ones configured in
            initialization of this class.
        :param str|None parent_id: If not `None` the created table is placed
            in a relative position to the cell with id `parent_id`.
        :param Optional[str] id: The id of the table. If omitted (or non
            unique) an id is generated.
        """
        from . import decoration_contents
        contents = decoration_contents.asdict(contents)
        return self.call_api(
            result_callback, 'insertTable', x, y, width, contents, title,
            tags, style, parent_id, id)

    def update_table(self, result_callback, table_id, contents, title):
        """
        Update contents and title of a table in graph.

        :param Callable[[Any],None] result_callback: This is called after the
            underlying method executes.
        :param str table_id: Id of a table in graph.
        :param qmxgraph.decoration_contents.Table contents:
            The table contents.
        :param str title: Title of table.
        """
        from . import decoration_contents
        contents = decoration_contents.asdict(contents)
        return self.call_api(
            result_callback, 'updateTable', table_id, contents, title)

    def group(self, result_callback):
        """
        Create a group with currently selected cells in graph. Edges connected
        between selected vertices are automatically also included in group.

        :param Callable[[Any],None] result_callback: This is called after the
            underlying method executes.
        """
        return self.call_api(result_callback, 'group')

    def ungroup(self, result_callback):
        """
        Ungroup currently selected group.

        :param Callable[[Any],None] result_callback: This is called after the
            underlying method executes.
        """
        return self.call_api(result_callback, 'ungroup')

    def toggle_outline(self, result_callback):
        """
        Outline is a small window that shows an overview of graph. It usually
        starts disabled and can be shown on demand.

        :param Callable[[Any],None] result_callback: This is called after the
            underlying method executes.
        """
        return self.call_api(result_callback, 'toggleOutline')

    def toggle_grid(self, result_callback):
        """
        The grid in background of graph helps aligning cells inside graph. It
        usually starts enabled and can be hidden on demand.

        :param Callable[[Any],None] result_callback: This is called after the
            underlying method executes.
        """
        return self.call_api(result_callback, 'toggleGrid')

    def toggle_snap(self, result_callback):
        """
        Snap feature forces vertices to be moved in a way its bounds match
        grid. It usually starts enabled and can be disabled on demand.

        Note that if grid is hidden this feature is also disabled.

        :param Callable[[Any],None] result_callback: This is called after the
            underlying method executes.
        """
        return self.call_api(result_callback, 'toggleSnap')

    def get_cell_id_at(self, result_callback, x, y):
        """
        Gets the id of cell at given coordinates.

        :param Callable[[Optional[str]],None] result_callback: This callback
            receives id of cell at given position, if no cell is found None.
        :param int x: X coordinate in screen coordinates.
        :param int y: Y coordinate in screen coordinates.
        """
        return self.call_api(result_callback, 'getCellIdAt', x, y)

    def get_decoration_parent_cell_id(self, result_callback, cell_id):
        """
        Get the id of the edge that contains the decoration with the given
        cell id.

        :param Callable[[str],None] result_callback: This callback receives
            the id of the edge containing the given decoration.
        :param str cell_id: THe decoration's id.
        """
        return self.call_api(
            result_callback, 'getDecorationParentCellId', cell_id)

    def has_cell(self, result_callback, cell_id):
        """
        Indicates if cell exists.

        :param Callable[[bool],None] result_callback: This callback receives a
            boolean indication in the cell exists.
        :param str cell_id: Id of a cell in graph.
        """
        return self.call_api(result_callback, 'hasCell', cell_id)

    def has_port(self, result_callback, cell_id, port_name):
        """
        Indicates if the port exists.

        :param Callable[[bool],None] result_callback: This callback receives a
            boolean indication in the port exists.
        :param str cell_id: Id of a cell in graph.
        :param str port_name: Name of the expected port.
        """
        return self.call_api(result_callback, 'hasPort', cell_id, port_name)

    def get_cell_type(self, result_callback, cell_id):
        """
        :param Callable[[str],None] result_callback: This callback receives a
            boolean indication in the port exists.
        :param str cell_id: Id of a cell in graph.
        :rtype: str
        :return: Possible returns are:

            - :data:`qmxgraph.constants.CELL_TYPE_VERTEX` for vertices;
            - :data:`qmxgraph.constants.CELL_TYPE_EDGE` for edges;
            - :data:`qmxgraph.constants.CELL_TYPE_DECORATION` for decorations;
            - :data:`qmxgraph.constants.CELL_TYPE_TABLE` for tables;

            It raises if none of these types are a match.
        """
        return self.call_api(result_callback, 'getCellType', cell_id)

    def get_geometry(self, result_callback, cell_id):
        """
        Gets the geometry of cell in screen coordinates.

        :param Callable[[List[float]],None] result_callback: This callback
            receives cell geometry data as 4 floats:

            - x;
            - y;
            - width;
            - height;

        :param str cell_id: Id of a cell in graph.
        """
        return self.call_api(result_callback, 'getGeometry', cell_id)

    def get_terminal_points(self, result_callback, cell_id):
        """
        Gets the terminal points of an edge;

        :param Callable[[List[List[float]]],None] result_callback:
            This callback receives cell terminal coordinates a list of two
            list and 2 float each list:

            - - the source x coordinate;
              - the source y coordinate;

            - - the target x coordinate;
              - the target y coordinate;

        :param str cell_id: Id of a edge in graph.
        """
        return self.call_api(result_callback, 'getEdgeTerminalPoints', cell_id)

    def get_decoration_position(self, result_callback, cell_id):
        """
        Gets the decoration's relative position.

        :param Callable[[float],None] result_callback: This callback receives a
            normalized number between [0, 1] representing the position of the
            decoration along the parent edge terminal.
        :param str cell_id: Id of a decoration in graph.
        :rtype: float
        :return: Returns an a normalized number between [0, 1] representing
            the position of the decoration along the parent edge.
        """
        return self.call_api(result_callback, 'getDecorationPosition', cell_id)

    def set_decoration_position(self, result_callback, cell_id, position):
        """
        Gets the decoration's relative position.

        :param Callable[[Any],None] result_callback: This is called after the
            underlying method executes.
        :param str cell_id: Id of a decoration in graph.
        :param float position: A normalized number between [0, 1] representing
            the position of the decoration along the parent edge.
        """
        return self.call_api(result_callback, 'setDecorationPosition', cell_id, position)

    def set_visible(self, result_callback, cell_id, visible):
        """
        Change visibility state of cell.

        :param Callable[[Any],None] result_callback: This is called after the
            underlying method executes.
        :param str cell_id: Id of a cell in graph.
        :param bool visible: If visible or not.
        """
        return self.call_api(result_callback, 'setVisible', cell_id, visible)

    def is_visible(self, result_callback, cell_id):
        """
        Indicates the cell's visibility.

        :param Callable[[bool],None] result_callback: This callback receives a
            flag indicating the cell's visibility.
        :param str cell_id: Id of a cell in graph.
        """
        return self.call_api(result_callback, 'isVisible', cell_id)

    def set_port_visible(self, result_callback, cell_id, port_name, visible):
        """
        Change visibility state of cell's port.

        :param str cell_id: Id of a cell in graph.
        :param str port_name: Name of a port in the cell.
        :param bool visible: If visible or not.
        """
        return self.call_api(result_callback, 'setPortVisible', cell_id, port_name, visible)

    def is_port_visible(self, result_callback, cell_id, port_name):
        """
        Indicates the cell's visibility.

        :param str cell_id: Id of a cell in graph.
        :param bool port_name: Name of a port in the cell.
        """
        return self.call_api(result_callback, 'isPortVisible', cell_id, port_name)

    def set_connectable(self, result_callback, cell_id, connectable):
        """
        Change connectable state of a cell.

        :param str cell_id: Id of a cell in graph.
        :param bool connectable: If connectable or not.
        """
        return self.call_api(result_callback, 'setConnectable', cell_id, connectable)

    def is_connectable(self, result_callback, cell_id):
        """
        Indicates the cell's connectivity.

        :param str cell_id: Id of a cell in graph.
        """
        return self.call_api(result_callback, 'isConnectable', cell_id)

    def zoom_in(self, result_callback):
        """
        Zoom in the graph.
        """
        return self.call_api(result_callback, 'zoomIn')

    def zoom_out(self, result_callback):
        """
        Zoom out the graph.
        """
        return self.call_api(result_callback, 'zoomOut')

    def reset_zoom(self, result_callback):
        """
        Reset graph's zoom.
        """
        return self.call_api(result_callback, 'resetZoom')

    def fit(self, result_callback):
        """
        Rescale the graph to fit in the container.
        """
        return self.call_api(result_callback, 'fit')

    def get_zoom_scale(self, result_callback):
        """
        Return the current scale (zoom).

        :rtype: float
        """
        return self.call_api(result_callback, 'getZoomScale')

    def get_scale_and_translation(self, result_callback):
        """
        Get the current scale and translation.

        :rtype: Tuple[float, float, float]
        :return: The values represent:

            - graph scale;
            - translation along the x axis;
            - translation along the y axis;

            The three values returned by this function is suitable to be
            supplied to :func:`QmxGraphApi.set_scale_and_translation` to
            set the scale and translation to a previous value.
        """
        return self.call_api(result_callback, 'getScaleAndTranslation')

    def set_scale_and_translation(self, result_callback, scale, x, y):
        """
        Set the scale and translation.

        :param float scale: The new graph's scale (1 = 100%).
        :param float x: The new graph's translation along the X axis
            (0 = origin).
        :param float y: The new graph's scale along the Y axis (0 = origin}.
        """
        return self.call_api(result_callback, 'setScaleAndTranslation', scale, x, y)

    def set_selected_cells(self, result_callback, cell_ids):
        """
        Select the cells with the given ids.

        :param list[str] cell_ids:
        """
        return self.call_api(result_callback, 'setSelectedCells', cell_ids)

    def get_selected_cells(self, result_callback):
        """
        Get the selected cells ids.

        :rtype: list[str]
        """
        return self.call_api(result_callback, 'getSelectedCells')

    def remove_cells(self, result_callback, cell_ids):
        """
        Remove cells from graph.

        :param list cell_ids: Ids of cells that must be removed.
        """
        return self.call_api(result_callback, 'removeCells', cell_ids)

    def remove_port(self, result_callback, vertex_id, port_name):
        """
        Remove an existing port from a vertex. Any edge connected to the
        vertex through the port is also removed.

        :param str vertex_id: The id of the parent vertex.
        :param str port_name: The port's name to remove.
        """
        return self.call_api(result_callback, 'removePort', vertex_id, port_name)

    def set_double_click_handler(self, result_callback, handler):
        """
        Set the handler used for double click in cells of graph.

        Unlike other event handlers, double click is exclusive to a single
        handler. This follows underlying mxGraph implementation that works in
        this manner, with the likely intention of enforcing a single
        side-effect happening when a cell is double clicked.

        Requires that a bridge object is first added to JavaScript to work.

        :param handler: Name of signal bound to JavaScript by a bridge
            object that is going to be used as callback to event. Receives a
            str with double clicked cell id as only argument.
        """
        return self.call_api(
            result_callback, 'setDoubleClickHandler', qmxgraph.js.Variable(handler))

    def set_popup_menu_handler(self, result_callback, handler):
        """
        Set the handler used for popup menu (i.e. menu triggered by right
        click) in cells of graph.

        Unlike other event handlers, popup menu is exclusive to a single
        handler. This follows underlying mxGraph implementation that works in
        this manner, with the likely intention of enforcing a single
        side-effect happening when a cell is right-clicked.

        Requires that a bridge object is first added to JavaScript to work.

        :param handler: Name of signal bound to JavaScript by a bridge
            object that is going to be used as callback to event. Receives,
            respectively, id of cell that was right-clicked, X coordinate in
            screen coordinates and Y coordinate in screen coordinates as its
            three arguments.
        """
        return self.call_api(
            result_callback, 'setPopupMenuHandler', qmxgraph.js.Variable(handler))

    def on_label_changed(self, result_callback, handler):
        """
        Register a handler to event when label of a cell changes in graph.

        Requires that a bridge object is first added to JavaScript to work.

        :param str handler: Name of signal bound to JavaScript by a bridge
            object that is going to be used as callback to event. Receives,
            respectively, cell id, new label and old label as arguments.
        """
        return self.call_api(
            result_callback, 'onLabelChanged', qmxgraph.js.Variable(handler))

    def on_cells_added(self, result_callback, handler):
        """
        Register a handler to event when cells are added from graph.

        Requires that a bridge object is first added to JavaScript to work.

        :param str handler: Name of signal bound to JavaScript by a bridge
            object that is going to be used as callback to event. Receives a
            `QVariantList` of added cell ids as only argument.
        """
        return self.call_api(result_callback, 'onCellsAdded', qmxgraph.js.Variable(handler))

    def on_cells_removed(self, result_callback, handler):
        """
        Register a handler to event when cells are removed from graph.

        Requires that a bridge object is first added to JavaScript to work.

        :param str handler: Name of signal bound to JavaScript by a bridge
            object that is going to be used as callback to event. Receives a
            `QVariantList` of removed cell ids as only argument.
        """
        return self.call_api(result_callback, 'onCellsRemoved', qmxgraph.js.Variable(handler))

    def on_selection_changed(self, result_callback, handler):
        """
        Add function to handle selection change events in the graph.

        :param handler: Name of signal bound to JavaScript by a bridge object
            that is going to be used as callback to event. Receives an list of
            str with selected cells ids as only argument.
        """
        return self.call_api(
            result_callback, 'onSelectionChanged', qmxgraph.js.Variable(handler))

    def on_terminal_changed(self, result_callback, handler):
        """
        Add function to handle terminal change events in the graph.

        :param handler: Name of signal bound to JavaScript by a bridge object
            that is going to be used as callback to event. Receives,
            respectively, cell id, boolean indicating if the changed terminal
            is the source (or target), id of the net terminal, id of the old
            terminal.
        """
        return self.call_api(
            result_callback, 'onTerminalChanged', qmxgraph.js.Variable(handler))

    def on_terminal_with_port_changed(self, result_callback, handler):
        """
        Add function to handle terminal change with port info events in
        the graph.

        :param handler: Name of signal bound to JavaScript by a bridge
            object that is going to be used as callback to event. Receives,
            respectively, cell id, boolean indicating if the changed
            terminal is the source (or target), id of the new terminal,
            id of the old terminal.
        """
        return self.call_api(
            result_callback, 'onTerminalWithPortChanged', qmxgraph.js.Variable(handler))

    def on_view_update(self, result_callback, handler):
        """
        Add function to handle updates in the graph view.
        :param handler: Name of signal bound to JavaScript by a bridge object
            that is going to be used as callback to event. Receives,
            respectively, graph dump and graph scale and translation.
        """
        return self.call_api(
            result_callback, 'onViewUpdate', qmxgraph.js.Variable(handler))

    def on_cells_bounds_changed(self, result_callback, handler):
        """
        Add function to handle updates in the graph view.
        :param handler: Name of signal bound to JavaScript by a bridge
            object that is going to be used as callback to event. Receives
            a map of cell id to a map describing the cell bounds.

        """
        return self.call_api(result_callback, 'onBoundsChanged', qmxgraph.js.Variable(handler))

    def resize_container(self, result_callback, width, height):
        """
        Resizes the container of graph drawing widget.

        Note that new dimensions have lesser priority than keeping graph big
        enough to contain all existing vertices and edges. So if new dimensions
        are too small to contain all parts of graph it will be only resized
        down to dimensions enough to contain all parts.

        :param int width: New width.
        :param int height: New height.
        """
        return self.call_api(result_callback, 'resizeContainer', width, height)

    def get_label(self, result_callback, cell_id):
        """
        Gets the label of cell.

        :param str cell_id: Id of a cell in graph.
        :rtype: str
        :return: Label of cell.
        """
        return self.call_api(result_callback, 'getLabel', cell_id)

    def set_label(self, result_callback, cell_id, label):
        """
        Sets the label of a cell.

        :param str cell_id: Id of a cell in graph.
        :param str label: New label.
        """
        return self.call_api(result_callback, 'setLabel', cell_id, label)

    def set_style(self, result_callback, cell_id, style):
        """
        Sets a cell's style.

        :param str cell_id: Id of a cell in graph.
        :param str style: Name of a style or an inline style.
        """
        return self.call_api(result_callback, 'setStyle', cell_id, style)

    def get_style(self, result_callback, cell_id):
        """
        Gets a cell's style.

        :param str cell_id: Id of a cell in graph.
        :rtype: str
        :return: Name of a style or an inline style.
        """
        return self.call_api(result_callback, 'getStyle', cell_id)

    def set_tag(self, result_callback, cell_id, tag_name, tag_value):
        """
        Sets a tag in cell.

        :param str cell_id: Id of a cell in graph.
        :param str tag_name: Name of tag.
        :param str tag_value: Value of tag.
        """
        return self.call_api(result_callback, 'setTag', cell_id, tag_name, tag_value)

    def get_tag(self, result_callback, cell_id, tag_name):
        """
        Gets value of a value in cell.

        :param str cell_id: Id of a cell in graph.
        :param str tag_name: Name of tag.
        :rtype: str
        :return: Value of tag.
        """
        return self.call_api(result_callback, 'getTag', cell_id, tag_name)

    def has_tag(self, result_callback, cell_id, tag_name):
        """
        If cell has tag.

        :param str cell_id: Id of a cell in graph.
        :param str tag_name: Name of tag.
        :rtype: bool
        :return: True if tag exists in cell.
        """
        return self.call_api(result_callback, 'hasTag', cell_id, tag_name)

    def get_edge_terminals(self, result_callback, edge_id):
        """
        Gets the ids of endpoint vertices of an edge.

        :param str edge_id: Id of an edge in graph.
        :rtype: list[str]
        :return: A list with 2 items, first the source vertex id and second
            the target vertex id.
        """
        return self.call_api(result_callback, 'getEdgeTerminals', edge_id)

    def get_edge_terminals_with_ports(self, result_callback, edge_id):
        """
        Gets the ids of endpoint vertices of an edge and the ports used in the
        connection.

        :param str edge_id: Id of an edge in graph.
        :rtype: list[list[str|None]]
        :return: 2 lists with 2 items each:

            - - the source vertex id;
              - the port's name used on the source (can be `None`);

            - - the target vertex id;
              - the port's name used on the target (can be `None`);

        """
        return self.call_api(result_callback, 'getEdgeTerminalsWithPorts', edge_id)

    def set_edge_terminal(self, result_callback, edge_id, terminal_type, new_terminal_cell_id,
                          port_name=None):
        """
        Set an edge's terminal.

        :param str edge_id: The id of a edge in graph.
        :param str terminal_type: Indicates if the affect terminal is the
            source or target for the edge. The valid values are:
            - `QmxGraphApi.SOURCE_TERMINAL_CELL`;
            - `QmxGraphApi.TARGET_TERMINAL_CELL`;
        :param new_terminal_cell_id: The if of the new terminal for the edge.
        :param str port_name: The of the port to use in the connection.
        """
        valid_terminal_types = {
            self.SOURCE_TERMINAL_CELL,
            self.TARGET_TERMINAL_CELL,
        }
        if terminal_type not in valid_terminal_types:
            err_msg = '%s is not a valid value for `terminal_type`'
            raise ValueError(err_msg % (terminal_type,))

        return self.call_api(
            result_callback, 'setEdgeTerminal', edge_id, terminal_type, new_terminal_cell_id,
            port_name)

    def get_cell_bounds(self, result_callback, cell_id):
        """
        Set an cell's geometry. If some argument is omitted (or `None`) that
        geometry's characteristic is not affected.

        :param str cell_id: The id of a cell in graph.
        :rtype: qmxgraph.cell_bounds.CellBounds
        """
        from qmxgraph.cell_bounds import CellBounds

        def DictToCellBoundCallback(cell_bounds_as_dict):
            result_callback(CellBounds(**cell_bounds_as_dict))

        self.call_api(DictToCellBoundCallback, 'getCellBounds', cell_id)
        return result_callback

    def set_cell_bounds(self, result_callback, cell_id, cell_bounds):
        """
        Set an cell's geometry. If some argument is omitted (or `None`) that
        geometry's characteristic is not affected.

        :param str cell_id: The id of a cell in graph.
        :param qmxgraph.cell_bounds.CellBounds cell_bounds: The cell bounds to apply.
        """
        from qmxgraph.cell_bounds import asdict
        return self.call_api(result_callback, 'setCellBounds', cell_id, asdict(cell_bounds))

    def dump(self, result_callback):
        """
        Obtain a representation of the current state of the graph as an XML
        string. The state can be restored calling :func:`QmxGraphApi.restore`.

        :rtype: str
        :return: A xml string.
        """
        return self.call_api(result_callback, 'dump')

    def restore(self, result_callback, state):
        """
        Restore the graph's state to one saved with `dump`.

        :param str state: A xml string previously obtained with `dump`.
        """
        return self.call_api(result_callback, 'restore', state)

    def set_cells_deletable(self, result_callback, enabled):
        return self.call_api(result_callback, 'setCellsDeletable', enabled)

    def is_cells_deletable(self, result_callback):
        return self.call_api(result_callback, 'isCellsDeletable')

    def set_cells_disconnectable(self, result_callback, enabled):
        return self.call_api(result_callback, 'setCellsDisconnectable', enabled)

    def is_cells_disconnectable(self, result_callback):
        return self.call_api(result_callback, 'isCellsDisconnectable')

    def set_cells_editable(self, result_callback, enabled):
        return self.call_api(result_callback, 'setCellsEditable', enabled)

    def is_cells_editable(self, result_callback):
        return self.call_api(result_callback, 'isCellsEditable')

    def set_cells_movable(self, result_callback, enabled):
        return self.call_api(result_callback, 'setCellsMovable', enabled)

    def is_cells_movable(self, result_callback):
        return self.call_api(result_callback, 'isCellsMovable')

    def set_cells_connectable(self, result_callback, enabled):
        return self.call_api(result_callback, 'setCellsConnectable', enabled)

    def is_cells_connectable(self, result_callback):
        return self.call_api(result_callback, 'isCellsConnectable')

    def run_layout(self, result_callback, layout_name):
        return self.call_api(result_callback, 'runLayout', layout_name)

    def call_api(self, result_callback, fn, *args):
        """
        Call a function in underlying API provided by JavaScript graph.

        :param Callable[Any,None] result_callback: This call receives the
            result from the execution.
        :param str fn: A function call available in API.
        :param Any args: Positional arguments passed to graph's
            JavaScript API call (unfortunately can't use named arguments
            with JavaScript). All object passed must be JSON encodable or
            Variable instances.
        """
        if qmxgraph.debug.is_qmxgraph_debug_enabled():
            self.call_api_debug(result_callback, fn, *args)
        else:
            graph = self._graph()
            eval_js = graph.inner_web_view().eval_js
            call = qmxgraph.js.prepare_js_call(fn, *args)
            eval_js(result_callback, "api.{}".format(call))
        return result_callback

    def call_api_debug(self, result_callback, fn, *args):

        def check_is_loaded(is_loaded):
            if is_loaded:
                eval_js(
                    check_function_exist,
                    "(typeof api !== 'undefined') && !!api.{}".format(fn),
                )
            else:
                raise qmxgraph.js.InvalidJavaScriptError(
                    "Because graph is unloaded can't call the JavaScript API."
                )

        def check_function_exist(function_exist):
            if function_exist:
                call = qmxgraph.js.prepare_js_call(fn, *args)
                eval_js(result_callback, "api.{}".format(call))
            else:
                raise qmxgraph.js.InvalidJavaScriptError(
                    'Unable to find function "{}" in QmxGraph '
                    'JavaScript API'.format(fn)
                )

        graph = self._graph()
        eval_js = graph.inner_web_view().eval_js
        graph.is_loaded(check_is_loaded)

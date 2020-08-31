from __future__ import absolute_import

import json
import os
import weakref
from contextlib import suppress

from PyQt5.QtCore import QDataStream, QIODevice, QObject, Qt, pyqtSignal, \
    QTimer, pyqtSlot
from PyQt5.QtGui import QPainter
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWidgets import QDialog, QGridLayout, QShortcut, QSizePolicy, \
    QWidget, QStyleOption, QStyle

from qmxgraph import constants, render
from qmxgraph.api import QmxGraphApi
from qmxgraph.callback_blocker import silent_disconnect
from qmxgraph.configuration import GraphOptions, GraphStyles

from ._web_view import QWebViewWithDragDrop


# Some ugliness to successfully build the doc on ReadTheDocs...
on_rtd = os.environ.get('READTHEDOCS') == 'True'
if not on_rtd:
    from qmxgraph import resource_mxgraph, resource_qmxgraph  # noqa


class QmxGraph(QWidget):
    """
    A graph widget that is actually an web view using as backend mxGraph_,
    a very feature rich JS graph library which is also used as backend to
    the powerful Google Drive's draw.io widget.

    **Tags**

    Tags don't have any impact or influence on QmxGraph features. It is just a
    feature so client code can associate custom data with cells created in a
    graph.

    Tags can be helpful, for instance, to be able to infer an
    application-specific type of a dragged & dropped new cell. When added cell
    events are handled, client code can just query tags to know this
    information. Without tags, it would need to infer based on unreliable
    heuristics like current style or label.

    An important observation is that tag values are *always* strings. If a
    value of other type is used it will raise an error.

    **Debug/Inspection**

    It is possible to open a web inspector for underlying graph drawing page by
    typing `F12` with widget focused.

    .. _mxGraph: https://jgraph.github.io/mxgraph/
    """

    # Signal fired when underlying web view finishes loading. Argument
    # indicates if loaded successfully.
    loadFinished = pyqtSignal(bool)

    def __init__(
        self,
        options=None,
        styles=None,
        stencils=tuple(),
        auto_load=True,
        parent=None,
    ):
        """
        :param qmxgraph.configuration.GraphOptions|None options: Features
            enabled in graph drawing widget. If none given, uses defaults.
        :param qmxgraph.configuration.GraphStyles|None styles: Additional
            styles made available for graph drawing widget besides mxGraph's
            default ones. If none given only mxGraph defaults are available.
        :param iterable[str] stencils: A sequence of XMLs available in Qt
            resource collections. Each XML must respect format defined by
            mxGraph (see
            https://jgraph.github.io/mxgraph/docs/js-api/files/shape/mxStencil-js.html#mxStencil
            and
            https://jgraph.github.io/mxgraph/javascript/examples/stencils.xml
            for reference).
        :param bool auto_load: If should load page as soon as widget is
            initialized.
        :param QWidget|None parent: Parent widget.
        """
        QWidget.__init__(self, parent)

        self._own_path = ':/qmxgraph'
        self._mxgraph_path = ':/mxgraph'

        if options is None:
            options = GraphOptions()
        self._options = options

        if styles is None:
            styles = GraphStyles(styles={})
        self._styles = styles

        self._stencils = stencils

        # Web view fills whole widget area
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)  # no margin to web view

        self._web_view = QWebViewWithDragDrop()
        self._web_view.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._error_bridge = JsPythonErrorHandlingBridge()
        self._events_bridge = JsPythonEventsBridge()
        self._is_events_bridge_pending_connection = True
        self._double_click_bridge = _JsPythonDoubleClickBridge()
        self._popup_menu_bridge = _JsPythonPopupMenuBridge()
        self._channel = QWebChannel()
        self._channel.registerObject('bridge_error_handler', self._error_bridge)
        self._channel.registerObject('bridge_events_handler', self._events_bridge)
        self._channel.registerObject('bridge_double_click_handler', self._double_click_bridge)
        self._channel.registerObject('bridge_popup_menu_handler', self._popup_menu_bridge)
        self._web_view.page().setWebChannel(self._channel)

        # Starts disabled, only enable once finished loading page (as user
        # interaction before that would be unsafe)
        # TODO: widget remain with disabled appearance even after enabled
        # self.setEnabled(False)

        self._layout.addWidget(self._web_view, 0, 0, 1, 1)

        # Similar to a browser, QmxGraph widget is going to allow inspection by
        # typing F12
        self._inspector_dialog = None
        inspector_shortcut = QShortcut(self)
        inspector_shortcut.setKey("F12")
        inspector_shortcut.activated.connect(self.toggle_inspector)

        self._execute_on_load_finished()

        self._api = QmxGraphApi(graph=self)

        self._web_view.on_drag_enter_event.connect(self._on_drag_enter)
        self._web_view.on_drag_move_event.connect(self._on_drag_move)
        self._web_view.on_drop_event.connect(self._on_drop)

        if auto_load:
            self._load_graph_page()

    def paintEvent(self, paint_event):
        """
        A simple override to the `QWidget.paintEvent` required soo the QSS
        rules have effect over `QWidget` subclasses.

        From: http://doc.qt.io/qt-5/stylesheet-reference.html#qwidget-widget

        :type paint_event: PyQt5.QtGui.QPaintEvent
        """
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

    def load(self):
        """
        Load graph drawing page, if not yet loaded.
        """
        if not self.is_loaded() or not self._web_view.is_loading():
            self._load_graph_page()

    def is_loaded(self):
        """
        :rtype: bool
        :return: Is graph page already loaded?
        """
        # If failed in initialization of graph and it isn't running do not
        # considered it loaded, as graph and its API aren't safe for use
        return self._web_view.is_loaded() and \
            self._web_view.eval_js('(typeof graphs !== "undefined") && graphs.isRunning()')

    def blank(self):
        """
        Blanks the graph drawing page, effectively clearing/unloading currently
        displayed graph.
        """
        if self._inspector_dialog:
            self._inspector_dialog.close()
            self._inspector_dialog = None

        self._web_view.blank()

    def set_error_bridge(self, bridge):
        """
        Redirects errors on JavaScript code from graph drawing widget to
        bridge.

        :param ErrorHandlingBridge bridge: Handler for errors.
        """
        silent_disconnect(self._error_bridge.on_error, bridge.on_error)
        self._error_bridge.on_error.connect(bridge.on_error)

    def set_events_bridge(self, bridge):
        """
        Redirects events fired by graph on JavaScript code to Python/Qt side
        by using a bridge.

        :param EventsBridge bridge: Bridge with event handlers.
        """
        signal_name_list = [
            k for k, v in EventsBridge.__dict__.items()
            if isinstance(v, pyqtSignal)
        ]
        for signal_name in signal_name_list:
            own_signal = getattr(self._events_bridge, signal_name)
            outside_signal = getattr(bridge, signal_name)
            silent_disconnect(own_signal, outside_signal)
            own_signal.connect(outside_signal)

    def _connect_events_bridge(self):
        if self.is_loaded():
            self.api.on_cells_added('bridge_events_handler.cells_added_slot')
            self.api.on_cells_removed('bridge_events_handler.cells_removed_slot')
            self.api.on_label_changed('bridge_events_handler.label_changed_slot')
            self.api.on_selection_changed(
                'bridge_events_handler.selection_changed_slot')
            self.api.on_terminal_changed(
                'bridge_events_handler.terminal_changed_slot')
            self.api.on_terminal_with_port_changed(
                'bridge_events_handler.terminal_with_port_changed_slot')
            self.api.on_view_update('bridge_events_handler.view_update_slot')
            self.api.on_cells_bounds_changed(
                'bridge_events_handler.cells_bounds_changed_slot')

    def set_double_click_handler(self, handler):
        """
        Set the handler used for double click in cells of graph.

        Unlike other event handlers, double click is exclusive to a single
        handler. This follows underlying mxGraph implementation that works in
        this manner, with the likely intention of enforcing a single
        side-effect happening when a cell is double clicked.

        :param callable|None handler: Handler that receives double clicked
            cell id as only argument. If None it disconnects double click
            handler from graph.
        """
        with suppress(TypeError):
            self._double_click_bridge.on_double_click.disconnect()
        if handler:
            self._double_click_bridge.on_double_click.connect(handler)

    def _connect_double_click_handler(self):
        if self.is_loaded():
            self.api.set_double_click_handler(
                'bridge_double_click_handler.double_click_slot')

    def set_popup_menu_handler(self, handler):
        """
        Set the handler used for popup menu (i.e. right-click) in cells of
        graph.

        Unlike other event handlers, popup menu is exclusive to a single
        handler. This follows underlying mxGraph implementation that works in
        this manner, with the likely intention of enforcing a single
        side-effect happening when a cell is right-clicked.

        :param callable|None handler: Handler that receives, respectively, id
            of cell that was right-clicked, X coordinate in screen coordinates
            and Y coordinate in screen coordinates as its three arguments. If
            None it disconnects handler from graph.
        """
        with suppress(TypeError):
            self._popup_menu_bridge.on_popup_menu.disconnect()
        if handler:
            self._popup_menu_bridge.on_popup_menu.connect(handler)

    def _connect_popup_menu_handler(self):
        if self.is_loaded():
            self.api.set_popup_menu_handler(
                'bridge_popup_menu_handler.popup_menu_slot')

    @property
    def api(self):
        """
        :rtype: qmxgraph.api.QmxGraphApi
        :return: Proxy to API to manipulate graph.
        """
        return self._api

    # Web inspector -----------------------------------------------------------

    def show_inspector(self):
        """
        Show web inspector bound to QmxGraph page.
        """
        if not self._inspector_dialog:
            dialog = self._inspector_dialog = QDialog(self)
            dialog.setWindowTitle("Web Inspector")
            dialog.setWindowFlags(
                dialog.windowFlags() | Qt.WindowMaximizeButtonHint)
            dialog.resize(800, 600)
            layout = QGridLayout(dialog)
            layout.setContentsMargins(0, 0, 0, 0)  # no margin to web view

            from PyQt5.QtWebEngineWidgets import QWebEngineView
            inspector = QWebEngineView(dialog)
            inspector.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Expanding)
            self._web_view.page().setDevToolsPage(inspector.page())
            inspector.setVisible(True)
            layout.addWidget(inspector)

        self._inspector_dialog.show()

    def hide_inspector(self):
        """
        Hide web inspector bound to QmxGraph page.
        """
        if not self._inspector_dialog:
            return
        self._inspector_dialog.hide()

    def toggle_inspector(self):
        """
        Toggle visibility state of web inspector bound to QmxGraph page.
        """
        if self._inspector_dialog and self._inspector_dialog.isVisible():
            self.hide_inspector()
        else:
            self.show_inspector()

    # Accessors recommended for debugging/testing only ------------------------

    def inner_web_view(self):
        """
        :rtype: QWebViewWithDragDrop
        :return: Web view widget showing graph drawing page.
        """
        return self._web_view

    # Overridden events -------------------------------------------------------

    def resizeEvent(self, event):
        if self.is_loaded():
            # Whenever graph widget is resized, it is going to resize
            # underlying graph in JS to fit widget as well as possible.
            width = event.size().width()
            height = event.size().height()
            self.api.resize_container(width, height)

        event.ignore()

    # Protected plumbing methods ----------------------------------------------

    def _load_graph_page(self):
        """
        Loads the graph drawing page in Qt's web view widget.
        """
        mxgraph_path = self._mxgraph_path
        own_path = self._own_path

        html = render.render_embedded_html(
            options=self._options,
            styles=self._styles,
            stencils=self._stencils,
            mxgraph_path=mxgraph_path,
            own_path=own_path,
        )

        from PyQt5.QtCore import QUrl
        self._web_view.setHtml(html, baseUrl=QUrl('qrc:/'))

    def _execute_on_load_finished(self):
        """
        Several actions must be delayed until page finishes loading to take
        effect.
        """
        self_ref = weakref.ref(self)

        def post_load(ok):
            self_ = self_ref()
            if not self_:
                return
            ok = bool(ok and self_.is_loaded())
            if ok:
                # TODO: widget remain w/ disabled appearance even after enabled
                # Allow user to interact with page again
                # self_._web_view.setEnabled(True)

                self_._connect_events_bridge()
                self_._connect_double_click_handler()
                self_._connect_popup_menu_handler()

                width = self_.width()
                height = self_.height()
                self_.api.resize_container(width, height)

            self_.loadFinished.emit(ok)

        self._web_view.loadFinished.connect(post_load)

    def _on_drag_enter(self, event):
        """
        :type event: QDragEnterEvent
        """
        self._approve_only_dd_mime_type(event)

    def _on_drag_move(self, event):
        """
        :type event: QDragMoveEvent
        """
        self._approve_only_dd_mime_type(event)

    def _approve_only_dd_mime_type(self, event):
        """
        Only approve events that contain QmxGraph's drag&drop MIME type.

        :type event: QDragEnterEvent|QDragMoveEvent
        """
        data = event.mimeData().data(constants.QGRAPH_DD_MIME_TYPE)
        if not data.isNull():
            event.acceptProposedAction()
        else:
            event.ignore()

    def _on_drop(self, event):
        """
        Adds to graph contents read from MIME data from drop event.

        Note that new vertices are added centered at current mouse position.

        :type event: QDropEvent
        """
        data = event.mimeData().data(constants.QGRAPH_DD_MIME_TYPE)
        if not data.isNull():
            data_stream = QDataStream(data, QIODevice.ReadOnly)
            parsed = json.loads(data_stream.readString().decode('utf8'))

            # Refer to `mime.py` for docs about format
            version = parsed['version']
            if version not in (1, 2):
                raise ValueError(
                    "Unsupported version of QmxGraph MIME data: {}".format(
                        version))

            x = event.pos().x()
            y = event.pos().y()

            if version in (1, 2):
                vertices = parsed.get('vertices', [])
                scale = self.api.get_zoom_scale()
                for v in vertices:
                    # place vertices with an offset so their center falls
                    # in the event point.
                    vertex_x = x + (v['dx'] - v['width'] * 0.5) * scale
                    vertex_y = y + (v['dy'] - v['height'] * 0.5) * scale
                    self.api.insert_vertex(
                        x=vertex_x,
                        y=vertex_y,
                        width=v['width'],
                        height=v['height'],
                        label=v['label'],
                        style=v.get('style', None),
                        tags=v.get('tags', {}),
                    )

            if version in (2,):
                decorations = parsed.get('decorations', [])
                for v in decorations:
                    self.api.insert_decoration(
                        x=x,
                        y=y,
                        width=v['width'],
                        height=v['height'],
                        label=v['label'],
                        style=v.get('style', None),
                        tags=v.get('tags', {}),
                    )

            event.acceptProposedAction()
        else:
            event.ignore()


def _make_async_pyqt_slot(slot_name, signal_name, parameters):

    def async_slot(self, *args):
        signal = getattr(self, signal_name)
        convert_args = getattr(
            self, f'js_to_py_args_{signal_name}', lambda x: x,
        )
        args = convert_args(args)
        QTimer.singleShot(1, lambda: signal.emit(*args))

    return pyqtSlot(*parameters, name=slot_name)(async_slot)


def _create_async_slots(namespace, signal_holder_class):
    import re

    for k, v in signal_holder_class.__dict__.items():
        if isinstance(v, pyqtSignal):
            (signature,) = v.signatures
            m = re.match(r'^([^(]+)\(([^)]*)\)$', signature)
            assert m is not None

            signal_name = m.group(1)
            assert signal_name.startswith('on_')
            slot_name = signal_name[3:] + '_slot'
            if slot_name not in namespace:
                parameters = m.group(2)
                parameters = parameters.split(',') if parameters else []
                namespace[slot_name] = _make_async_pyqt_slot(slot_name, signal_name, parameters)
                namespace[slot_name] = _make_async_pyqt_slot(slot_name, signal_name, parameters)


class ErrorHandlingBridge(QObject):
    """
    Error handler on JavaScript side will use `on_error` signal to communicate
    to Python any error that may'be happened.

    Client code must connect to signal and handle messages in whatever manner
    desired.
    """

    # JavaScript client code emits this signal whenever an error happens
    #
    # Arguments:
    # msg: str
    # url: str
    # line: int
    # column: int
    on_error = pyqtSignal(str, str, int, int, name='on_error')


class JsPythonErrorHandlingBridge(ErrorHandlingBridge):
    """
    Javascript interface object for ErrorHandlingBridge.
    """
    _create_async_slots(locals(), ErrorHandlingBridge)


class EventsBridge(QObject):
    """
    A bridge object between Python/Qt and JavaScript that provides a series
    of signals that are connected to events fired on JavaScript.

    :ivar pyqtSignal on_cells_removed: JavaScript client code emits this
        signal when cells are removed from graph. Arguments:

        - cell_ids: QVariantList

    :ivar pyqtSignal on_cells_added: JavaScript client code emits this
        signal when cells are added to graph. Arguments:

        - cell_ids: QVariantList

    :ivar pyqtSignal on_label_changed: JavaScript client code emits this
        signal when cell is renamed. Arguments:

        - cell_id: str
        - new_label: str
        - old_label: str

    :ivar pyqtSignal on_selection_changed: JavaScript client code emits
        this signal when the current selection change. Arguments:

        - cell_ids: QVariantList

    :ivar pyqtSignal on_terminal_changed: JavaScript client code emits
        this signal when a cell terminal change. Arguments:

        - cell_id: str
        - terminal_type: str
        - new_terminal_id: str
        - old_terminal_id: str

    :ivar pyqtSignal on_terminal_with_port_changed: JavaScript client code emits
        this signal when a cell terminal change with port information. Arguments:

        - cell_id: str
        - terminal_type: str
        - new_terminal_id: str
        - new_terminal_port_id: str
        - old_terminal_id: str
        - old_terminal_port_id: str

    :ivar pyqtSignal on_view_update: JavaScript client code emits this
        signal when the view is updated. Arguments:

        - graph_view: str
        - scale_and_translation: QVariantList

    :ivar pyqtSignal on_cells_bounds_changed: JavaScript client code emits
        this signal when some cells' bounds changes.The arguments `dict`
        maps the affected `cell_id`s
        to :class:`qmxgraph.cell_bounds.CellBounds` instances:

        - changed_bounds: dict


    Using this object connecting to events from JavaScript basically becomes a
    matter of using Qt signals.

    .. code-block::

        def on_cells_added_handler(cell_ids):
            print(f'added {cell_ids}')

        def on_terminal_changed_handler(
            cell_id, terminal_type, new_terminal_id, old_terminal_id):
            print(
                f'{terminal_type} of {cell_id} changed from'
                f' {old_terminal_id} to {new_terminal_id}'
            )

        def on_cells_removed_handler(cell_ids):
            print(f'removed {cell_ids}')

        events_bridge = EventsBridge()
        widget = ...
        widget.set_events_bridge(events_bridge)

        events_bridge.on_cells_added.connect(on_cells_added_handler)
        events_bridge.on_cells_removed.connect(on_cells_removed_handler)
        events_bridge.on_terminal_changed.connect(on_terminal_changed_handler)

    """

    on_cells_removed = pyqtSignal('QVariantList', name='on_cells_removed')
    on_cells_added = pyqtSignal('QVariantList', name='on_cells_added')
    on_label_changed = pyqtSignal(str, str, str, name='on_label_changed')
    on_selection_changed = pyqtSignal(
        'QVariantList', name='on_selection_changed')
    on_terminal_changed = pyqtSignal(
        str, str, str, str, name='on_terminal_changed')
    on_terminal_with_port_changed = pyqtSignal(
        str, str, str, str, str, str, name='on_terminal_with_port_changed')
    on_view_update = pyqtSignal(str, 'QVariantList', name='on_view_update')
    on_cells_bounds_changed = pyqtSignal('QVariant', name='on_cells_bounds_changed')


class JsPythonEventsBridge(EventsBridge):
    """
    Javascript interface object for EventsBridge.
    """
    _create_async_slots(locals(), EventsBridge)

    @staticmethod
    def js_to_py_args_on_cells_bounds_changed(js_args):
        """
        Convert the javascript arguments to respective python objects.
        """
        from qmxgraph.cell_bounds import CellBounds
        (bounds_changed,) = js_args
        bounds_changed = {
            k: CellBounds(**v) for k, v in bounds_changed.items()
        }
        return bounds_changed,


class _DoubleClickBridge(QObject):
    """
    A private bridge used for double click events in JavaScript graph.

    It is private so `QmxGraph` can make sure only a single double click
    handler is registered, to make sure it doesn't violate what is stated in
    `set_double_click_handler` docs of `api` module.
    """

    # Arguments:
    # cell_id: str
    on_double_click = pyqtSignal(str, name='on_double_click')


class _JsPythonDoubleClickBridge(_DoubleClickBridge):
    """
    Javascript interface object for _DoubleClickBridge.
    """
    _create_async_slots(locals(), _DoubleClickBridge)


class _PopupMenuBridge(QObject):
    """
    A private bridge used for popup menu events in JavaScript graph.

    It is private so `QmxGraph` can make sure only a single popup menu handler
    is registered, to make sure it doesn't violate what is stated in
    `set_popup_menu_handler` docs of `api` module.
    """

    # Arguments:
    # cell_id: str
    # x: int
    # y: int
    on_popup_menu = pyqtSignal(str, int, int, name='on_popup_menu')


class _JsPythonPopupMenuBridge(_PopupMenuBridge):
    """
    Javascript interface object for _PopupMenuBridge.
    """
    _create_async_slots(locals(), _PopupMenuBridge)

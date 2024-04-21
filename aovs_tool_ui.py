import sys
from importlib import reload

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

from aovs_tool import aovs_tool_core as aovs_core
reload(aovs_core)


class AovsToolUI(QMainWindow):
    __title__ = 'aovspliter'

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.setWindowTitle(self.__title__)
        self._setup_ui()
        self.aovs_nuke = aovs_core.AovsToolNuke()
        self.layers_count = 0

    def _setup_ui(self):
        self.setCentralWidget(QWidget())
        main_layout = QVBoxLayout()
        self.centralWidget().setLayout(main_layout)
        self.central_splitter = QSplitter()
        self.central_splitter.setOrientation(Qt.Horizontal)
        self.central_splitter.setHandleWidth(8)
        main_layout.addWidget(self.central_splitter)
        self._setup_panel_layer()
        self._setup_panel_options()
        main_layout.addWidget(self.btn_extract)

    def _setup_panel_layer(self):
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText('Search eg : light* ')
        self.input_search.textChanged.connect(self.on_textChanged)

        self.view_layers = QListWidget()
        self.view_layers.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.view_layers.itemSelectionChanged.connect(self.on_selection_changes)

        self.lb_node_name = QLabel()

        self.lb_selection_count = QLabel()
        # self.lb_selection_count.setStyleSheet("font:italic")
        self.lb_selection_count.setEnabled(False)
        self.lb_selection_count.setAlignment(Qt.AlignRight)

        self.lb_layers_count = QLabel()
        # self.lb_layers_count.setStyleSheet("font:italic")
        self.lb_layers_count.setAlignment(Qt.AlignRight)
        self.lb_layers_count.setEnabled(False)

        self.btn_extract = QPushButton()
        self.btn_extract.setText('Extract Aovs')
        self.btn_extract.clicked.connect(self.action_extract)

        self.btn_refresh_node = QPushButton()
        self.btn_refresh_node.setText("Refresh")
        self.btn_refresh_node.clicked.connect(self.on_refresh_layer_list)

        h_layout_1 = QHBoxLayout()
        h_layout_1.setMargin(0)
        h_layout_1.addWidget(self.lb_node_name)
        h_layout_1.addStretch()
        h_layout_1.addWidget(self.btn_refresh_node)

        h_layout_2 = QHBoxLayout()
        h_layout_2.setMargin(0)
        h_layout_2.addStretch()
        h_layout_2.addWidget(self.lb_selection_count)
        h_layout_2.addWidget(self.lb_layers_count)

        frame_main = QFrame()
        lay_main = QVBoxLayout(frame_main)
        lay_main.setContentsMargins(0, 0, 4, 0)
        lay_main.addLayout(h_layout_1)
        lay_main.addWidget(self.input_search)
        lay_main.addWidget(self.view_layers)
        lay_main.addLayout(h_layout_2)
        # lay_main.addWidget(self.btn_extract)

        self.central_splitter.addWidget(frame_main)

    def _setup_panel_options(self):
        self.input_merge_aovs = QCheckBox()
        self.input_merge_aovs.setText('Merge aovs (add)')
        self.input_merge_aovs.setChecked(True)

        grp_premults = QGroupBox(title='Unpremult/ Premult')
        h_layout_1 = QHBoxLayout(grp_premults)
        h_layout_1.setMargin(2)
        self.choice_premult_none = QRadioButton('None')
        self.choice_premult_each = QRadioButton('Each aovs')
        self.choice_premult_all = QRadioButton('All aovs')
        h_layout_1.addWidget(self.choice_premult_none)
        h_layout_1.addWidget(self.choice_premult_each)
        h_layout_1.addWidget(self.choice_premult_all)

        grp_orient = QGroupBox(title='Merges direction')
        h_layout_2 = QHBoxLayout(grp_orient)
        h_layout_2.setMargin(2)
        self.choice_orient_right = QRadioButton('right')
        self.choice_premult_left = QRadioButton('left')

        h_layout_2.addWidget(self.choice_orient_right)
        h_layout_2.addWidget(self.choice_premult_left)

        frame_main = QFrame()
        lay_main = QVBoxLayout(frame_main)
        lay_main.setContentsMargins(4, 0, 0, 0)
        lay_main.addStretch()
        lay_main.addWidget(grp_premults)
        lay_main.addWidget(self.input_merge_aovs)
        lay_main.addWidget(grp_orient)
        self.central_splitter.addWidget(frame_main)

    def update_layer_list(self, layers: list):
        self.view_layers.clear()
        for layer in layers:
            _item = QListWidgetItem()
            _item.setText(layer)
            self.view_layers.addItem(_item)
        self.layers_count = len(layers)
        self.update_labels_layer()

    def update_labels_layer(self, hidden_count: int = None, selection_count: int = None):
        if selection_count:
            self.lb_selection_count.setText(f'selected items : {selection_count}')

        lr_count_txt = f'($count / {self.layers_count})'
        if hidden_count is not None:
            lr_count_txt = lr_count_txt.replace('$count', str(hidden_count))
        else:
            lr_count_txt = lr_count_txt.replace('$count', str(self.layers_count))

        self.lb_layers_count.setText(lr_count_txt)

    def get_selected_layers(self):
        items = self.view_layers.selectedItems()
        return [item.text() for item in items]

    def on_textChanged(self, _pattern: str):
        hidden_count = self.layers_count
        for row in range(self.view_layers.count()):
            item = self.view_layers.item(row)
            keyword = item.text()
            if _pattern:
                if aovs_core.is_match(_pattern, keyword):
                    item.setHidden(False)
                else:
                    item.setHidden(True)
                    hidden_count += - 1
            else:
                item.setHidden(False)

        self.update_labels_layer(hidden_count=hidden_count)

    def on_selection_changes(self):
        self.update_labels_layer(selection_count=len(self.view_layers.selectedItems()))

    def on_refresh_layer_list(self):
        if not aovs_core.INSIDE_NUKE:
            datas = read_layers()
            self.lb_node_name.setText(self.aovs_nuke.get_selected_node().name())
            self.update_layer_list(datas)
            return

        # Inside Nuke
        self.aovs_nuke.get_selected_node()
        if not self.aovs_nuke.selected_node:
            self.lb_node_name.setText('Nothing selected!')
            self.update_layer_list([])
            return
        datas = self.aovs_nuke.get_layers()
        self.lb_node_name.setText(self.aovs_nuke.selected_node.name())
        self.update_layer_list(datas)

    def action_extract(self):
        layers = self.get_selected_layers()
        self.aovs_nuke.build_aovs_shuffles(layers)
        pass


def nuke_launcher():
    app = QApplication.instance()
    for widget in app.topLevelWidgets():
        if widget.metaObject().className() == 'Foundry::UI::DockMainWindow':
            parent = widget
            break
    main_window = AovsToolUI(parent=parent)
    main_window.show()
    main_window.on_refresh_layer_list()


def read_layers():
    import json
    with open(r'\\yandre_nas\home\WORK\DEV\NUKE\aovs_tool\layers.json') as _f:
        _d = json.load(_f)
    return _d


def _generate_layers():
    aovs = ['Beauty', 'combineddiffuse', 'directdiffuse', 'indirectdiffuse', 'combinedglossyreflection', 'directglossyreflection', 'indirectglossyreflection', 'glossytransmission', 'combinedemission', 'directemission', 'indirectemission', 'sss', 'export_basecolor']
    supl = ['P', 'N', 'depth', 'UV']

    lights = ['HDR', 'spotLightA', 'spotLightB', 'default']
    layers = []
    for a in aovs:
        for l in lights:
            _aov = a + '_' + l
            layers.append(_aov)

    layers.extend(supl)
    with open('./aovs_spliter/layers.json', 'w') as _f:
        json.dump(layers, _f, indent=4)


if __name__ == "__main__":

    # _generate_layers()
    app = QApplication(sys.argv)
    wind = AovsToolUI()
    wind.show()
    wind.update_layer_list(read_layers())
    app.exec_()

from PyQt6.QtWidgets import (
    QDialog, QLineEdit, QVBoxLayout, QLabel, QHBoxLayout, QPushButton,
    QScrollArea, QWidget, QToolButton, QMessageBox, QFrame, QColorDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class PresetEditorDialog(QDialog):
    Deleted = 2

    def __init__(self, presets_manager, preset_name: str | None = None, parent=None):
        super().__init__(parent)
        self.presets_manager = presets_manager
        self.editing_name = preset_name

        title = f"Edytuj preset — {preset_name}" if preset_name else "Nowy preset"
        self.setWindowTitle(title)
        self.setMinimumWidth(900)
        self.setMinimumHeight(500)
        self._setup_ui()

        if preset_name:
            self._load_preset(preset_name)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Nazwa presetu:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Podaj nazwę presetu...")
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        split_layout = QHBoxLayout()
        split_layout.setSpacing(16)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        row_layout = QHBoxLayout()
        row_layout.addWidget(QLabel("Wiersze tabeli:"))
        add_row_btn = QPushButton("+ Dodaj wiersz")
        add_row_btn.setFlat(True)
        add_row_btn.clicked.connect(lambda: self._add_row_input(""))
        row_layout.addWidget(add_row_btn)
        left_layout.addLayout(row_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)

        self.rows_container = QWidget()
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setSpacing(6)
        self.rows_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.rows_container)
        left_layout.addWidget(self.scroll_area)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)

        style_layout = QHBoxLayout()
        style_layout.addWidget(QLabel("Style:"))
        add_style_btn = QPushButton("+ Dodaj styl")
        add_style_btn.setFlat(True)
        add_style_btn.clicked.connect(lambda: self._add_style_input("", None, None))
        style_layout.addWidget(add_style_btn)
        right_layout.addLayout(style_layout)

        self.style_scroll_area = QScrollArea()
        self.style_scroll_area.setWidgetResizable(True)
        self.style_scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)

        self.styles_container = QWidget()
        self.styles_layout = QVBoxLayout(self.styles_container)
        self.styles_layout.setSpacing(6)
        self.styles_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.style_scroll_area.setWidget(self.styles_container)
        right_layout.addWidget(self.style_scroll_area)

        split_layout.addWidget(left_widget, 1)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.VLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        split_layout.addWidget(divider)

        split_layout.addWidget(right_widget, 1)
        layout.addLayout(split_layout)

        btn_layout = QHBoxLayout()

        if self.editing_name:
            delete_btn = QPushButton("Usuń preset")
            delete_btn.setToolTip(f"Trwale usuń preset '{self.editing_name}'")
            delete_btn.clicked.connect(self._delete_preset)
            btn_layout.addWidget(delete_btn)

        btn_layout.addStretch()

        cancel_btn = QPushButton("Anuluj")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Zapisz")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _add_row_input(self, text: str):
        row_widget = QWidget()
        row_h = QHBoxLayout(row_widget)
        row_h.setContentsMargins(0, 0, 0, 0)
        row_h.setSpacing(4)

        remove_btn = QToolButton()
        remove_btn.setText("✕")
        remove_btn.setFixedSize(26, 26)
        remove_btn.setToolTip("Usuń wiersz")
        row_h.addWidget(remove_btn)

        line = QLineEdit(text)
        line.setPlaceholderText("Nazwa wiersza...")
        row_h.addWidget(line)
        row_widget.line_edit = line

        move_up_btn = QPushButton("↑")
        move_up_btn.setMaximumWidth(26)
        move_up_btn.setToolTip("Przesuń wiersz do góry")
        row_h.addWidget(move_up_btn)

        move_down_btn = QPushButton("↓")
        move_down_btn.setMaximumWidth(26)
        move_down_btn.setToolTip("Przesuń wiersz w dół")
        row_h.addWidget(move_down_btn)

        remove_btn.clicked.connect(lambda: self._remove_row(row_widget))
        move_up_btn.clicked.connect(lambda: self._move_row_up(row_widget))
        move_down_btn.clicked.connect(lambda: self._move_row_down(row_widget))

        self.rows_layout.addWidget(row_widget)
        line.setFocus()

    def _remove_row(self, row_widget: QWidget):
        self.rows_layout.removeWidget(row_widget)
        row_widget.deleteLater()

    def _move_row_up(self, row_widget: QWidget):
        self._move_row(row_widget, -1)

    def _move_row_down(self, row_widget: QWidget):
        self._move_row(row_widget, 1)

    def _move_row(self, row_widget: QWidget, offset: int):
        index = self.rows_layout.indexOf(row_widget)
        new_index = index + offset
        if 0 <= new_index < self.rows_layout.count():
            self.rows_layout.removeWidget(row_widget)
            self.rows_layout.insertWidget(new_index, row_widget)

    def _add_style_input(self, key: str, text_color: list | None, bg_color: list | None):
        row_widget = QWidget()
        row_h = QHBoxLayout(row_widget)
        row_h.setContentsMargins(0, 0, 0, 0)
        row_h.setSpacing(4)

        remove_btn = QToolButton()
        remove_btn.setText("✕")
        remove_btn.setFixedSize(26, 26)
        remove_btn.setToolTip("Usuń styl")
        row_h.addWidget(remove_btn)

        key_input = QLineEdit(key)
        key_input.setPlaceholderText("Wartość (np. Proste)...")
        row_h.addWidget(key_input)
        row_widget.key_edit = key_input

        fg_btn = QPushButton("A")
        fg_btn.setFixedSize(26, 26)
        fg_btn.setToolTip("Kolor tekstu")
        row_widget.fg_color = text_color
        self._update_color_btn(fg_btn, text_color, is_text=True)
        fg_btn.clicked.connect(lambda: self._pick_color(row_widget, fg_btn, is_text=True))
        row_h.addWidget(fg_btn)

        bg_btn = QPushButton()
        bg_btn.setFixedSize(26, 26)
        bg_btn.setToolTip("Kolor tła")
        row_widget.bg_color = bg_color
        self._update_color_btn(bg_btn, bg_color, is_text=False)
        bg_btn.clicked.connect(lambda: self._pick_color(row_widget, bg_btn, is_text=False))
        row_h.addWidget(bg_btn)

        self.styles_layout.addWidget(row_widget)
        remove_btn.clicked.connect(lambda: self._remove_style(row_widget))
        key_input.setFocus()

    def _remove_style(self, row_widget: QWidget):
        self.styles_layout.removeWidget(row_widget)
        row_widget.deleteLater()

    def _update_color_btn(self, btn: QPushButton, color: list | None, is_text: bool):
        if color:
            r, g, b = color
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            if is_text:
                btn.setStyleSheet(f"color: {hex_color}; border: 1px solid #888;")
                btn.setText("A")
            else:
                btn.setStyleSheet(f"background-color: {hex_color}; border: 1px solid #888;")
                btn.setText("")
        else:
            if is_text:
                btn.setStyleSheet("border: 1px solid #888;")
                btn.setText("A")
            else:
                btn.setStyleSheet("background-color: #FFF; border: 1px solid #888;")
                btn.setText("")

    def _pick_color(self, row_widget: QWidget, btn: QPushButton, is_text: bool):
        current = row_widget.fg_color if is_text else row_widget.bg_color
        initial = QColor(*current) if current else QColor(Qt.GlobalColor.white)
        color = QColorDialog.getColor(initial, self, "Wybierz kolor")
        if color.isValid():
            rgb = [color.red(), color.green(), color.blue()]
            if is_text:
                row_widget.fg_color = rgb
            else:
                row_widget.bg_color = rgb
            self._update_color_btn(btn, rgb, is_text)

    def _delete_preset(self):
        reply = QMessageBox.warning(
            self,
            "Usuń preset",
            f"Czy na pewno chcesz trwale usunąć preset '{self.editing_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.presets_manager.delete_preset(self.editing_name)
            self.done(PresetEditorDialog.Deleted)

    def _load_preset(self, name: str):
        self.name_input.setText(name)
        rows = self.presets_manager.get_preset_rows(name)
        for row in rows:
            self._add_row_input(row)

        preset = self.presets_manager.presets.get(name)
        if preset and preset.styles:
            for value, style in preset.styles.items():
                self._add_style_input(value, style.text_color, style.background_color)

    def _save(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Błąd", "Podaj nazwę presetu.")
            return

        rows = []
        for i in range(self.rows_layout.count()):
            line_edit = self.rows_layout.itemAt(i).widget().line_edit
            text = line_edit.text().strip()
            if text:
                rows.append(text)

        if not rows:
            QMessageBox.warning(self, "Błąd", "Preset musi zawierać co najmniej jeden wiersz.")
            return
        if len(rows) != len(set(rows)):
            QMessageBox.warning(self, "Błąd", "Nazwy kolumn w presecie nie mogą się powtarzać.")
            return

        from models import RowStyle
        styles: dict[str, RowStyle] = {}
        seen_keys = []
        for i in range(self.styles_layout.count()):
            row_widget = self.styles_layout.itemAt(i).widget()
            key = row_widget.key_edit.text().strip()
            if not key:
                continue
            if key in seen_keys:
                QMessageBox.warning(self, "Błąd", f"Wartość stylu '{key}' występuje więcej niż raz.")
                return
            seen_keys.append(key)
            styles[key] = RowStyle(
                text_color=row_widget.fg_color,
                background_color=row_widget.bg_color,
            )

        existing = self.presets_manager.get_preset_names()

        if self.editing_name and self.editing_name != name:
            if name in existing:
                QMessageBox.warning(self, "Błąd", f"Preset o nazwie '{name}' już istnieje.")
                return
            self.presets_manager.delete_preset(self.editing_name)

        elif not self.editing_name and name in existing:
            QMessageBox.warning(self, "Błąd", f"Preset o nazwie '{name}' już istnieje.")
            return

        self.presets_manager.save_preset(name, rows, styles or None)
        self.accept()

    def get_saved_name(self) -> str:
        return self.name_input.text().strip()
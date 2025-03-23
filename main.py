import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QPushButton,
    QFileDialog,
    QScrollArea,
    QFrame,
    QMessageBox,
    QGridLayout,
    QListWidget,
    QListWidgetItem,
)
from PyQt5.QtGui import QPixmap, QFont, QIcon, QPalette, QColor, QImage
from PyQt5.QtCore import Qt, QSize
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Image,
    Paragraph,
    Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from PIL import Image as PILImage
import io


class PhotoItem(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.photo_path = None
        layout = QHBoxLayout(self)
        self.image_label = QLabel("No Photo")
        self.image_label.setFixedSize(100, 100)
        layout.addWidget(self.image_label)
        self.add_button = QPushButton("Add Photo")
        layout.addWidget(self.add_button)
        self.add_button.clicked.connect(self.open_photo)
        self.setLayout(layout)

    def open_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Passport Photo", "", "Image Files (*.png *.jpg *.jpeg)"
        )
        if file_path:
            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaled(
                100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.image_label.setPixmap(pixmap)
            self.add_button.setText("Change Photo")
            self.photo_path = file_path


class PassportPhotoSelector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.listWidget = QListWidget()
        self.listWidget.setDragDropMode(QListWidget.InternalMove)
        self.listWidget.setSpacing(5)
        layout = QVBoxLayout(self)
        title = QLabel("Passport Photos")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet("color: #ecf0f1;")
        layout.addWidget(title)
        layout.addWidget(self.listWidget)
        self.setLayout(layout)

    def add_photo(self, index):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Passport Photo", "", "Image Files (*.png *.jpg *.jpeg)"
        )
        if file_path:
            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaled(
                140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )

            photo_label, add_button = self.photo_widgets[index]
            photo_label.setPixmap(pixmap)
            add_button.setText("Change Photo")

            if index >= len(self.photos):
                self.photos.append(file_path)
            else:
                self.photos[index] = file_path

    def update_selectors(self, count):
        current_count = self.listWidget.count()
        while self.listWidget.count() > count:
            self.listWidget.takeItem(self.listWidget.count() - 1)
        while self.listWidget.count() < count:
            item = QListWidgetItem()
            photo_item = PhotoItem()
            item.setSizeHint(photo_item.sizeHint())
            self.listWidget.addItem(item)
            self.listWidget.setItemWidget(item, photo_item)

    def get_photos(self):
        photos = []
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            widget = self.listWidget.itemWidget(item)
            if widget is not None and widget.photo_path:
                photos.append(widget.photo_path)
            else:
                photos.append("")
        return photos


class FamilyInfoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Family Information PDF Generator")
        self.setMinimumSize(800, 700)

        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #2c3e50;
            }
            QLabel {
                color: #ecf0f1;
            }
            QLineEdit, QSpinBox {
                padding: 8px;
                border: 1px solid #7f8c8d;
                border-radius: 4px;
                background-color: #34495e;
                color: #ecf0f1;
            }
            QLineEdit:focus, QSpinBox:focus {
                border: 1px solid #e74c3c;
            }
        """
        )

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header = QLabel("Family Information PDF Generator")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #ecf0f1; margin-bottom: 15px;")
        main_layout.addWidget(header)

        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(15)

        personal_info_label = QLabel("Personal Information")
        personal_info_label.setFont(QFont("Arial", 14, QFont.Bold))
        form_layout.addWidget(personal_info_label)

        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        name_label.setFixedWidth(120)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter first name")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        form_layout.addLayout(name_layout)

        surname_layout = QHBoxLayout()
        surname_label = QLabel("Surname:")
        surname_label.setFixedWidth(120)
        self.surname_input = QLineEdit()
        self.surname_input.setPlaceholderText("Enter last name")
        surname_layout.addWidget(surname_label)
        surname_layout.addWidget(self.surname_input)
        form_layout.addLayout(surname_layout)

        number_layout = QHBoxLayout()
        number_label = QLabel("Phone Number:")
        number_label.setFixedWidth(120)
        self.number_input = QLineEdit()
        self.number_input.setPlaceholderText("Enter phone number")
        number_layout.addWidget(number_label)
        number_layout.addWidget(self.number_input)
        form_layout.addLayout(number_layout)

        family_layout = QHBoxLayout()
        family_label = QLabel("Total Family Members:")
        family_label.setFixedWidth(120)
        self.family_input = QSpinBox()
        self.family_input.setRange(1, 20)
        self.family_input.setValue(1)
        family_layout.addWidget(family_label)
        family_layout.addWidget(self.family_input)
        form_layout.addLayout(family_layout)

        self.family_input.valueChanged.connect(
            lambda val: self.photo_selector.update_selectors(val)
        )

        children_layout = QHBoxLayout()
        children_label = QLabel("Number of Children:")
        children_label.setFixedWidth(120)
        self.children_input = QSpinBox()
        self.children_input.setRange(0, 15)
        self.children_input.setValue(0)
        children_layout.addWidget(children_label)
        children_layout.addWidget(self.children_input)
        form_layout.addLayout(children_layout)

        main_layout.addWidget(form_widget)

        self.photo_selector = PassportPhotoSelector()
        self.photo_selector.update_selectors(self.family_input.value())

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.photo_selector)
        scroll_area.setStyleSheet("border: none;")

        main_layout.addWidget(scroll_area)

        self.generate_button = QPushButton("Generate PDF")
        self.generate_button.setFont(QFont("Arial", 12))
        self.generate_button.setStyleSheet(
            """
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """
        )
        self.generate_button.clicked.connect(self.generate_pdf)
        main_layout.addWidget(self.generate_button)

        self.show()

    def generate_pdf(self):
        name = self.name_input.text().strip()
        surname = self.surname_input.text().strip()
        number = self.number_input.text().strip()
        family_members = self.family_input.value()
        children = self.children_input.value()
        photos = self.photo_selector.get_photos()

        if not name or not surname:
            QMessageBox.warning(
                self, "Missing Information", "Please enter name and surname."
            )
            return

        if not photos:
            QMessageBox.warning(
                self, "Missing Photos", "Please add at least one passport photo."
            )
            return

        default_filename = f"{name}_{surname}.pdf"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF File", default_filename, "PDF Files (*.pdf)"
        )

        if not file_path:
            return

        try:
            self.create_pdf(
                file_path, name, surname, number, family_members, children, photos
            )
            QMessageBox.information(
                self, "Success", f"PDF generated successfully as {file_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate PDF: {str(e)}")

    def create_pdf(
        self, file_path, name, surname, number, family_members, children, photos
    ):
        custom_pagesize = (letter[0], letter[1] + 500)
        doc = SimpleDocTemplate(
            file_path,
            pagesize=custom_pagesize,
            leftMargin=10,
            rightMargin=10,
            topMargin=10,
            bottomMargin=10,
        )
        elements = []

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "Title", parent=styles["Heading1"], fontSize=18, alignment=1, spaceAfter=20
        )
        normal_style = styles["Normal"]

        elements.append(Paragraph(f"Family Information: {name} {surname}", title_style))
        elements.append(Spacer(1, 20))

        data = [
            ["Name:", name],
            ["Surname:", surname],
            ["Phone Number:", number],
            ["Total Family Members:", str(family_members)],
            ["Number of Children:", str(children)],
        ]

        table = Table(data, colWidths=[150, 350])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.lightblue),
                    ("TEXTCOLOR", (0, 0), (0, -1), colors.black),
                    ("ALIGN", (0, 0), (0, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("BACKGROUND", (1, 0), (1, -1), colors.white),
                    ("TEXTCOLOR", (1, 0), (1, -1), colors.black),
                    ("ALIGN", (1, 0), (1, -1), "LEFT"),
                    ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

        elements.append(table)
        elements.append(Spacer(1, 30))

        elements.append(Paragraph("Passport Photos", title_style))
        elements.append(Spacer(1, 20))

        from reportlab.platypus import PageBreak
        from PIL import Image as PILImage

        for i in range(0, len(photos), 2):
            batch = photos[i : i + 2]
            image_elements = []
            for photo_path in batch:
                pil_image = PILImage.open(photo_path)
                img_width, img_height = pil_image.size
                max_width = 250
                scale = max_width / img_width if img_width > max_width else 1
                new_width = img_width * scale
                new_height = img_height * scale
                image_elements.append(
                    Image(photo_path, width=new_width, height=new_height)
                )
            if len(image_elements) < 2:
                image_elements.append("")
            table_images = Table([image_elements])
            table_images.setStyle(
                TableStyle(
                    [
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("GRID", (0, 0), (-1, -1), 1, colors.lightgrey),
                        ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
                        ("TOPPADDING", (0, 0), (-1, -1), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                    ]
                )
            )
            elements.append(table_images)
            if i + 2 < len(photos):
                elements.append(PageBreak())

        doc.build(elements)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FamilyInfoApp()
    sys.exit(app.exec_())

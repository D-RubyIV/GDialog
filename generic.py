import sys

from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, \
    QPushButton, QLineEdit, QLabel, QCheckBox, QComboBox
from PySide6.QtCore import Qt
from sqlalchemy import create_engine, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, relationship
from sqlalchemy.inspection import inspect

from models import BaseModel, GroupRecord

# Define the SQLAlchemy model
Base = declarative_base()

# Database setup
DATABASE_URL = r"sqlite:///database.db"  # For a local database in the current directory
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


class DynamicFieldDialog(QDialog):
    def __init__(self, model: BaseModel, record=None):
        super().__init__()

        self.setWindowTitle(f"{model.__tablename__} - Add/Update Record")
        self.layout = QVBoxLayout()

        self.fields = {}
        self.record = record
        self.model = model

        # Inspect the model's columns
        for column in model.get_filtered_allow_create():
            if column.name != "id" and column.name != "updated_time" and column.name != "created_time":  # Skip 'id' or other fields you don't want to display
                label = QLabel(f"{column.name.capitalize()}:")
                # Boolean
                if isinstance(column.type, Boolean):
                    input_field = QCheckBox()
                    if self.record:
                        input_field.setChecked(getattr(self.record, column.name, False))
                # Số
                elif isinstance(column.type, Integer):
                    input_field = QLineEdit()
                    if self.record:
                        input_field.setText(str(getattr(self.record, column.name, '')))
                # Chuỗi
                elif isinstance(column.type, String):
                    input_field = QLineEdit()
                    if self.record:
                        input_field.setText(getattr(self.record, column.name, ''))
                # Đéo biết nữa
                else:
                    input_field = QLineEdit()

                self.fields[column.name] = input_field
                self.layout.addWidget(label)
                self.layout.addWidget(input_field)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_record)
        self.layout.addWidget(save_button)

        self.setLayout(self.layout)

    def save_record(self):
        session = Session()

        # Create or update record data
        record_data = {}
        for col, input_field in self.fields.items():
            if isinstance(input_field, QCheckBox):
                record_data[col] = input_field.isChecked()
            else:
                record_data[col] = input_field.text()

        if self.record:
            # Update record
            for col, value in record_data.items():
                setattr(self.record, col, value)
            session.add(self.record)  # Bổ sung dòng này để cập nhật trạng thái record
            session.commit()
        else:
            # Create new record
            record = self.model(**record_data)
            session.add(record)
            session.commit()

        session.close()
        self.accept()


class CRUDManagerWidget(QDialog):
    def __init__(self, model, width, height, window=None):
        super().__init__(window)

        self.setWindowTitle(f"{model.__tablename__} CRUD Dialog")
        self.resize(width, height)
        self.layout = QVBoxLayout()

        self.input_layout = QHBoxLayout()
        self.model = model
        self.table_widget = QTableWidget()

        # Set up table headers based on model fields
        headers = self.get_view_header_labels()
        print("HEADER LABELS:")
        print(headers)
        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setHorizontalHeaderLabels(headers)

        self.layout.addWidget(self.table_widget)

        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self.open_create_dialog)
        self.layout.addWidget(self.create_button)

        self.update_button = QPushButton("Update")
        self.update_button.clicked.connect(self.open_update_dialog)
        self.layout.addWidget(self.update_button)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_record)
        self.layout.addWidget(self.delete_button)

        self.load_button = QPushButton("Load Records")
        self.load_button.clicked.connect(self.load_records)
        self.layout.addWidget(self.load_button)

        self.setLayout(self.layout)

    def get_view_header_labels(self):
        return [col.name.capitalize() for col in self.model.get_filtered_allow_view()]

    def load_records(self):
        """Load all records from the database and display them in the table"""
        session = Session()
        records = session.query(self.model).all()
        self.table_widget.setRowCount(len(records))

        for row, record in enumerate(records):
            for col, column in enumerate(self.model.get_filtered_allow_view()):
                self.table_widget.setItem(row, col, QTableWidgetItem(str(getattr(record, column.name))))
        session.close()

    def open_create_dialog(self):
        dialog = DynamicFieldDialog(self.model)
        dialog.exec()
        self.load_records()  # Reload records after adding

    def open_update_dialog(self):
        selected_row = self.table_widget.currentRow()
        if selected_row == -1:
            return  # No row selected

        record_id = int(self.table_widget.item(selected_row, 6).text())
        session = Session()
        record = session.query(self.model).filter_by(id=record_id).first()
        session.close()

        dialog = DynamicFieldDialog(self.model, record)
        dialog.exec()
        self.load_records()  # Reload records after updating

    def delete_record(self):
        selected_row = self.table_widget.currentRow()
        if selected_row == -1:
            return  # No row selected

        record_id = int(self.table_widget.item(selected_row, 6).text())
        session = Session()
        record = session.query(self.model).filter_by(id=record_id).first()

        if record:
            session.delete(record)
            session.commit()

        session.close()
        self.load_records()  # Reload records to show updated list


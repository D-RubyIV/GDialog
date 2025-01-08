import sys

from PySide6.QtWidgets import QApplication

from generic import engine, CRUDManagerWidget
from models import BaseModel, GroupRecord

if __name__ == "__main__":
    BaseModel.metadata.create_all(engine)
    app = QApplication(sys.argv)
    dialog = CRUDManagerWidget(
        model=GroupRecord,
        width=1000,
        height=500
    )
    dialog.show()
    dialog.load_records()
    sys.exit(app.exec())

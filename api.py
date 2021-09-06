import sys
from PyQt5.QtWidgets import QDialog, QApplication
from UI import Ui_Form
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mssql import \
    BIGINT, BINARY, BIT, CHAR, DATE, DATETIME, DATETIME2, \
    DATETIMEOFFSET, DECIMAL, FLOAT, IMAGE, INTEGER, MONEY, \
    NCHAR, NTEXT, NUMERIC, NVARCHAR, REAL, SMALLDATETIME, \
    SMALLINT, SMALLMONEY, SQL_VARIANT, TEXT, TIME, \
    TIMESTAMP, TINYINT, UNIQUEIDENTIFIER, VARBINARY, VARCHAR
from sqlalchemy import Table, MetaData, Column, Integer, String, ForeignKey
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker
import uuid

engine = create_engine('mssql+pyodbc://sa:justChi11@127.0.0.1/test?driver=SQL+Server+Native+Client+11.0')

Base = declarative_base()


#建立school資料表對應
school_metadata = MetaData()

school = Table('School', school_metadata,
            Column('ID', UNIQUEIDENTIFIER, primary_key=True),
            Column('Name', NVARCHAR(8))
        )

class School(object):
    def __init__(self, ID, Name):
        self.ID = ID
        self.Name = Name

mapper(School, school)


#建立student資料表對應
student_metadata = MetaData()

student = Table('Student', student_metadata,
            Column('ID', UNIQUEIDENTIFIER, primary_key=True),
            Column('Name', NVARCHAR(10)),
            Column('School', UNIQUEIDENTIFIER, ForeignKey(School.ID)),
            Column('Sex', NVARCHAR(5))
        )

class Student(object):
    def __init__(self, ID, Name, School, Sex):
        self.ID = ID
        self.Name = Name
        self.School = School
        self.Sex = Sex

mapper(Student, student)


Base.metadata.create_all(engine)


Session = sessionmaker()
Session.configure(bind=engine)
session = Session()


class AppWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        #為新增按鈕的點擊事件綁定function
        self.ui.CButton.clicked.connect(self.CButton_Clicked)

        #為查詢按鈕的點擊事件綁定function
        self.ui.RButton.clicked.connect(self.RButton_Clicked)

        self.show()

    def CButton_Clicked(self):

        #依照校名找出該校資料
        tschool = session.query(School).filter(School.Name==self.ui.CSchoolTextBox.text()).one()
        
        #將各資料塞進物件
        newstudent = Student(ID=uuid.uuid4(), Name=self.ui.CNameTextBox.text(), Sex=self.ui.CSexTextBox.text(), School=tschool.ID)
        
        #將物件存於記憶體
        session.add(newstudent)
        # 這裡是一次增加一筆
        # 若將來需要增加多筆可以改成以下寫法
        # session.add_all([
        #     Student(ID=uuid.uuid4(), Name='Student1', School='School1', Sex='男生'),
        #     Student(ID=uuid.uuid4(), Name='Student2', School='School2', Sex='女生'),
        #     Student(ID=uuid.uuid4(), Name='Student3', School='School3', Sex='女生')])
        
        #確認修改資料庫
        session.commit()

    def RButton_Clicked(self):
        
        #依照學生姓名撈出該名學生所有資料，使用join
        tstudent = session.query(Student,School).join(School,Student.School==School.ID).filter(Student.Name==self.ui.RNameTextbox.text()).one()
        self.ui.lineEdit.setText('ID：'+tstudent.Student.ID+',性名：'+tstudent.Student.Name+
            ',性別：'+tstudent.Student.Sex+',學校：'+tstudent.School.Name)


app = QApplication(sys.argv)
w = AppWindow()
w.show()
sys.exit(app.exec_())
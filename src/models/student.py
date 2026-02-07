from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column


from src.database import Base



class Student(Base):
    __tablename__="students"

    id:Mapped[int]=mapped_column(Integer,primary_key=True,index=True,autoincrement=True)
    name:Mapped[str]=mapped_column(String(255),nullable=False)
    age:Mapped[int]=mapped_column(Integer,nullable=False)
    grade:Mapped[str]=mapped_column(String(255),nullable=False)



    def __repr__(self):
        return f"<Student(id={self.id}, name={self.name}, age={self.age}, grade={self.grade})>"



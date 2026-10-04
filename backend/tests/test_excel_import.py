import io
import openpyxl
from app.services.excel_service import excel_service


def test_excel_student_parsing():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Nama", "Email", "NIS", "NISN", "Gender", "Telepon", "Alamat"])
    ws.append(["Ahmad Test", "ahmad.test@siswa.id", "20249999", "00999999", "L", "0811111111", "Jakarta"])
    
    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)
    
    students = excel_service.parse_student_excel(stream.getvalue())
    assert len(students) == 1
    assert students[0]["name"] == "Ahmad Test"
    assert students[0]["nis"] == "20249999"
    assert students[0]["gender"] == "L"


def test_excel_question_parsing():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Question Text", "Type", "Option A", "Option B", "Option C", "Option D", "Correct Answer", "Points", "Difficulty"])
    ws.append(["Apa ibukota Indonesia?", "multiple_choice", "Bandung", "Jakarta", "Surabaya", "Medan", "B", 10, "easy"])
    
    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)
    
    questions = excel_service.parse_questions_excel(stream.getvalue())
    assert len(questions) == 1
    assert questions[0]["question_text"] == "Apa ibukota Indonesia?"
    assert questions[0]["correct_answer"] == "B"
    assert questions[0]["points"] == 10
    assert len(questions[0]["options"]) == 4

"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND
Mã nguồn chứa danh sách Tool Schemas (JSON Schema) và Execution Layer phục vụ cho MCP Server.
"""

import json
from typing import Dict, Any

# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA (TASK 1.2)
# ==============================================================================

TOOLS_SCHEMA = [
    {
        "name": "academic_query",
        "description": (
            "Tra cứu thông tin học vụ của sinh viên VinUni bằng mã sinh viên, "
            "bao gồm họ tên, lớp, GPA, email, trạng thái học tập và tên cố vấn."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {
                    "type": "string",
                    "description": "Mã sinh viên cần tra cứu (ví dụ: 'SV2026001')."
                }
            },
            "required": ["student_id"]
        }
    },
    {
        "name": "schedule_appointment",
        "description": (
            "Đặt lịch hẹn tư vấn học vụ với cố vấn học tập của sinh viên VinUni."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {
                    "type": "string",
                    "description": "Mã sinh viên cần đặt lịch (ví dụ: 'SV2026001')."
                },
                "datetime_str": {
                    "type": "string",
                    "description": "Thời gian hẹn, ví dụ: '14:00 15/09/2026'."
                },
                "advisor_name": {
                    "type": "string",
                    "description": "Tên cố vấn học tập của sinh viên."
                }
            },
            "required": ["student_id", "datetime_str", "advisor_name"]
        }
    }
]

# ==============================================================================
# 2. MÔ PHỎNG DỮ LIỆU & HÀM THỰC THI TOOL (EXECUTION LAYER)
# ==============================================================================

ACADEMIC_DATABASE = {
    "SV2026001": {
        "student_id": "SV2026001",
        "full_name": "Nguyễn Thị Lê Na",
        "class": "K4B-2A202602501",
        "gpa": 3.68,
        "email": "le.na@vinuni.edu.vn",
        "status": "Đang học",
        "advisor": "PGS.TS Nguyễn Văn A"
    }
}


def execute_academic_query(student_id: str) -> str:
    """Thực thi tra cứu thông tin học vụ của sinh viên"""

    normalized_student_id = student_id.strip().upper()
    student = ACADEMIC_DATABASE.get(normalized_student_id)

    if not student:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy thông tin sinh viên với mã '{student_id}'."
        }, ensure_ascii=False)

    return json.dumps({
        "status": "SUCCESS",
        "student_id": normalized_student_id,
        "data": student
    }, ensure_ascii=False)


def execute_schedule_appointment(
    student_id: str,
    datetime_str: str,
    advisor_name: str
) -> str:
    """Thực thi đặt lịch hẹn tư vấn học vụ với cố vấn"""

    normalized_student_id = student_id.strip().upper()
    student = ACADEMIC_DATABASE.get(normalized_student_id)

    if not student:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy sinh viên '{student_id}' để đặt lịch."
        }, ensure_ascii=False)

    booking_id = f"APT-{normalized_student_id}-{datetime_str.replace(' ', '').replace('/', '')}"

    return json.dumps({
        "status": "SUCCESS",
        "booking_id": booking_id,
        "student_id": normalized_student_id,
        "datetime": datetime_str,
        "advisor_name": advisor_name,
        "message": (
            f"Đặt lịch thành công cho sinh viên {normalized_student_id} "
            f"với cố vấn {advisor_name} vào lúc {datetime_str}."
        )
    }, ensure_ascii=False)


# Router gọi tool thực tế
TOOL_ROUTER = {
    "academic_query": execute_academic_query,
    "schedule_appointment": execute_schedule_appointment
}


def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Hàm trung chuyển thực thi tool"""

    if tool_name in TOOL_ROUTER:
        return TOOL_ROUTER[tool_name](**arguments)

    return json.dumps({
        "status": "UNKNOWN_TOOL",
        "error": f"Tool '{tool_name}' không tồn tại!"
    }, ensure_ascii=False)

# if __name__ == "__main__":
#     print("=== TEST LOAN INFORMATION LOOKUP ===")

#     result = dispatch_tool_call(
#         "loan_information_lookup",
#         {
#             "loan_type": "car_loan",
#             "loan_amount": 500000000,
#             "monthly_income": 25000000
#         }
#     )

#     print(result)
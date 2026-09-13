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
    # Tool 1: Tra cứu thông tin sản phẩm vay
    {
        "name": "loan_information_lookup",
        "description": (
            "Tra cứu thông tin sản phẩm vay của ngân hàng dựa trên nhu cầu "
            "của khách hàng như loại khoản vay, số tiền vay và thu nhập hàng tháng."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "loan_type": {
                    "type": "string",
                    "description": (
                        "Loại khoản vay khách hàng quan tâm, "
                        "ví dụ: 'car_loan', 'home_loan', 'personal_loan'."
                    )
                },
                "loan_amount": {
                    "type": "number",
                    "description": "Số tiền khách hàng muốn vay, đơn vị VND."
                },
                "monthly_income": {
                    "type": "number",
                    "description": "Thu nhập hàng tháng của khách hàng, đơn vị VND."
                }
            },
            "required": ["loan_type"]
        }
    },

    # Tool 2: Đặt lịch tư vấn với chuyên viên tín dụng
    {
        "name": "loan_consultation_booking",
        "description": (
            "Đặt lịch hẹn tư vấn khoản vay với chuyên viên tín dụng của ngân hàng."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "customer_name": {
                    "type": "string",
                    "description": "Họ và tên khách hàng."
                },
                "phone_number": {
                    "type": "string",
                    "description": (
                        "Số điện thoại của khách hàng, "
                        "ví dụ: '0901234567'."
                    )
                },
                "datetime_str": {
                    "type": "string",
                    "description": (
                        "Thời gian khách hàng muốn đặt lịch tư vấn, "
                        "ví dụ: '14:00 20/09/2026'."
                    )
                },
                "loan_type": {
                    "type": "string",
                    "description": (
                        "Loại khoản vay cần tư vấn, "
                        "ví dụ: 'car_loan', 'home_loan', 'personal_loan'."
                    )
                }
            },
            "required": [
                "customer_name",
                "phone_number",
                "datetime_str",
                "loan_type"
            ]
        }
    }
]

# ==============================================================================
# 2. MÔ PHỎNG DỮ LIỆU & HÀM THỰC THI TOOL (EXECUTION LAYER)
# ==============================================================================

MOCK_DATABASE = {
    "car_loan": {
        "product_name": "Vay mua ô tô cá nhân",
        "interest_rate": "8.5%/năm",
        "max_loan_amount": 2000000000,
        "max_term_months": 84,
        "min_monthly_income": 15000000,
        "required_documents": [
            "CCCD",
            "Chứng minh thu nhập",
            "Hợp đồng mua bán xe"
        ]
    },
    "home_loan": {
        "product_name": "Vay mua nhà",
        "interest_rate": "7.8%/năm",
        "max_loan_amount": 5000000000,
        "max_term_months": 300,
        "min_monthly_income": 20000000,
        "required_documents": [
            "CCCD",
            "Chứng minh thu nhập",
            "Hợp đồng mua bán nhà",
            "Hồ sơ tài sản bảo đảm"
        ]
    },
    "personal_loan": {
        "product_name": "Vay tiêu dùng tín chấp",
        "interest_rate": "12.0%/năm",
        "max_loan_amount": 500000000,
        "max_term_months": 60,
        "min_monthly_income": 10000000,
        "required_documents": [
            "CCCD",
            "Chứng minh thu nhập"
        ]
    }
}


def execute_loan_information_lookup(
    loan_type: str,
    loan_amount: float = None,
    monthly_income: float = None
) -> str:
    """Thực thi tra cứu thông tin sản phẩm vay"""

    normalized_loan_type = loan_type.strip().lower()
    loan = MOCK_DATABASE.get(normalized_loan_type)

    if not loan:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy sản phẩm vay loại '{loan_type}'."
        }, ensure_ascii=False)

    result = {
        "status": "SUCCESS",
        "loan_type": normalized_loan_type,
        "data": loan
    }

    # Đánh giá sơ bộ nếu khách hàng cung cấp thêm thông tin
    if loan_amount is not None:
        result["loan_amount_check"] = (
            "ELIGIBLE"
            if loan_amount <= loan["max_loan_amount"]
            else "EXCEEDS_MAX_AMOUNT"
        )

    if monthly_income is not None:
        result["income_check"] = (
            "ELIGIBLE"
            if monthly_income >= loan["min_monthly_income"]
            else "BELOW_MINIMUM_INCOME"
        )

    return json.dumps(result, ensure_ascii=False)


def execute_loan_consultation_booking(
    customer_name: str,
    phone_number: str,
    datetime_str: str,
    loan_type: str
) -> str:
    """Thực thi đặt lịch tư vấn khoản vay với chuyên viên ngân hàng"""

    booking_id = f"LOAN-BK-{phone_number[-4:]}-99"

    return json.dumps({
        "status": "SUCCESS",
        "booking_id": booking_id,
        "customer_name": customer_name,
        "phone_number": phone_number,
        "loan_type": loan_type,
        "datetime": datetime_str,
        "advisor": "Chuyên viên tín dụng 01",
        "message": (
            f"Đặt lịch thành công cho khách hàng {customer_name} "
            f"tư vấn {loan_type} vào lúc {datetime_str}."
        )
    }, ensure_ascii=False)


# Router gọi tool thực tế
TOOL_ROUTER = {
    "loan_information_lookup": execute_loan_information_lookup,
    "loan_consultation_booking": execute_loan_consultation_booking
}


def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Hàm trung chuyển thực thi tool"""

    # TODO 2.1 - Điều tuyến Tool Call
    if tool_name == "loan_information_lookup":
        return execute_loan_information_lookup(**arguments)

    elif tool_name == "loan_consultation_booking":
        return execute_loan_consultation_booking(**arguments)

    return json.dumps({
        "status": "UNKNOWN_TOOL",
        "error": f"Tool '{tool_name}' không tồn tại!"
    }, ensure_ascii=False)

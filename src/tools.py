"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND

Đề tài:
Trợ lý AI tư vấn khoản vay ngân hàng.

Mã nguồn chứa:
- Tool Schemas chuẩn Native JSON Schema
- Mock Database sản phẩm vay
- Execution Layer
- Tool Router phục vụ MCP Server
"""

import json
from typing import Dict, Any


# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA
# ==============================================================================

TOOLS_SCHEMA = [

    # ==========================================================================
    # TOOL 1: TRA CỨU THÔNG TIN KHOẢN VAY
    # ==========================================================================

    {
        "name": "loan_information_lookup",
        "description": (
            "Tra cứu thông tin sản phẩm vay của ngân hàng theo loại khoản vay. "
            "Có thể sử dụng thêm số tiền muốn vay và thu nhập hàng tháng "
            "để kiểm tra điều kiện sơ bộ."
        ),
        "parameters": {
            "type": "object",
            "properties": {

                "loan_type": {
                    "type": "string",
                    "description": (
                        "Loại khoản vay cần tra cứu. "
                        "Các giá trị hỗ trợ gồm: "
                        "'car_loan' (vay mua ô tô), "
                        "'home_loan' (vay mua nhà), "
                        "'personal_loan' (vay tiêu dùng cá nhân)."
                    )
                },

                "loan_amount": {
                    "type": "number",
                    "description": (
                        "Số tiền khách hàng muốn vay, đơn vị VND. "
                        "Ví dụ: 500000000 tương ứng 500 triệu đồng."
                    )
                },

                "monthly_income": {
                    "type": "number",
                    "description": (
                        "Thu nhập hàng tháng của khách hàng, đơn vị VND. "
                        "Ví dụ: 25000000 tương ứng 25 triệu đồng/tháng."
                    )
                }
            },

            "required": [
                "loan_type"
            ]
        }
    },


    # ==========================================================================
    # TOOL 2: ĐẶT LỊCH TƯ VẤN KHOẢN VAY
    # ==========================================================================

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
                    "description": (
                        "Họ và tên khách hàng cần đặt lịch tư vấn."
                    )
                },

                "phone_number": {
                    "type": "string",
                    "description": (
                        "Số điện thoại liên hệ của khách hàng. "
                        "Ví dụ: '0901234567'."
                    )
                },

                "datetime_str": {
                    "type": "string",
                    "description": (
                        "Ngày và giờ khách hàng muốn đặt lịch tư vấn. "
                        "Ví dụ: '14:00 20/09/2026'."
                    )
                },

                "loan_type": {
                    "type": "string",
                    "description": (
                        "Loại khoản vay cần tư vấn. "
                        "Ví dụ: 'car_loan', 'home_loan', 'personal_loan'."
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
# 2. MOCK DATABASE SẢN PHẨM VAY
# ==============================================================================

LOAN_DATABASE = {

    "car_loan": {
        "product_code": "CAR001",
        "product_name": "Vay mua ô tô cá nhân",
        "interest_rate": "8.5%/năm",
        "max_loan_amount": 2_000_000_000,
        "max_term_months": 84,
        "min_monthly_income": 15_000_000,
        "required_documents": [
            "CCCD",
            "Chứng minh thu nhập",
            "Hợp đồng mua bán xe"
        ]
    },

    "home_loan": {
        "product_code": "HOME001",
        "product_name": "Vay mua nhà",
        "interest_rate": "7.8%/năm",
        "max_loan_amount": 5_000_000_000,
        "max_term_months": 300,
        "min_monthly_income": 20_000_000,
        "required_documents": [
            "CCCD",
            "Chứng minh thu nhập",
            "Hợp đồng mua bán nhà",
            "Hồ sơ tài sản bảo đảm"
        ]
    },

    "personal_loan": {
        "product_code": "PERSONAL001",
        "product_name": "Vay tiêu dùng tín chấp",
        "interest_rate": "12.0%/năm",
        "max_loan_amount": 500_000_000,
        "max_term_months": 60,
        "min_monthly_income": 10_000_000,
        "required_documents": [
            "CCCD",
            "Chứng minh thu nhập"
        ]
    }
}


# ==============================================================================
# 3. HÀM THỰC THI TOOL 1
# ==============================================================================

def execute_loan_information_lookup(
    loan_type: str,
    loan_amount: float = None,
    monthly_income: float = None
) -> str:
    """
    Thực thi tra cứu thông tin sản phẩm vay.

    Có thể kiểm tra sơ bộ:
    - số tiền vay có vượt hạn mức không
    - thu nhập có đạt yêu cầu tối thiểu không
    """

    normalized_loan_type = (
        loan_type
        .strip()
        .lower()
    )

    loan = LOAN_DATABASE.get(
        normalized_loan_type
    )

    # ==========================================================================
    # KHÔNG TÌM THẤY SẢN PHẨM
    # ==========================================================================

    if not loan:

        return json.dumps(
            {
                "status": "NOT_FOUND",
                "loan_type": normalized_loan_type,
                "message": (
                    f"Không tìm thấy sản phẩm vay "
                    f"loại '{loan_type}'."
                )
            },
            ensure_ascii=False
        )


    # ==========================================================================
    # KẾT QUẢ CƠ BẢN
    # ==========================================================================

    result = {
        "status": "SUCCESS",
        "loan_type": normalized_loan_type,
        "data": loan
    }


    # ==========================================================================
    # KIỂM TRA SỐ TIỀN VAY
    # ==========================================================================

    if loan_amount is not None:

        result["requested_loan_amount"] = (
            loan_amount
        )

        if (
            loan_amount
            <= loan["max_loan_amount"]
        ):

            result["loan_amount_check"] = (
                "ELIGIBLE"
            )

        else:

            result["loan_amount_check"] = (
                "EXCEEDS_MAX_AMOUNT"
            )


    # ==========================================================================
    # KIỂM TRA THU NHẬP
    # ==========================================================================

    if monthly_income is not None:

        result["monthly_income"] = (
            monthly_income
        )

        if (
            monthly_income
            >= loan["min_monthly_income"]
        ):

            result["income_check"] = (
                "ELIGIBLE"
            )

        else:

            result["income_check"] = (
                "BELOW_MINIMUM_INCOME"
            )


    # ==========================================================================
    # ĐÁNH GIÁ SƠ BỘ
    # ==========================================================================

    checks = []

    if "loan_amount_check" in result:
        checks.append(
            result["loan_amount_check"]
            == "ELIGIBLE"
        )

    if "income_check" in result:
        checks.append(
            result["income_check"]
            == "ELIGIBLE"
        )

    if checks:

        result["preliminary_eligibility"] = (
            "ELIGIBLE"
            if all(checks)
            else "NOT_ELIGIBLE"
        )

    else:

        result["preliminary_eligibility"] = (
            "NOT_ASSESSED"
        )


    return json.dumps(
        result,
        ensure_ascii=False
    )


# ==============================================================================
# 4. HÀM THỰC THI TOOL 2
# ==============================================================================

def execute_loan_consultation_booking(
    customer_name: str,
    phone_number: str,
    datetime_str: str,
    loan_type: str
) -> str:
    """
    Thực thi đặt lịch tư vấn khoản vay
    với chuyên viên tín dụng.
    """

    normalized_loan_type = (
        loan_type
        .strip()
        .lower()
    )

    # ==========================================================================
    # KIỂM TRA LOẠI KHOẢN VAY
    # ==========================================================================

    if normalized_loan_type not in LOAN_DATABASE:

        return json.dumps(
            {
                "status": "NOT_FOUND",
                "message": (
                    f"Không tìm thấy sản phẩm vay "
                    f"loại '{loan_type}' để đặt lịch tư vấn."
                )
            },
            ensure_ascii=False
        )


    # ==========================================================================
    # TẠO BOOKING ID
    # ==========================================================================

    phone_suffix = (
        phone_number[-4:]
        if len(phone_number) >= 4
        else phone_number
    )

    normalized_datetime = (
        datetime_str
        .replace(" ", "")
        .replace("/", "")
        .replace(":", "")
    )

    booking_id = (
        f"LOAN-BK-"
        f"{phone_suffix}-"
        f"{normalized_datetime}"
    )


    # ==========================================================================
    # MOCK CHUYÊN VIÊN
    # ==========================================================================

    advisor_name = (
        "Chuyên viên tín dụng 01"
    )


    # ==========================================================================
    # RESPONSE
    # ==========================================================================

    return json.dumps(
        {
            "status": "SUCCESS",
            "booking_id": booking_id,
            "customer_name": customer_name,
            "phone_number": phone_number,
            "loan_type": normalized_loan_type,
            "datetime": datetime_str,
            "advisor": advisor_name,
            "message": (
                f"Đặt lịch thành công cho khách hàng "
                f"{customer_name} tư vấn "
                f"{normalized_loan_type} "
                f"vào lúc {datetime_str}."
            )
        },
        ensure_ascii=False
    )


# ==============================================================================
# 5. TOOL ROUTER
# ==============================================================================

TOOL_ROUTER = {

    "loan_information_lookup":
        execute_loan_information_lookup,

    "loan_consultation_booking":
        execute_loan_consultation_booking
}


# ==============================================================================
# 6. DISPATCH TOOL CALL
# ==============================================================================

def dispatch_tool_call(
    tool_name: str,
    arguments: Dict[str, Any]
) -> str:
    """
    Hàm trung chuyển thực thi Tool.

    - Nhận tên Tool
    - Nhận arguments
    - Gọi hàm thực thi tương ứng
    """

    if tool_name == "loan_information_lookup":

        return execute_loan_information_lookup(
            **arguments
        )

    elif tool_name == "loan_consultation_booking":

        return execute_loan_consultation_booking(
            **arguments
        )

    return json.dumps(
        {
            "status": "UNKNOWN_TOOL",
            "error": (
                f"Tool '{tool_name}' "
                f"không tồn tại!"
            )
        },
        ensure_ascii=False
    )


# ==============================================================================
# 7. TEST ĐỘC LẬP
# ==============================================================================

if __name__ == "__main__":

    print(
        "=========================================================="
    )

    print(
        "🛠️ KIỂM THỬ TOOL BACKEND - "
        "BANKING LOAN ADVISORY"
    )

    print(
        "=========================================================="
    )


    # ==========================================================================
    # TEST TOOL 1
    # ==========================================================================

    print(
        "\n--- TEST 1: "
        "Tra cứu vay mua ô tô ---"
    )

    result_1 = dispatch_tool_call(
        "loan_information_lookup",
        {
            "loan_type": "car_loan",
            "loan_amount": 500_000_000,
            "monthly_income": 25_000_000
        }
    )

    print(
        json.dumps(
            json.loads(result_1),
            ensure_ascii=False,
            indent=2
        )
    )


    # ==========================================================================
    # TEST TOOL 2
    # ==========================================================================

    print(
        "\n--- TEST 2: "
        "Đặt lịch tư vấn vay mua ô tô ---"
    )

    result_2 = dispatch_tool_call(
        "loan_consultation_booking",
        {
            "customer_name": "Nguyễn Văn An",
            "phone_number": "0901234567",
            "datetime_str": "14:00 20/09/2026",
            "loan_type": "car_loan"
        }
    )

    print(
        json.dumps(
            json.loads(result_2),
            ensure_ascii=False,
            indent=2
        )
    )


    # ==========================================================================
    # TEST EDGE CASE
    # ==========================================================================

    print(
        "\n--- TEST 3: "
        "Loan type không tồn tại ---"
    )

    result_3 = dispatch_tool_call(
        "loan_information_lookup",
        {
            "loan_type": "education_loan"
        }
    )

    print(
        json.dumps(
            json.loads(result_3),
            ensure_ascii=False,
            indent=2
        )
    )
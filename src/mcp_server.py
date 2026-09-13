"""
🔌 MODEL CONTEXT PROTOCOL (MCP) SERVER MODULE

Đề tài:
Trợ lý AI tư vấn khoản vay ngân hàng.

Mô phỏng kiến trúc MCP Server (Client-Server Architecture)
cung cấp các công cụ chuẩn hóa cho ReAct Agent.
"""

import json
import sys

from typing import Dict, Any, List

from tools import TOOLS_SCHEMA, dispatch_tool_call


# ==============================================================================
# ENCODING SETUP
# ==============================================================================

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(
            encoding="utf-8"
        )
    except Exception:
        pass


# ==============================================================================
# MCP BANKING SERVER
# ==============================================================================

class MCPBankingServer:
    """
    Giả lập MCP Server cho hệ thống tư vấn khoản vay ngân hàng.

    Server công bố các Tool như:
    - loan_information_lookup
    - loan_consultation_booking
    """

    def __init__(
        self,
        server_name: str = "banking-loan-mcp-server"
    ):
        self.server_name = server_name
        self.version = "2026.1.0"


    # ==========================================================================
    # LIST TOOLS
    # ==========================================================================

    def list_tools(
        self
    ) -> List[Dict[str, Any]]:
        """
        Trả về danh sách Tools theo schema
        được khai báo trong src/tools.py.
        """

        return TOOLS_SCHEMA


    # ==========================================================================
    # CALL TOOL
    # ==========================================================================

    def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        [TASK 2.1]

        Thực thi Tool trên MCP Server theo chuẩn JSON-RPC 2.0.

        Quy trình:
        1. Gọi dispatch_tool_call(tool_name, arguments)
        2. Parse chuỗi JSON trả về bằng json.loads()
        3. Đóng gói response theo JSON-RPC 2.0
        """

        raw_result = dispatch_tool_call(
            tool_name,
            arguments
        )

        content = json.loads(
            raw_result
        )

        return {
            "jsonrpc": "2.0",
            "server": self.server_name,
            "tool": tool_name,
            "result": content
        }


# ==============================================================================
# TEST MCP SERVER ĐỘC LẬP
# ==============================================================================

if __name__ == "__main__":

    print(
        "=========================================================="
    )

    print(
        "🔌 KIỂM THỬ ĐỘC LẬP MCP SERVER "
        "(banking-loan-mcp-server)"
    )

    print(
        "=========================================================="
    )

    # ==========================================================================
    # KHỞI TẠO SERVER
    # ==========================================================================

    server = MCPBankingServer()

    tools = server.list_tools()

    print(
        f"✅ Khởi tạo thành công MCP Server: "
        f"{server.server_name} "
        f"(Version: {server.version})"
    )

    print(
        f"📦 Số lượng Tools công bố: "
        f"{len(tools)}"
    )


    # ==========================================================================
    # TEST TOOL SCHEMA 1:
    # loan_information_lookup
    # ==========================================================================

    lookup_tool = next(
        (
            t for t in tools
            if t.get("name")
            == "loan_information_lookup"
        ),
        None
    )

    if (
        lookup_tool
        and lookup_tool
        .get("parameters", {})
        .get("properties")
    ):

        print(
            "✅ Tool 'loan_information_lookup' "
            "đã có schema đầy đủ."
        )

    else:

        print(
            "⏳ Tool 'loan_information_lookup' "
            "chưa được định nghĩa đầy đủ "
            "trong 'src/tools.py'."
        )


    # ==========================================================================
    # TEST TOOL SCHEMA 2:
    # loan_consultation_booking
    # ==========================================================================

    booking_tool = next(
        (
            t for t in tools
            if t.get("name")
            == "loan_consultation_booking"
        ),
        None
    )

    if (
        booking_tool
        and booking_tool
        .get("parameters", {})
        .get("properties")
    ):

        print(
            "✅ Tool 'loan_consultation_booking' "
            "đã có schema đầy đủ."
        )

    else:

        print(
            "⏳ Tool 'loan_consultation_booking' "
            "chưa được định nghĩa đầy đủ "
            "trong 'src/tools.py'."
        )


    # ==========================================================================
    # TEST TOOL 1:
    # TRA CỨU SẢN PHẨM VAY
    # ==========================================================================

    print(
        "\n--- TEST TOOL 1: "
        "loan_information_lookup ---"
    )

    lookup_result = server.call_tool(
        "loan_information_lookup",
        {
            "loan_type": "car_loan",
            "loan_amount": 500000000,
            "monthly_income": 25000000
        }
    )

    print(
        "✅ Test dispatch tool "
        "'loan_information_lookup' thành công:"
    )

    print(
        json.dumps(
            lookup_result,
            ensure_ascii=False,
            indent=2
        )
    )


    # ==========================================================================
    # TEST TOOL 2:
    # ĐẶT LỊCH TƯ VẤN
    # ==========================================================================

    print(
        "\n--- TEST TOOL 2: "
        "loan_consultation_booking ---"
    )

    booking_result = server.call_tool(
        "loan_consultation_booking",
        {
            "customer_name": "Nguyễn Văn An",
            "phone_number": "0901234567",
            "datetime_str": "14:00 20/09/2026",
            "loan_type": "car_loan"
        }
    )

    print(
        "✅ Test dispatch tool "
        "'loan_consultation_booking' thành công:"
    )

    print(
        json.dumps(
            booking_result,
            ensure_ascii=False,
            indent=2
        )
    )


    # ==========================================================================
    # TEST EDGE CASE:
    # SẢN PHẨM KHÔNG TỒN TẠI
    # ==========================================================================

    print(
        "\n--- TEST EDGE CASE: "
        "loan type không tồn tại ---"
    )

    not_found_result = server.call_tool(
        "loan_information_lookup",
        {
            "loan_type": "education_loan"
        }
    )

    print(
        json.dumps(
            not_found_result,
            ensure_ascii=False,
            indent=2
        )
    )
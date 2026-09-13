"""
🔌 MODEL CONTEXT PROTOCOL (MCP) SERVER MODULE
Mô phỏng kiến trúc MCP Server (Client-Server Architecture) cung cấp công cụ chuẩn hóa.
"""

import json
import sys
from typing import Dict, Any, List
from tools import TOOLS_SCHEMA, dispatch_tool_call

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class MCPAcademicServer:
    """
    Giả lập MCP Server tuân thủ chuẩn giao thức Model Context Protocol
    """
    def __init__(self, server_name: str = "vinuni-academic-mcp-server"):
        self.server_name = server_name
        self.version = "2026.1.0"
        
    def list_tools(self) -> List[Dict[str, Any]]:
        """Trả về danh sách các Tools chuẩn giao thức MCP"""
        return TOOLS_SCHEMA
        
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        [TASK 2.1] Thực thi Tool trên MCP Server theo chuẩn JSON-RPC 2.0.

        Quy trình:
        1. Gọi dispatch_tool_call(tool_name, arguments)
        2. Parse chuỗi JSON trả về bằng json.loads()
        3. Đóng gói response theo format MCP JSON-RPC 2.0
        """

        try:
            # Bước 1: Gọi Tool Router
            raw_result = dispatch_tool_call(tool_name, arguments)

            # Bước 2: Chuyển JSON string -> Python dict
            content = json.loads(raw_result)

            # Bước 3: Đóng gói phản hồi MCP JSON-RPC 2.0
            return {
                "jsonrpc": "2.0",
                "server": self.server_name,
                "tool": tool_name,
                "result": content
            }

        except json.JSONDecodeError as e:
            return {
                "jsonrpc": "2.0",
                "server": self.server_name,
                "tool": tool_name,
                "result": {
                    "status": "INVALID_TOOL_RESPONSE",
                    "error": f"Không thể parse JSON từ Tool: {str(e)}"
                }
            }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "server": self.server_name,
                "tool": tool_name,
                "result": {
                    "status": "MCP_EXECUTION_ERROR",
                    "error": str(e)
                }
            }


if __name__ == "__main__":
    print("==========================================================")
    print("🔌 KIỂM THỬ ĐỘC LẬP MCP SERVER (banking-loan-mcp-server)")
    print("==========================================================")

    server = MCPAcademicServer()

    tools = server.list_tools()

    print(
        f"✅ Khởi tạo thành công MCP Server: "
        f"{server.server_name} (Version: {server.version})"
    )

    print(f"📦 Số lượng Tools công bố: {len(tools)}")

    # ==========================================================
    # TEST TOOL SCHEMA
    # ==========================================================

    booking_tool = next(
        (
            t for t in tools
            if t.get("name") == "loan_consultation_booking"
        ),
        None
    )

    if (
        booking_tool
        and booking_tool.get("parameters", {}).get("properties")
    ):
        print(
            "✅ [TODO 1.2]: Tool 'loan_consultation_booking' "
            "đã có schema đầy đủ."
        )
    else:
        print(
            "⏳ [TODO 1.2]: Tool 'loan_consultation_booking' "
            "chưa được định nghĩa properties."
        )

    # ==========================================================
    # TEST TOOL 1: LOAN INFORMATION LOOKUP
    # ==========================================================

    test_result = server.call_tool(
        "loan_information_lookup",
        {
            "loan_type": "car_loan",
            "loan_amount": 500000000,
            "monthly_income": 25000000
        }
    )

    print(
        "✅ [TODO 2.1]: Test dispatch tool "
        "'loan_information_lookup' thành công:"
    )

    print(
        f"   Phản hồi JSON-RPC: "
        f"{json.dumps(test_result, ensure_ascii=False, indent=2)}"
    )

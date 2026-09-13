"""
🚀 CORE AGENT APPLICATION (DAY 03: CHATBOT VS REACT AGENT)
Thực thi so sánh giữa Chatbot Baseline (Cấp 2) và ReAct Agent kết nối MCP Server (Cấp 3).
"""

import json
import os
import sys
import time

from dotenv import load_dotenv


# ==============================================================================
# PATH / ENCODING SETUP
# ==============================================================================

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ==============================================================================
# IMPORT PROJECT MODULES
# ==============================================================================

# Nếu class trong mcp_server.py của bạn vẫn đang tên MCPAcademicServer
# thì giữ nguyên import này.
from mcp_server import MCPAcademicServer

from prompts import (
    CHATBOT_BASELINE_PROMPT,
    REACT_AGENT_SYSTEM_PROMPT,
    MAX_ITERATIONS
)

from providers import get_llm_provider


# Load environment variables từ .env
load_dotenv()


# ==============================================================================
# LOAD TEST CASES
# ==============================================================================

def load_test_cases():
    """
    Tải danh sách test cases từ:
    config/test_cases.json

    Nếu chưa tồn tại thì dùng:
    config/test_cases.example.json
    """

    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    config_path = os.path.join(
        base_dir,
        "config",
        "test_cases.json"
    )

    if not os.path.exists(config_path):

        example_path = os.path.join(
            base_dir,
            "config",
            "test_cases.example.json"
        )

        if os.path.exists(example_path):

            print(
                "⚠️ [CONFIG NOTICE]: "
                "Chưa thấy file 'config/test_cases.json'."
            )

            print(
                "👉 Đang sử dụng "
                "'config/test_cases.example.json'."
            )

            print(
                "👉 Hãy copy file mẫu thành "
                "'config/test_cases.json' "
                "và chỉnh sửa theo đề tài ngân hàng.\n"
            )

            config_path = example_path

        else:
            config_path = "test_cases.json"

    with open(
        config_path,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


# ==============================================================================
# SAVE WATERFALL TRACE
# ==============================================================================

def save_waterfall_trace(trace_data: list):
    """
    Ghi Waterfall Trace Log ra:
    docs/trace_waterfall.json
    """

    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    docs_dir = os.path.join(
        base_dir,
        "docs"
    )

    os.makedirs(
        docs_dir,
        exist_ok=True
    )

    trace_path = os.path.join(
        docs_dir,
        "trace_waterfall.json"
    )

    with open(
        trace_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            trace_data,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(
        f"📊 [OBSERVABILITY]: "
        f"Đã lưu {len(trace_data)} sự kiện "
        f"Waterfall Trace tại '{trace_path}'!"
    )


# ==============================================================================
# CHATBOT BASELINE
# ==============================================================================

def run_baseline_chatbot(
    user_query: str,
    provider
):
    """
    Chatbot Baseline:
    Không có quyền sử dụng Tool.
    """

    print(
        f"\n💬 [CHATBOT BASELINE] "
        f"Câu hỏi: {user_query}"
    )

    response = provider.generate(
        user_query,
        system_prompt=CHATBOT_BASELINE_PROMPT
    )

    print(
        f"🤖 Chatbot phản hồi:\n"
        f"{response}"
    )


# ==============================================================================
# REACT AGENT
# ==============================================================================

def run_react_agent(
    user_query: str,
    provider,
    mcp_server: MCPAcademicServer
) -> list:

    """
    [REACT AGENT LOOP]

    Thực thi vòng lặp:

    Thought
        ↓
    Action
        ↓
    Observation
        ↓
    Thought
        ↓
    ...
        ↓
    Final Answer

    Observation từ Tool sẽ được đưa trở lại cho LLM
    ở iteration tiếp theo.

    Trả về danh sách Waterfall Trace Logs.
    """

    print(
        f"\n🤖 [REACT AGENT] "
        f"Câu hỏi: {user_query}"
    )

    step = 0
    trace_logs = []

    # Danh sách Tool schemas do MCP Server công bố
    tools_list = mcp_server.list_tools()

    # Context ban đầu là câu hỏi gốc
    current_context = user_query

    # ======================================================================
    # REACT LOOP
    # ======================================================================

    while step < MAX_ITERATIONS:

        step += 1

        step_start_time = time.time()

        print(
            f"\n--- 🔄 ReAct Loop "
            f"(Step {step}/{MAX_ITERATIONS}) ---"
        )

        # ------------------------------------------------------------------
        # GỌI LLM VỚI NATIVE TOOL CALLING
        # ------------------------------------------------------------------

        llm_response = provider.generate_with_tools(
            current_context,
            tools_list,
            system_prompt=REACT_AGENT_SYSTEM_PROMPT
        )

        latency_ms = round(
            (time.time() - step_start_time) * 1000,
            2
        )

        thought = llm_response.get(
            "thought",
            "Đang suy luận..."
        )

        print(
            f"🧠 [Thought]: "
            f"{thought}"
        )

        # ==================================================================
        # CASE 1:
        # LLM TRẢ VỀ TEXT -> FINAL ANSWER
        # ==================================================================

        if llm_response.get("type") == "text":

            final_content = llm_response.get(
                "content",
                ""
            )

            print(
                f"🏁 [Final Answer]: "
                f"{final_content}"
            )

            trace_logs.append({
                "step": step,
                "query": user_query,
                "action_type": "FINAL_ANSWER",
                "thought": thought,
                "output": final_content,
                "latency_ms": latency_ms
            })

            break

        # ==================================================================
        # CASE 2:
        # LLM YÊU CẦU GỌI TOOL
        # ==================================================================

        elif llm_response.get("type") == "tool_call":

            tool_name = llm_response.get(
                "tool_name"
            )

            arguments = llm_response.get(
                "arguments",
                {}
            )

            print(
                f"🛠️ [Action Proposed]: "
                f"{tool_name}({arguments})"
            )

            # --------------------------------------------------------------
            # THỰC THI TOOL QUA MCP SERVER
            # --------------------------------------------------------------

            mcp_result = mcp_server.call_tool(
                tool_name,
                arguments
            )

            obs_data = mcp_result.get(
                "result",
                {}
            )

            obs_str = json.dumps(
                obs_data,
                ensure_ascii=False
            )

            print(
                f"👁️ [Observation từ MCP Server]: "
                f"{obs_str}"
            )

            # --------------------------------------------------------------
            # GHI WATERFALL TRACE
            # --------------------------------------------------------------

            trace_logs.append({
                "step": step,
                "query": user_query,
                "action_type": "TOOL_EXECUTION",
                "tool_name": tool_name,
                "arguments": arguments,
                "observation": obs_data,
                "latency_ms": latency_ms
            })

            # --------------------------------------------------------------
            # ĐƯA OBSERVATION TRỞ LẠI CHO LLM
            #
            # Quan trọng:
            # KHÔNG break ở đây.
            #
            # Agent phải đọc Observation và quyết định:
            # - gọi Tool tiếp theo
            # - hoặc trả Final Answer
            # --------------------------------------------------------------

            current_context += (
                "\n\n"
                "===== REACT HISTORY =====\n"
                f"Action: {tool_name}\n"
                f"Arguments: "
                f"{json.dumps(arguments, ensure_ascii=False)}\n"
                f"Observation: {obs_str}\n"
                "=========================\n\n"
                "Hãy tiếp tục xử lý yêu cầu ban đầu dựa trên "
                "Observation vừa nhận được. "
                "Nếu cần sử dụng thêm công cụ thì hãy gọi công cụ phù hợp. "
                "Nếu đã đủ thông tin thì hãy trả lời người dùng."
            )

        # ==================================================================
        # RESPONSE TYPE KHÔNG HỢP LỆ
        # ==================================================================

        else:

            print(
                "❌ [ERROR]: "
                "LLM trả về response type không hợp lệ."
            )

            trace_logs.append({
                "step": step,
                "query": user_query,
                "action_type": "ERROR",
                "thought": thought,
                "output": "Invalid LLM response type",
                "latency_ms": latency_ms
            })

            break

    # ==========================================================================
    # MAX ITERATIONS REACHED
    # ==========================================================================

    if (
        step >= MAX_ITERATIONS
        and (
            not trace_logs
            or trace_logs[-1].get(
                "action_type"
            ) != "FINAL_ANSWER"
        )
    ):

        warning_message = (
            f"Agent đã đạt giới hạn "
            f"{MAX_ITERATIONS} iterations "
            f"nhưng chưa đưa ra Final Answer."
        )

        print(
            f"\n⚠️ [MAX ITERATIONS]: "
            f"{warning_message}"
        )

        trace_logs.append({
            "step": step,
            "query": user_query,
            "action_type": "MAX_ITERATIONS_REACHED",
            "output": warning_message,
            "latency_ms": 0
        })

    return trace_logs


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":

    print(
        "=========================================================="
    )

    print(
        "🏦 AI LOAN ADVISORY AGENT"
    )

    print(
        "CHATBOT BASELINE VS REACT AGENT"
    )

    print(
        "=========================================================="
    )

    # --------------------------------------------------------------------------
    # KHỞI TẠO LLM PROVIDER
    # --------------------------------------------------------------------------

    provider = get_llm_provider()

    # --------------------------------------------------------------------------
    # KHỞI TẠO MCP SERVER
    #
    # Nếu bạn chưa đổi tên class MCPAcademicServer
    # thì cứ giữ nguyên dòng này.
    # --------------------------------------------------------------------------

    mcp_server = MCPAcademicServer()

    print(
        f"🔌 LLM Provider: "
        f"{provider.__class__.__name__}"
    )

    print(
        f"🌐 MCP Server: "
        f"{mcp_server.server_name}\n"
    )

    # --------------------------------------------------------------------------
    # LOAD TEST CASES
    # --------------------------------------------------------------------------

    tests = load_test_cases()

    print(
        f"✅ Đã tải thành công "
        f"{len(tests)} Test Cases thử nghiệm.\n"
    )

    # ==========================================================================
    # INTERACTIVE MODE
    # ==========================================================================

    if "--interactive" in sys.argv:

        print(
            "🎮 [INTERACTIVE MODE] "
            "Trò chuyện trực tiếp với Loan Advisory ReAct Agent:"
        )

        print(
            "\n💡 Gợi ý câu hỏi thử nghiệm:"
        )

        print(
            "   1. Tra cứu khoản vay:"
        )

        print(
            "      'Tôi muốn vay 500 triệu mua ô tô. "
            "Có sản phẩm nào phù hợp?'"
        )

        print(
            "\n   2. Đặt lịch tư vấn:"
        )

        print(
            "      'Tôi là Nguyễn Văn An, "
            "số điện thoại 0901234567. "
            "Đặt lịch tư vấn vay mua ô tô "
            "lúc 14:00 ngày 20/09/2026.'"
        )

        print(
            "\n   3. ReAct đa bước:"
        )

        print(
            "      'Tôi muốn vay 500 triệu mua ô tô. "
            "Hãy tìm sản phẩm phù hợp. "
            "Nếu có sản phẩm phù hợp thì đặt lịch tư vấn "
            "cho tôi lúc 15:00 ngày 21/09/2026. "
            "Tên tôi là Nguyễn Văn An, "
            "số điện thoại 0901234567.'"
        )

        print(
            "\n   4. Edge case:"
        )

        print(
            "      'Hãy tra cứu sản phẩm vay "
            "có mã LOAN-999999.'"
        )

        print(
            "\n   - Gõ 'exit' hoặc 'quit' để kết thúc.\n"
        )

        while True:

            try:

                user_input = input(
                    "👤 Khách hàng hỏi: "
                ).strip()

                if (
                    not user_input
                    or user_input.lower()
                    in ["exit", "quit"]
                ):

                    print(
                        "👋 Tạm biệt! "
                        "Kết thúc phiên trò chuyện."
                    )

                    break

                logs = run_react_agent(
                    user_input,
                    provider,
                    mcp_server
                )

                save_waterfall_trace(
                    logs
                )

            except (
                KeyboardInterrupt,
                EOFError
            ):

                print(
                    "\n👋 Đã thoát phiên tương tác."
                )

                break

    # ==========================================================================
    # TEST SUITE MODE
    # ==========================================================================

    elif "--all" in sys.argv:

        print(
            "🚀 [TEST SUITE MODE] "
            f"Kiểm tra {len(tests)} Test Cases:"
        )

        completed_count = 0
        todo_count = 0
        all_traces = []

        for tc in tests:

            print(
                "\n=================================================="
            )

            print(
                f"🧪 [{tc['id']}] "
                f"Loại test: {tc['type']} "
                f"(Độ phức tạp: {tc['complexity']})"
            )

            print(
                f"📌 Kỳ vọng: "
                f"{tc['expected_behavior']}"
            )

            question = tc.get(
                "question",
                ""
            )

            if question.strip().startswith(
                "TODO"
            ):

                print(
                    "⏸️ [CHƯA KÍCH HOẠT - ĐANG LÀ TODO]:"
                )

                print(
                    f"   {question}"
                )

                print(
                    "   👉 Hãy mở file "
                    "'config/test_cases.json' "
                    "và viết câu hỏi theo đề tài "
                    "tư vấn khoản vay ngân hàng."
                )

                todo_count += 1

            else:

                logs = run_react_agent(
                    question,
                    provider,
                    mcp_server
                )

                all_traces.extend(
                    logs
                )

                completed_count += 1

        print(
            "\n=================================================="
        )

        print(
            f"📊 [KẾT QUẢ TEST SUITE]: "
            f"Đã thực thi "
            f"{completed_count}/{len(tests)} Test Cases "
            f"| {todo_count} Test Cases còn TODO"
        )

        if all_traces:

            save_waterfall_trace(
                all_traces
            )

        print(
            "\n💡 Để trò chuyện trực tiếp:"
        )

        print(
            "   python src/app.py --interactive"
        )

    # ==========================================================================
    # DEFAULT MODE
    # ==========================================================================

    else:

        print(
            "ℹ️ HƯỚNG DẪN SỬ DỤNG:"
        )

        print(
            "  1. Chat trực tiếp:"
        )

        print(
            "     python src/app.py --interactive"
        )

        print(
            "\n  2. Chạy toàn bộ Test Cases:"
        )

        print(
            "     python src/app.py --all\n"
        )

        # ----------------------------------------------------------------------
        # DEMO TEST CASE
        # ----------------------------------------------------------------------

        if len(tests) > 1:

            sample_query = tests[1].get(
                "question",
                ""
            )

            print(
                "--- 🏁 DEMO CHẠY THỬ TEST CASE MẪU ---"
            )

            if sample_query.strip().startswith(
                "TODO"
            ):

                print(
                    "⚠️ Test Case mẫu vẫn đang là TODO."
                )

                print(
                    "👉 Hãy chỉnh "
                    "'config/test_cases.json' "
                    "trước khi chạy."
                )

            else:

                logs = run_react_agent(
                    sample_query,
                    provider,
                    mcp_server
                )

                save_waterfall_trace(
                    logs
                )

        print(
            "\n💡 Gợi ý:"
        )

        print(
            "   python src/app.py --interactive"
        )

        print(
            "   python src/app.py --all"
        )
"""
🚀 CORE AGENT APPLICATION

Đề tài:
TRỢ LÝ AI TƯ VẤN KHOẢN VAY NGÂN HÀNG

So sánh:
- Chatbot Baseline (không có Tool)
- ReAct Agent kết nối MCP Server

ReAct Flow:
Thought -> Action -> Observation -> Thought -> ... -> Final Answer
"""

import json
import os
import sys
import time

from dotenv import load_dotenv


# ==============================================================================
# PATH / ENCODING SETUP
# ==============================================================================

sys.path.append(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(
            encoding="utf-8"
        )
    except Exception:
        pass


# ==============================================================================
# IMPORT PROJECT MODULES
# ==============================================================================

from mcp_server import MCPBankingServer

from prompts import (
    CHATBOT_BASELINE_PROMPT,
    REACT_AGENT_SYSTEM_PROMPT,
    MAX_ITERATIONS
)

from providers import get_llm_provider


# ==============================================================================
# LOAD ENVIRONMENT VARIABLES
# ==============================================================================

load_dotenv()


# ==============================================================================
# LOAD TEST CASES
# ==============================================================================

def load_test_cases():
    """
    Tải danh sách Test Cases từ:

    config/test_cases.json

    Nếu chưa tồn tại thì sử dụng:

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
                "và chỉnh sửa theo đề tài "
                "tư vấn khoản vay ngân hàng.\n"
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
    Ghi Waterfall Trace Log ra file:

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

    - Chỉ sử dụng LLM.
    - Không có quyền gọi Tool.
    - Không truy cập dữ liệu khoản vay thời gian thực.
    - Không thể đặt lịch tư vấn.
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
    mcp_server: MCPBankingServer
) -> list:
    """
    REACT AGENT LOOP

    Luồng xử lý:

    Thought
        ↓
    Action
        ↓
    Observation
        ↓
    Thought
        ↓
    Action
        ↓
    Observation
        ↓
    Final Answer

    Agent có thể sử dụng:

    1. loan_information_lookup
       Tra cứu thông tin sản phẩm vay.

    2. loan_consultation_booking
       Đặt lịch tư vấn với chuyên viên tín dụng.

    Observation sau mỗi Tool Call sẽ được đưa trở lại LLM
    để quyết định bước tiếp theo.

    Trả về:
        list Waterfall Trace Logs.
    """

    print(
        f"\n🤖 [BANKING REACT AGENT] "
        f"Câu hỏi: {user_query}"
    )

    step = 0

    trace_logs = []

    # Danh sách Tool schemas do MCP Server cung cấp
    tools_list = mcp_server.list_tools()

    # Context ban đầu
    current_context = user_query

    # Lưu lịch sử các tool đã gọi
    executed_actions = []

    # ==========================================================================
    # REACT LOOP
    # ==========================================================================

    while step < MAX_ITERATIONS:

        step += 1

        step_start_time = time.time()

        print(
            f"\n--- 🔄 ReAct Loop "
            f"(Step {step}/{MAX_ITERATIONS}) ---"
        )

        # ======================================================================
        # GỌI LLM VỚI NATIVE TOOL CALLING
        # ======================================================================

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

        response_type = llm_response.get(
            "type"
        )

        # ======================================================================
        # CASE 1:
        # LLM TRẢ FINAL ANSWER
        # ======================================================================

        if response_type == "text":

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

        # ======================================================================
        # CASE 2:
        # LLM YÊU CẦU GỌI TOOL
        # ======================================================================

        elif response_type == "tool_call":

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

            # ------------------------------------------------------------------
            # CHỐNG LẶP CÙNG TOOL CALL
            # ------------------------------------------------------------------

            action_signature = json.dumps(
                {
                    "tool_name": tool_name,
                    "arguments": arguments
                },
                ensure_ascii=False,
                sort_keys=True
            )

            if action_signature in executed_actions:

                print(
                    "⚠️ [REACT WARNING]: "
                    "Agent đang cố gọi lại cùng một Tool "
                    "với cùng tham số."
                )

                current_context += (
                    "\n\n"
                    "LƯU Ý HỆ THỐNG:\n"
                    "Bạn đã gọi Tool này với cùng tham số "
                    "và đã nhận Observation trước đó. "
                    "KHÔNG gọi lại cùng Tool. "
                    "Hãy sử dụng Observation đã có để "
                    "trả Final Answer hoặc quyết định "
                    "một hành động khác."
                )

                continue

            executed_actions.append(
                action_signature
            )

            # ------------------------------------------------------------------
            # THỰC THI TOOL QUA MCP SERVER
            # ------------------------------------------------------------------

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

            # ------------------------------------------------------------------
            # GHI WATERFALL TRACE
            # ------------------------------------------------------------------

            trace_logs.append({
                "step": step,
                "query": user_query,
                "action_type": "TOOL_EXECUTION",
                "tool_name": tool_name,
                "arguments": arguments,
                "observation": obs_data,
                "latency_ms": latency_ms
            })

            # ------------------------------------------------------------------
            # ĐƯA OBSERVATION TRỞ LẠI CHO LLM
            #
            # KHÔNG BREAK.
            #
            # LLM phải quyết định:
            #
            # - gọi tool tiếp theo
            # - hoặc trả Final Answer
            # ------------------------------------------------------------------

            current_context += (
                "\n\n"
                "===== REACT HISTORY =====\n"
                f"Action: {tool_name}\n"
                f"Arguments: "
                f"{json.dumps(arguments, ensure_ascii=False)}\n"
                f"Observation: {obs_str}\n"
                "=========================\n\n"
                "Hãy tiếp tục xử lý yêu cầu ban đầu dựa trên "
                "Observation vừa nhận được.\n"
                "\n"
                "QUY TẮC:\n"
                "- Không gọi lại cùng Tool với cùng tham số nếu "
                "Observation đã có.\n"
                "- Nếu cần một Tool khác, hãy gọi Tool phù hợp.\n"
                "- Nếu Observation trả SUCCESS và đã đủ dữ liệu, "
                "hãy trả Final Answer.\n"
                "- Nếu Observation trả NOT_FOUND, hãy thông báo "
                "không tìm thấy dữ liệu và không bịa thông tin.\n"
                "- Nếu yêu cầu là đa bước và bước tiếp theo phụ thuộc "
                "Observation này, hãy thực hiện bước tiếp theo."
            )

        # ======================================================================
        # RESPONSE TYPE KHÔNG HỢP LỆ
        # ======================================================================

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
                "output": (
                    "Invalid LLM response type"
                ),
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
        "🏦 BANKING LOAN ADVISORY AGENT"
    )

    print(
        "CHATBOT BASELINE VS REACT AGENT"
    )

    print(
        "=========================================================="
    )

    # ==========================================================================
    # KHỞI TẠO LLM PROVIDER
    # ==========================================================================

    provider = get_llm_provider()

    # ==========================================================================
    # KHỞI TẠO MCP BANKING SERVER
    # ==========================================================================

    mcp_server = MCPBankingServer()

    print(
        f"🔌 LLM Provider: "
        f"{provider.__class__.__name__}"
    )

    print(
        f"🌐 MCP Server: "
        f"{mcp_server.server_name}\n"
    )

    # ==========================================================================
    # LOAD TEST CASES
    # ==========================================================================

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
            "Trò chuyện trực tiếp với "
            "Banking Loan ReAct Agent:"
        )

        print(
            "\n💡 Gợi ý câu hỏi thử nghiệm:"
        )

        # ----------------------------------------------------------------------
        # EXAMPLE 1
        # ----------------------------------------------------------------------

        print(
            "\n1️⃣ Câu hỏi chung:"
        )

        print(
            "   'Ngân hàng hiện có những loại "
            "khoản vay phổ biến nào?'"
        )

        # ----------------------------------------------------------------------
        # EXAMPLE 2
        # ----------------------------------------------------------------------

        print(
            "\n2️⃣ Tra cứu khoản vay:"
        )

        print(
            "   'Tôi muốn vay 500 triệu mua ô tô, "
            "thu nhập 25 triệu/tháng. "
            "Hãy tra cứu sản phẩm phù hợp.'"
        )

        # ----------------------------------------------------------------------
        # EXAMPLE 3
        # ----------------------------------------------------------------------

        print(
            "\n3️⃣ Đặt lịch tư vấn:"
        )

        print(
            "   'Tôi là Nguyễn Văn An, "
            "số điện thoại 0901234567. "
            "Hãy đặt lịch tư vấn vay mua ô tô "
            "lúc 14:00 ngày 20/09/2026.'"
        )

        # ----------------------------------------------------------------------
        # EXAMPLE 4
        # ----------------------------------------------------------------------

        print(
            "\n4️⃣ ReAct đa bước:"
        )

        print(
            "   'Tôi muốn vay 500 triệu mua ô tô, "
            "thu nhập 25 triệu/tháng. "
            "Hãy tìm sản phẩm phù hợp. "
            "Nếu đáp ứng điều kiện sơ bộ thì "
            "đặt lịch tư vấn cho tôi lúc "
            "15:00 ngày 21/09/2026. "
            "Tôi tên Nguyễn Văn An, "
            "số điện thoại 0901234567.'"
        )

        # ----------------------------------------------------------------------
        # EXAMPLE 5
        # ----------------------------------------------------------------------

        print(
            "\n5️⃣ Edge Case:"
        )

        print(
            "   'Hãy tra cứu sản phẩm vay "
            "loại education_loan.'"
        )

        print(
            "\nGõ 'exit' hoặc 'quit' "
            "để kết thúc.\n"
        )

        # ----------------------------------------------------------------------
        # INTERACTIVE LOOP
        # ----------------------------------------------------------------------

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
                f"(Độ phức tạp: "
                f"{tc['complexity']})"
            )

            print(
                f"📌 Kỳ vọng: "
                f"{tc['expected_behavior']}"
            )

            question = tc.get(
                "question",
                ""
            )

            # ------------------------------------------------------------------
            # TEST CASE CHƯA HOÀN THIỆN
            # ------------------------------------------------------------------

            if question.strip().startswith(
                "TODO"
            ):

                print(
                    "⏸️ [CHƯA KÍCH HOẠT - "
                    "ĐANG LÀ TODO]:"
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

            # ------------------------------------------------------------------
            # CHẠY TEST CASE
            # ------------------------------------------------------------------

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

        # ----------------------------------------------------------------------
        # KẾT QUẢ
        # ----------------------------------------------------------------------

        print(
            "\n=================================================="
        )

        print(
            f"📊 [KẾT QUẢ TEST SUITE]: "
            f"Đã thực thi "
            f"{completed_count}/{len(tests)} "
            f"Test Cases | "
            f"{todo_count} Test Cases còn TODO"
        )

        # ----------------------------------------------------------------------
        # SAVE TRACE
        # ----------------------------------------------------------------------

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
            "\n1. Chat trực tiếp:"
        )

        print(
            "   python src/app.py --interactive"
        )

        print(
            "\n2. Chạy toàn bộ Test Cases:"
        )

        print(
            "   python src/app.py --all\n"
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
                "--- 🏁 DEMO CHẠY THỬ "
                "TEST CASE MẪU ---"
            )

            if sample_query.strip().startswith(
                "TODO"
            ):

                print(
                    "⚠️ Test Case mẫu "
                    "vẫn đang là TODO."
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
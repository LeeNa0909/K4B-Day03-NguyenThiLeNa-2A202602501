"""
🔌 MULTI-PROVIDER LLM ADAPTER

Google Gemini, OpenAI & Offline Mock

Đề tài:
Trợ lý AI tư vấn khoản vay ngân hàng.

Hỗ trợ:
- Text generation
- Native Tool Calling
- ReAct Agent
- Gemini API
- OpenAI API
- Offline Mock Provider
"""

import os
import sys
import json
import re

from typing import Dict, Any, List
from dotenv import load_dotenv


# ==============================================================================
# ENCODING
# ==============================================================================

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ==============================================================================
# LOAD ENVIRONMENT VARIABLES
# ==============================================================================

load_dotenv()


# ==============================================================================
# BASE PROVIDER
# ==============================================================================

class BaseLLMProvider:
    """
    Interface cơ sở cho các LLM Provider
    hỗ trợ Native Tool Calling.
    """

    def generate(
        self,
        prompt: str,
        system_prompt: str = ""
    ) -> str:
        raise NotImplementedError

    def generate_with_tools(
        self,
        prompt: str,
        tools_schema: List[Dict[str, Any]],
        system_prompt: str = ""
    ) -> Dict[str, Any]:
        raise NotImplementedError


# ==============================================================================
# MOCK OFFLINE PROVIDER
# ==============================================================================

class MockOfflineProvider(BaseLLMProvider):
    """
    Offline Mock Provider.

    Chỉ dùng để kiểm tra luồng chương trình khi chưa có API Key.

    LƯU Ý:
    Bài nghiệm thu chính thức phải sử dụng Gemini/OpenAI API thật.
    """

    def __init__(self):
        self.model_name = "Offline-Mock-Banking-Loan-Agent-2026"


    # ==========================================================================
    # CHATBOT BASELINE
    # ==========================================================================

    def generate(
        self,
        prompt: str,
        system_prompt: str = ""
    ) -> str:

        return (
            "[Mock Chatbot Response]: "
            "Tôi có thể cung cấp thông tin chung về các sản phẩm vay ngân hàng. "
            "Tuy nhiên, ở chế độ Chatbot Baseline tôi không có quyền truy cập "
            "cơ sở dữ liệu sản phẩm vay theo thời gian thực hoặc đặt lịch "
            "với chuyên viên tín dụng."
        )


    # ==========================================================================
    # HELPER FUNCTIONS
    # ==========================================================================

    def _detect_loan_type(
        self,
        prompt_lower: str
    ) -> str:

        if any(
            keyword in prompt_lower
            for keyword in [
                "ô tô",
                "oto",
                "xe hơi",
                "mua xe",
                "car loan",
                "car_loan"
            ]
        ):
            return "car_loan"

        if any(
            keyword in prompt_lower
            for keyword in [
                "mua nhà",
                "vay nhà",
                "nhà ở",
                "home loan",
                "home_loan"
            ]
        ):
            return "home_loan"

        if any(
            keyword in prompt_lower
            for keyword in [
                "tiêu dùng",
                "tín chấp",
                "cá nhân",
                "personal loan",
                "personal_loan"
            ]
        ):
            return "personal_loan"

        if "education_loan" in prompt_lower:
            return "education_loan"

        return "personal_loan"


    def _extract_amount(
        self,
        prompt_lower: str
    ):

        match = re.search(
            r"(\d+(?:[.,]\d+)?)\s*(triệu|tr)\b",
            prompt_lower
        )

        if match:
            value = float(
                match.group(1).replace(",", ".")
            )

            return int(
                value * 1_000_000
            )

        match = re.search(
            r"(\d+(?:[.,]\d+)?)\s*tỷ\b",
            prompt_lower
        )

        if match:
            value = float(
                match.group(1).replace(",", ".")
            )

            return int(
                value * 1_000_000_000
            )

        return None


    def _extract_monthly_income(
        self,
        prompt_lower: str
    ):

        patterns = [
            r"thu nhập(?: của tôi)?(?: là)?\s*(\d+(?:[.,]\d+)?)\s*(triệu|tr)",
            r"lương(?: của tôi)?(?: là)?\s*(\d+(?:[.,]\d+)?)\s*(triệu|tr)"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                prompt_lower
            )

            if match:
                value = float(
                    match.group(1).replace(",", ".")
                )

                return int(
                    value * 1_000_000
                )

        return None


    def _extract_phone(
        self,
        prompt: str
    ):

        match = re.search(
            r"\b0\d{9}\b",
            prompt
        )

        if match:
            return match.group(0)

        return None


    def _extract_customer_name(
        self,
        prompt: str
    ):

        patterns = [
            r"(?:tôi tên(?: là)?|tên tôi là|tôi là)\s+"
            r"([A-Za-zÀ-ỹĐđ\s]+?)(?=,|\.|\n|số điện thoại|$)"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                prompt,
                flags=re.IGNORECASE
            )

            if match:
                return match.group(1).strip()

        return None


    def _extract_datetime(
        self,
        prompt: str
    ):

        match = re.search(
            r"(\d{1,2}:\d{2})\s*(?:ngày)?\s*"
            r"(\d{1,2}/\d{1,2}/\d{4})",
            prompt,
            flags=re.IGNORECASE
        )

        if match:
            return (
                f"{match.group(1)} "
                f"{match.group(2)}"
            )

        return None


    # ==========================================================================
    # MOCK NATIVE TOOL CALLING
    # ==========================================================================

    def generate_with_tools(
        self,
        prompt: str,
        tools_schema: List[Dict[str, Any]],
        system_prompt: str = ""
    ) -> Dict[str, Any]:

        prompt_lower = prompt.lower()

        loan_type = self._detect_loan_type(
            prompt_lower
        )

        loan_amount = self._extract_amount(
            prompt_lower
        )

        monthly_income = self._extract_monthly_income(
            prompt_lower
        )

        customer_name = self._extract_customer_name(
            prompt
        )

        phone_number = self._extract_phone(
            prompt
        )

        datetime_str = self._extract_datetime(
            prompt
        )

        has_booking_intent = any(
            keyword in prompt_lower
            for keyword in [
                "đặt lịch",
                "dat lich",
                "hẹn tư vấn",
                "hen tu van",
                "đặt hẹn"
            ]
        )

        has_lookup_intent = any(
            keyword in prompt_lower
            for keyword in [
                "tra cứu",
                "tra cuu",
                "sản phẩm vay",
                "khoản vay",
                "vay",
                "lãi suất",
                "lai suat",
                "hạn mức",
                "han muc",
                "điều kiện",
                "dieu kien"
            ]
        )

        # ======================================================================
        # 1. ĐÃ ĐẶT LỊCH THÀNH CÔNG -> FINAL ANSWER
        # ======================================================================

        if (
            "loan_consultation_booking"
            in prompt_lower
            and '"status": "success"'
            in prompt_lower
            and "booking_id"
            in prompt_lower
        ):

            return {
                "type": "text",
                "content": (
                    "[Mock Agent Response]: "
                    "Lịch tư vấn khoản vay đã được đặt thành công. "
                    "Thông tin chi tiết được lấy từ kết quả của hệ thống."
                ),
                "thought": (
                    "Observation xác nhận việc đặt lịch thành công. "
                    "Đã đủ thông tin để đưa ra Final Answer."
                )
            }


        # ======================================================================
        # 2. LOOKUP NOT_FOUND -> FINAL ANSWER
        # ======================================================================

        if (
            "loan_information_lookup"
            in prompt_lower
            and '"status": "not_found"'
            in prompt_lower
        ):

            return {
                "type": "text",
                "content": (
                    "[Mock Agent Response]: "
                    "Không tìm thấy sản phẩm vay phù hợp trong hệ thống. "
                    "Tôi không tự tạo lãi suất, hạn mức hoặc thông tin sản phẩm."
                ),
                "thought": (
                    "Tool trả về NOT_FOUND nên phải thông báo chính xác "
                    "và không được bịa dữ liệu."
                )
            }


        # ======================================================================
        # 3. LOOKUP SUCCESS + YÊU CẦU ĐẶT LỊCH
        #    -> CALL BOOKING TOOL
        # ======================================================================

        if (
            "loan_information_lookup"
            in prompt_lower
            and '"status": "success"'
            in prompt_lower
            and has_booking_intent
            and "loan_consultation_booking"
            not in prompt_lower
        ):

            # Nếu thiếu thông tin đặt lịch thì trả text yêu cầu bổ sung
            if not customer_name:
                return {
                    "type": "text",
                    "content": (
                        "Vui lòng cung cấp họ và tên để tôi có thể "
                        "đặt lịch tư vấn khoản vay."
                    ),
                    "thought": (
                        "Đã tìm thấy sản phẩm vay nhưng còn thiếu tên khách hàng."
                    )
                }

            if not phone_number:
                return {
                    "type": "text",
                    "content": (
                        "Vui lòng cung cấp số điện thoại để tôi có thể "
                        "đặt lịch tư vấn."
                    ),
                    "thought": (
                        "Đã tìm thấy sản phẩm vay nhưng còn thiếu số điện thoại."
                    )
                }

            if not datetime_str:
                return {
                    "type": "text",
                    "content": (
                        "Vui lòng cung cấp ngày và giờ bạn muốn "
                        "đặt lịch tư vấn."
                    ),
                    "thought": (
                        "Đã tìm thấy sản phẩm vay nhưng còn thiếu thời gian hẹn."
                    )
                }

            return {
                "type": "tool_call",
                "tool_name": "loan_consultation_booking",
                "arguments": {
                    "customer_name": customer_name,
                    "phone_number": phone_number,
                    "datetime_str": datetime_str,
                    "loan_type": loan_type
                },
                "thought": (
                    "Kết quả tra cứu thành công và khách hàng yêu cầu đặt lịch. "
                    "Tôi sẽ gọi loan_consultation_booking."
                )
            }


        # ======================================================================
        # 4. LOOKUP SUCCESS NHƯNG KHÔNG CẦN BOOKING
        #    -> FINAL ANSWER
        # ======================================================================

        if (
            "loan_information_lookup"
            in prompt_lower
            and '"status": "success"'
            in prompt_lower
            and not has_booking_intent
        ):

            return {
                "type": "text",
                "content": (
                    "[Mock Agent Response]: "
                    "Đã tra cứu sản phẩm vay thành công. "
                    "Tôi sẽ sử dụng chính xác thông tin từ Observation "
                    "để tư vấn cho khách hàng."
                ),
                "thought": (
                    "Observation đã cung cấp đủ thông tin sản phẩm vay. "
                    "Không cần gọi thêm Tool."
                )
            }


        # ======================================================================
        # 5. YÊU CẦU ĐẶT LỊCH TRỰC TIẾP
        # ======================================================================

        if (
            has_booking_intent
            and not has_lookup_intent
        ):

            if not customer_name:
                return {
                    "type": "text",
                    "content": (
                        "Vui lòng cung cấp họ và tên của bạn "
                        "để tôi đặt lịch tư vấn."
                    ),
                    "thought": (
                        "Khách hàng muốn đặt lịch nhưng chưa cung cấp tên."
                    )
                }

            if not phone_number:
                return {
                    "type": "text",
                    "content": (
                        "Vui lòng cung cấp số điện thoại "
                        "để tôi đặt lịch tư vấn."
                    ),
                    "thought": (
                        "Khách hàng muốn đặt lịch nhưng chưa cung cấp số điện thoại."
                    )
                }

            if not datetime_str:
                return {
                    "type": "text",
                    "content": (
                        "Vui lòng cho biết ngày và giờ "
                        "bạn muốn đặt lịch tư vấn."
                    ),
                    "thought": (
                        "Khách hàng muốn đặt lịch nhưng chưa cung cấp thời gian."
                    )
                }

            return {
                "type": "tool_call",
                "tool_name": "loan_consultation_booking",
                "arguments": {
                    "customer_name": customer_name,
                    "phone_number": phone_number,
                    "datetime_str": datetime_str,
                    "loan_type": loan_type
                },
                "thought": (
                    "Khách hàng yêu cầu đặt lịch tư vấn khoản vay "
                    "và đã cung cấp đủ thông tin."
                )
            }


        # ======================================================================
        # 6. YÊU CẦU TRA CỨU
        # ======================================================================

        if has_lookup_intent:

            arguments = {
                "loan_type": loan_type
            }

            if loan_amount is not None:
                arguments["loan_amount"] = (
                    loan_amount
                )

            if monthly_income is not None:
                arguments["monthly_income"] = (
                    monthly_income
                )

            return {
                "type": "tool_call",
                "tool_name": "loan_information_lookup",
                "arguments": arguments,
                "thought": (
                    "Khách hàng yêu cầu thông tin cụ thể về sản phẩm vay. "
                    "Tôi cần gọi loan_information_lookup."
                )
            }


        # ======================================================================
        # 7. CÂU HỎI CHUNG
        # ======================================================================

        return {
            "type": "text",
            "content": (
                "[Mock Agent Response]: "
                "Tôi có thể hỗ trợ tra cứu các sản phẩm vay như "
                "vay mua ô tô, vay mua nhà và vay tiêu dùng cá nhân, "
                "đồng thời hỗ trợ đặt lịch tư vấn với chuyên viên tín dụng."
            ),
            "thought": (
                "Đây là câu hỏi chung, chưa yêu cầu dữ liệu cụ thể "
                "nên không cần gọi Tool."
            )
        }


# ==============================================================================
# GEMINI PROVIDER
# ==============================================================================

class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini Provider
    sử dụng Native Tool Calling với Google GenAI SDK.
    """

    def __init__(
        self,
        api_key: str = None,
        model: str = None
    ):

        self.api_key = (
            api_key
            or os.getenv("GEMINI_API_KEY")
        )

        self.model_name = (
            model
            or os.getenv("LLM_MODEL")
            or "gemini-2.5-flash"
        )


    # ==========================================================================
    # GEMINI TEXT GENERATION
    # ==========================================================================

    def generate(
        self,
        prompt: str,
        system_prompt: str = ""
    ) -> str:

        if (
            not self.api_key
            or self.api_key
            == "your_gemini_api_key_here"
        ):

            return (
                "[Gemini Error]: "
                "Chưa cấu hình GEMINI_API_KEY trong file .env!"
            )

        try:

            from google import genai

            client = genai.Client(
                api_key=self.api_key
            )

            contents = (
                f"{system_prompt}\n\n{prompt}"
                if system_prompt
                else prompt
            )

            response = client.models.generate_content(
                model=self.model_name,
                contents=contents
            )

            return response.text or ""

        except Exception as e:

            return (
                f"[Gemini Exception]: "
                f"{str(e)}"
            )


    # ==========================================================================
    # GEMINI NATIVE TOOL CALLING
    # ==========================================================================

    def generate_with_tools(
        self,
        prompt: str,
        tools_schema: List[Dict[str, Any]],
        system_prompt: str = ""
    ) -> Dict[str, Any]:

        if (
            not self.api_key
            or self.api_key
            == "your_gemini_api_key_here"
        ):

            print(
                "ℹ️ [Gemini Provider]: "
                "Chưa tìm thấy GEMINI_API_KEY hợp lệ. "
                "Chuyển sang Mock Offline."
            )

            return (
                MockOfflineProvider()
                .generate_with_tools(
                    prompt,
                    tools_schema,
                    system_prompt
                )
            )

        try:

            from google import genai
            from google.genai import types

            client = genai.Client(
                api_key=self.api_key
            )

            # ------------------------------------------------------------------
            # CONVERT TOOL SCHEMA
            # ------------------------------------------------------------------

            function_declarations = []

            for tool in tools_schema:

                if (
                    not tool.get("name")
                    or not tool.get("parameters")
                ):
                    continue

                function_declarations.append({
                    "name": tool["name"],
                    "description": tool.get(
                        "description",
                        ""
                    ),
                    "parameters": tool.get(
                        "parameters",
                        {}
                    )
                })

            # ------------------------------------------------------------------
            # CONFIG
            # ------------------------------------------------------------------

            config = (
                types.GenerateContentConfig(
                    system_instruction=(
                        system_prompt
                        if system_prompt
                        else None
                    ),
                    tools=[
                        {
                            "function_declarations":
                                function_declarations
                        }
                    ]
                    if function_declarations
                    else None,
                    temperature=0.2
                )
            )

            # ------------------------------------------------------------------
            # API CALL
            # ------------------------------------------------------------------

            response = (
                client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )
            )

            # ------------------------------------------------------------------
            # TOOL CALL
            # ------------------------------------------------------------------

            if response.function_calls:

                call = (
                    response.function_calls[0]
                )

                args = (
                    dict(call.args)
                    if hasattr(
                        call,
                        "args"
                    )
                    and call.args
                    else {}
                )

                return {
                    "type": "tool_call",
                    "tool_name": call.name,
                    "arguments": args,
                    "thought": (
                        f"Gemini quyết định gọi công cụ "
                        f"'{call.name}' với tham số: "
                        f"{json.dumps(args, ensure_ascii=False)}"
                    )
                }

            # ------------------------------------------------------------------
            # TEXT RESPONSE
            # ------------------------------------------------------------------

            return {
                "type": "text",
                "content": (
                    response.text
                    or ""
                ),
                "thought": (
                    "Gemini đã có đủ thông tin và "
                    "phản hồi trực tiếp bằng văn bản."
                )
            }

        except Exception as e:

            print(
                f"⚠️ [Gemini API Warning]: "
                f"Không thể kết nối Live API: "
                f"{str(e)}"
            )

            print(
                "⚠️ Tự động fallback "
                "về Mock Offline."
            )

            return (
                MockOfflineProvider()
                .generate_with_tools(
                    prompt,
                    tools_schema,
                    system_prompt
                )
            )


# ==============================================================================
# OPENAI PROVIDER
# ==============================================================================

class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI Provider
    sử dụng Native Function / Tool Calling.
    """

    def __init__(
        self,
        api_key: str = None,
        model: str = None
    ):

        self.api_key = (
            api_key
            or os.getenv(
                "OPENAI_API_KEY"
            )
        )

        self.model_name = (
            model
            or os.getenv(
                "LLM_MODEL"
            )
            or "gpt-4o-mini"
        )


    # ==========================================================================
    # OPENAI TEXT GENERATION
    # ==========================================================================

    def generate(
        self,
        prompt: str,
        system_prompt: str = ""
    ) -> str:

        if (
            not self.api_key
            or self.api_key
            == "your_openai_api_key_here"
        ):

            return (
                "[OpenAI Error]: "
                "Chưa cấu hình OPENAI_API_KEY trong file .env!"
            )

        try:

            from openai import OpenAI

            client = OpenAI(
                api_key=self.api_key
            )

            messages = []

            if system_prompt:

                messages.append({
                    "role": "system",
                    "content": (
                        system_prompt
                    )
                })

            messages.append({
                "role": "user",
                "content": prompt
            })

            response = (
                client
                .chat
                .completions
                .create(
                    model=self.model_name,
                    messages=messages
                )
            )

            return (
                response
                .choices[0]
                .message
                .content
                or ""
            )

        except Exception as e:

            return (
                f"[OpenAI Exception]: "
                f"{str(e)}"
            )


    # ==========================================================================
    # OPENAI NATIVE TOOL CALLING
    # ==========================================================================

    def generate_with_tools(
        self,
        prompt: str,
        tools_schema: List[Dict[str, Any]],
        system_prompt: str = ""
    ) -> Dict[str, Any]:

        if (
            not self.api_key
            or self.api_key
            == "your_openai_api_key_here"
        ):

            print(
                "ℹ️ [OpenAI Provider]: "
                "Chưa tìm thấy OPENAI_API_KEY hợp lệ. "
                "Chuyển sang Mock Offline."
            )

            return (
                MockOfflineProvider()
                .generate_with_tools(
                    prompt,
                    tools_schema,
                    system_prompt
                )
            )

        try:

            from openai import OpenAI

            client = OpenAI(
                api_key=self.api_key
            )

            # ------------------------------------------------------------------
            # CONVERT TOOL SCHEMA
            # ------------------------------------------------------------------

            tools = []

            for tool in tools_schema:

                if not tool.get("name"):
                    continue

                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool.get(
                            "description",
                            ""
                        ),
                        "parameters": tool.get(
                            "parameters",
                            {}
                        )
                    }
                })

            # ------------------------------------------------------------------
            # MESSAGES
            # ------------------------------------------------------------------

            messages = []

            if system_prompt:

                messages.append({
                    "role": "system",
                    "content": system_prompt
                })

            messages.append({
                "role": "user",
                "content": prompt
            })

            # ------------------------------------------------------------------
            # API CALL
            # ------------------------------------------------------------------

            response = (
                client
                .chat
                .completions
                .create(
                    model=self.model_name,
                    messages=messages,
                    tools=(
                        tools
                        if tools
                        else None
                    ),
                    tool_choice=(
                        "auto"
                        if tools
                        else None
                    )
                )
            )

            msg = (
                response
                .choices[0]
                .message
            )

            # ------------------------------------------------------------------
            # TOOL CALL
            # ------------------------------------------------------------------

            if msg.tool_calls:

                call = (
                    msg.tool_calls[0]
                )

                args = (
                    json.loads(
                        call.function.arguments
                    )
                    if call.function.arguments
                    else {}
                )

                return {
                    "type": "tool_call",
                    "tool_name": (
                        call.function.name
                    ),
                    "arguments": args,
                    "thought": (
                        f"OpenAI quyết định gọi công cụ "
                        f"'{call.function.name}' "
                        f"với tham số: "
                        f"{json.dumps(args, ensure_ascii=False)}"
                    )
                }

            # ------------------------------------------------------------------
            # TEXT RESPONSE
            # ------------------------------------------------------------------

            return {
                "type": "text",
                "content": (
                    msg.content
                    or ""
                ),
                "thought": (
                    "OpenAI đã có đủ thông tin và "
                    "phản hồi trực tiếp bằng văn bản."
                )
            }

        except Exception as e:

            print(
                f"⚠️ [OpenAI API Warning]: "
                f"Không thể kết nối Live API: "
                f"{str(e)}"
            )

            print(
                "⚠️ Tự động fallback "
                "về Mock Offline."
            )

            return (
                MockOfflineProvider()
                .generate_with_tools(
                    prompt,
                    tools_schema,
                    system_prompt
                )
            )


# ==============================================================================
# PROVIDER FACTORY
# ==============================================================================

def get_llm_provider() -> BaseLLMProvider:
    """
    Khởi tạo Provider dựa trên biến môi trường:

    LLM_PROVIDER=gemini
    LLM_PROVIDER=openai
    LLM_PROVIDER=mock
    """

    provider_type = (
        os.getenv(
            "LLM_PROVIDER",
            "gemini"
        )
        .strip()
        .lower()
    )


    # ==========================================================================
    # GEMINI
    # ==========================================================================

    if provider_type == "gemini":

        key = os.getenv(
            "GEMINI_API_KEY"
        )

        if (
            key
            and key
            != "your_gemini_api_key_here"
        ):

            print(
                "✅ [Provider]: "
                "Đang sử dụng Google Gemini Live API."
            )

            return GeminiProvider()

        print(
            "⚠️ [Provider]: "
            "Không tìm thấy GEMINI_API_KEY hợp lệ. "
            "Đang dùng Mock Offline Provider."
        )

        return MockOfflineProvider()


    # ==========================================================================
    # OPENAI
    # ==========================================================================

    elif provider_type == "openai":

        key = os.getenv(
            "OPENAI_API_KEY"
        )

        if (
            key
            and key
            != "your_openai_api_key_here"
        ):

            print(
                "✅ [Provider]: "
                "Đang sử dụng OpenAI Live API."
            )

            return OpenAIProvider()

        print(
            "⚠️ [Provider]: "
            "Không tìm thấy OPENAI_API_KEY hợp lệ. "
            "Đang dùng Mock Offline Provider."
        )

        return MockOfflineProvider()


    # ==========================================================================
    # MOCK
    # ==========================================================================

    elif provider_type == "mock":

        print(
            "ℹ️ [Provider]: "
            "Đang sử dụng Offline Mock Provider."
        )

        return MockOfflineProvider()


    # ==========================================================================
    # UNKNOWN PROVIDER
    # ==========================================================================

    print(
        f"⚠️ [Provider]: "
        f"LLM_PROVIDER='{provider_type}' "
        f"không hợp lệ. "
        f"Fallback sang Mock Offline."
    )

    return MockOfflineProvider()
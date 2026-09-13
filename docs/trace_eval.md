# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Nguyễn Thị Lê Na  
> **Mã Sinh Viên / Mã Học viên:** 2A202602501
> **Chủ đề Lựa chọn:** 
Trợ lý AI tư vấn khoản vay và đặt lịch chuyên viên ngân hàng
---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 4/ 5 | Bài toán có yêu cầu chia nhỏ nhiều bước suy luận nối tiếp nhau không? |
| **2. Tool Interaction** | 4/ 5 | Hệ thống có cần kết nối với MCP Server / Cơ sở dữ liệu bên ngoài không? |
| **3. Dynamic Decision** | 4/ 5 | Bước tiếp theo có phụ thuộc vào kết quả quan sát bước trước không? |
| **4. Long Horizon Goal** | 4/ 5 | Hệ thống có phải giữ mục tiêu xuyên suốt qua nhiều lượt xử lý không? |
| **TỔNG ĐIỂM AGENTIC FIT** | ** 16/ 20** | *Nếu tổng điểm > 12/20: Bài toán rất phù hợp triển khai Agentic System.* |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Dán 1 đoạn trích xuất log tiêu biểu từ file `docs/trace_waterfall.json` sinh ra từ phản hồi LLM API thật:

```json
[
  {
    "step": 1,
    "action_type": "TOOL_EXECUTION",
    "tool_name": "loan_information_lookup",
    "arguments": {
      "loan_type": "car_loan",
      "loan_amount": 500000000,
      "monthly_income": 25000000
    },
    "observation": {
      "status": "SUCCESS",
      "loan_type": "car_loan",
      "loan_amount_check": "ELIGIBLE",
      "income_check": "ELIGIBLE",
      "preliminary_eligibility": "ELIGIBLE"
    },
    "latency_ms": 120.5
  },
  {
    "step": 2,
    "action_type": "TOOL_EXECUTION",
    "tool_name": "loan_consultation_booking",
    "arguments": {
      "customer_name": "Nguyễn Văn An",
      "phone_number": "0901234567",
      "datetime_str": "15:00 21/09/2026",
      "loan_type": "car_loan"
    },
    "observation": {
      "status": "SUCCESS",
      "booking_id": "LOAN-BK-4567-150021092026",
      "customer_name": "Nguyễn Văn An",
      "loan_type": "car_loan",
      "datetime": "15:00 21/09/2026",
      "advisor": "Chuyên viên tín dụng 01"
    },
    "latency_ms": 135.2
  }
]
```

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [ ] Đã điền API Key thật trong `.env` và xác nhận Agent chạy mượt mà trên LLM API thật (Gemini/OpenAI).
- **Tổng số Test Cases đã chạy thành công:** 5/ 5 test cases.
- **Số lượt gọi Tool qua MCP Server chính xác:** 4 lượt.
- **Kết quả đẩy Repo nộp bài:** [x] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!

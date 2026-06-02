# OrderDesk Prompt Engineering Lab

Xây dựng một tác nhân (agent) đặt hàng sử dụng LLM cho một nhà bán lẻ thiết bị điện tử và cải thiện điểm số của tác nhân thông qua kỹ thuật Prompt Engineering.

Trong bài lab này, agent cần có khả năng:

* Hiểu các yêu cầu đặt hàng bằng tiếng Việt hoặc pha trộn nhiều ngôn ngữ.
* Sử dụng các công cụ (tools) theo đúng thứ tự.
* Hỏi lại người dùng khi thiếu thông tin cần thiết trước khi thực hiện hành động.
* Từ chối các yêu cầu không an toàn hoặc vi phạm chính sách.
* Lưu đơn hàng cuối cùng dưới dạng JSON có căn cứ từ kết quả công cụ (grounded JSON).

Mục tiêu chính không chỉ là làm cho chương trình chạy được, mà là cải thiện hành vi của agent bằng cách tối ưu:

* Prompt hệ thống (System Prompt)
* Schema của các công cụ (Tool Schema)
* Các guardrails (cơ chế bảo vệ và ràng buộc)

---

## Những Kỹ Năng Bạn Sẽ Thực Hành

* Viết System Prompt mạnh và rõ ràng hơn.
* Thiết kế Tool Schema dễ hiểu và ít gây nhầm lẫn hơn.
* Buộc agent phải làm rõ thông tin trước khi gọi công cụ.
* Thêm các guardrails để xử lý yêu cầu không an toàn.
* Đảm bảo câu trả lời cuối cùng được căn cứ vào kết quả từ công cụ.
* Gỡ lỗi (debug) các lỗi thông qua tool traces và các artifact đã được lưu.

---

## Cấu Trúc Repository

* `src/`: nơi bạn triển khai lời giải của mình.
* `simple_solution/`: lời giải mẫu cơ bản (baseline yếu).
* `data/products.json`: danh mục sản phẩm.
* `data/graded_cases.json`: các kịch bản dùng để chấm điểm.
* `data/expected_orders/`: các file JSON đơn hàng mong đợi cho các trường hợp cần lưu.
* `grade/scoring.py`: chương trình chấm điểm.
* `guide.md`: hướng dẫn từng bước thực hiện.
* `rubric.md`: tiêu chí chấm điểm.

---

## Quy Trình Làm Việc Được Khuyến Nghị

1. Chạy lời giải baseline trước.
2. Ghi lại điểm số của baseline.
3. Cải thiện mã nguồn trong thư mục `src/`.
4. Chạy bộ chấm điểm trên `src/`.
5. Lặp lại quy trình cho đến khi điểm số vượt rõ rệt so với baseline.

---

## Thiết Lập Môi Trường

Tạo file `.env`:

```bash
GOOGLE_API_KEY=...
LLM_MODEL=gemini-2.5-flash
```

Tùy chọn sử dụng mô hình chạy cục bộ:

```bash
OLLAMA_MODEL=qwen3.5:3b
OLLAMA_BASE_URL=http://localhost:11434
```

---

## Các Lệnh Thực Thi

Chạy baseline:

```bash
python grade/scoring.py --module simple_solution.agent.graph --provider google
```

Chạy lời giải của bạn:

```bash
python grade/scoring.py --module src.agent.graph --provider google
```

Chạy bộ kiểm thử:

```bash
pytest -q
```

---

## Một Bài Nộp Mạnh Cần Làm Được Những Gì?

* Yêu cầu người dùng bổ sung thông tin khi còn thiếu các trường bắt buộc trước khi gọi công cụ.
* Từ chối các yêu cầu không hợp lệ mà không gọi công cụ.
* Tuân thủ đúng trình tự gọi công cụ đối với các đơn hàng hợp lệ.
* Lưu đúng file JSON theo yêu cầu.
* Trả lời ngắn gọn bằng tiếng Việt và dựa trên dữ liệu thực tế từ công cụ.

Trước khi chỉnh sửa mã nguồn trong thư mục `src/`, hãy đọc kỹ file `guide.md`.



guide step to step 

# Hướng Dẫn Thực Hiện (Guide)

## 1. Bắt Đầu Với Baseline

Trước tiên hãy chạy lời giải baseline yếu:

```bash
python grade/scoring.py --module simple_solution.agent.graph --provider google
```

Lệnh này sẽ cho bạn điểm số ban đầu.

Nhiệm vụ của bạn là cải thiện mã nguồn trong thư mục `src/` và đạt điểm cao hơn baseline.

---

## 2. Hiểu Bài Toán

Agent cần xử lý tốt 4 hành vi chính:

* Tạo đơn hàng hợp lệ.
* Hỏi bổ sung khi thiếu thông tin khách hàng.
* Từ chối các yêu cầu vi phạm chính sách.
* Xác nhận đơn hàng dựa trên dữ liệu thực tế sau khi lưu thành công.

Đối với một đơn hàng hợp lệ, thứ tự gọi công cụ mong muốn là:

1. `list_products`
2. `get_product_details`
3. `get_discount`
4. `calculate_order_totals`
5. `save_order`

---

## 3. Những File Cần Tập Trung Chỉnh Sửa

Ưu tiên làm việc trên:

* `src/agent/graph.py`
* `src/utils/data_store.py`

Các tài liệu tham khảo hữu ích:

* `data/graded_cases.json`
* `data/expected_orders/`
* `simple_solution/`

---

## 4. Những Điểm Cần Cải Thiện

### Prompt (System Prompt)

Prompt hệ thống nên quy định rõ các nguyên tắc sau:

* Luôn trả lời bằng tiếng Việt.
* Không tự bịa thông tin về sản phẩm, khuyến mãi, tổng tiền hoặc đường dẫn file.
* Phải yêu cầu bổ sung các thông tin khách hàng còn thiếu trước khi gọi bất kỳ công cụ nào.
* Từ chối các yêu cầu không an toàn mà không gọi công cụ.
* Tuân thủ đúng thứ tự gọi công cụ được yêu cầu.
* Chỉ lưu đơn hàng sau khi quá trình kiểm tra hợp lệ hoàn tất.

---

### Tool Schema

Một Tool Schema tốt giúp giảm đáng kể lỗi của agent.

Nên ưu tiên:

* Tên công cụ rõ ràng.
* Docstring mô tả dễ hiểu.
* Khai báo rõ các tham số bắt buộc.
* Cấu trúc đầu vào phù hợp với luồng xử lý nghiệp vụ.

---

### Guardrails (Ràng Buộc An Toàn)

Agent phải từ chối các yêu cầu có mục đích:

* Bỏ qua kiểm tra tồn kho.
* Ép áp dụng khuyến mãi giả.
* Tạo hóa đơn giả.
* Bỏ qua danh mục sản phẩm hoặc chính sách hệ thống.

---

### Clarification (Làm Rõ Thông Tin)

Trước khi gọi bất kỳ công cụ nào, agent phải có đầy đủ:

* Tên khách hàng.
* Số điện thoại.
* Email.
* Địa chỉ giao hàng.
* Ít nhất một sản phẩm và số lượng tương ứng.

Nếu thiếu bất kỳ thông tin nào, agent phải hỏi lại và dừng xử lý.

---

## 5. Cách Debug

Khi một test case thất bại, hãy kiểm tra:

### Tool Trace

* Mô hình có gọi công cụ quá sớm không?
* Mô hình có gọi sai thứ tự công cụ không?

### Saved JSON

* Có lưu sai dữ liệu không?
* Có lưu đơn hàng trong trường hợp đáng lẽ không được lưu không?

### Final Answer

* Câu trả lời cuối cùng có thực sự dựa trên dữ liệu từ công cụ không?
* Phần yêu cầu bổ sung thông tin, từ chối hoặc xác nhận đơn hàng có ngắn gọn và chính xác không?

---

## 6. Vòng Lặp Cải Thiện

Thực hiện theo quy trình sau:

1. Chạy `simple_solution`.
2. Chạy `src`.
3. Phân tích các trường hợp bị lỗi.
4. Tăng cường và siết chặt System Prompt.
5. Cải thiện Tool Schema.
6. Chạy lại bộ chấm điểm.

Chạy lời giải của bạn bằng lệnh:

```bash
python grade/scoring.py --module src.agent.graph --provider google
```

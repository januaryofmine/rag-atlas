# RAG Atlas Key Features

Sản phẩm = **tìm engineer** từng build hệ thống RAG khớp yêu cầu.

### Input: prefix cố định

- **Prefix cố định (không đổi):** `Engineer who built:`
- User sẽ có search filter theo 2 options (có thể dùng cả hai cùng lúc, xem như 1 bộ search có nhiều cái filter):

**1. Short product description (Input field):** đây là field bắt buộc phải điền

- User gõ mô tả ngắn về product. Ví dụ:
  - _"a customer support assistant over internal company docs"_
  - _"a legal contract review & Q&A tool"_
  - _"a medical literature search assistant"_
  - _"an e-commerce semantic product search"_
- Chỉ phục vụ system **liên quan RAG** (không index toàn bộ GitHub như product Vamo).
- **2. RAG types (select box):** optional field
- User **chọn** từ danh sách category RAG có sẵn (không tự điền).
- Ví dụ option: GraphRAG · Agentic RAG · Self-RAG · Corrective RAG (CRAG) · Hybrid retrieval · Multimodal RAG…

### Search & Matching Logic:

- Hệ thống sẽ search các devs match short product description trước, ra 1 list devs
- Sau đó sẽ filter theo các search params còn lại, ở đây cụ thể là RAG type select box.
- Sau này có thể build bộ search thêm nhiều params hơn như là filter by location, filter by years of exp, ...
- Ở phase này, RAG type filter sẽ soft boost dev khớp RAG type lên cao hơn trong list (thay vì hard filter loại trực tiếp)

About Matching logic:

- Về việc matching logic theo short description):
  - Scoring kết hợp 2 tín hiệu: domain/use-case similarity + đặc tính RAG suy ra từ mô tả.
  - Cân bằng cả hai.
  - Repo/dev điểm tổng cao xếp trên.

### Output: danh sách devs match

Mỗi dev gồm:

1. **GitHub link** của dev
2. **GitHub repos** của dev đó làm, khớp requirement _(= evidence)_
3. _(optional)_ **Programming languages** dev đó thường dùng

### Nguyên tắc:

- **Evidence = repo**: dev xuất hiện vì có repo RAG thật khớp, không phải profile text.
- **Scope RAG only**: chỉ RAG-related, không crawl all topics in GitHub.

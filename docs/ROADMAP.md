# ROADMAP

## v0.1 (hiện tại)
- [x] FE/BE tách bạch (app / src).
- [x] Router online/offline (Gemini vs Ollama).
- [x] UI 2 cột, header/footer, hiệu ứng loading, citations & latency.
- [x] Tài liệu setup/kiến trúc/prompt.

## v0.2
- [ ] Log truy vấn & thống kê latency, tỉ lệ direct-cite.
- [ ] Trang /admin xem health, số unit, index path.
- [ ] Lọc theo nhóm luật (dat_dai, shtt, giao_thong…).

## v0.3
- [ ] Cache retrieval per‑question (LRU).
- [ ] Bộ test E2E: input → citations → answer.
- [ ] i18n labels UI.

## v0.4
- [ ] Ngân hàng câu hỏi benchmark (VN law).
- [ ] Tách worker sinh văn bản (queue) nếu cần scale.

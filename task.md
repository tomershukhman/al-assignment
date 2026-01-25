# Project Tasks

- [x] **Mathpix OCR Integration**
  - [x] Configure Mathpix credentials in `backend/config.py`
  - [x] Implement OCR service in `backend/ocr.py`
  - [x] specific `POST /ocr` endpoint for testing
  - [x] Verify extraction with sample image
- [ ] **Database Setup**
  - [ ] Define SQLModel entities (`Topic`, `Problem`, `Submission`) in `backend/models.py`
  - [ ] Initialize SQLite database
- [ ] **LLM Integration**
  - [ ] Configure Claude credentials
  - [ ] Implement pedagogical validation logic
- [ ] **Submission Pipeline**
  - [ ] Implement `POST /api/submissions`
  - [ ] Integrate OCR -> LLM -> DB flow
- [ ] **Frontend Development**
  - [ ] Setup React/Vite project
  - [ ] Implement Image Upload UI
  - [ ] Display Results

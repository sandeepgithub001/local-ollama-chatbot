# Local Ollama Chatbot - Implementation Plan

## 1. Purpose

This plan describes how to implement the requirements in [SPEC.md](SPEC.md) as a beginner-friendly, local-first Python application. It keeps the work small and demonstrable: first make a working chatbot, then add document-based RAG, then verify reliability and privacy.

## 2. Recommended Technology Stack

| Area | Choice | Purpose |
| --- | --- | --- |
| Language | Python 3.11 or later | Application and RAG logic |
| UI | Streamlit | Local browser-based chat interface and document controls |
| Model runtime | Ollama | Run the chat and embedding models locally |
| Ollama integration | Ollama Python client, behind a small application service | Send chat and embedding requests without coupling UI code to API details |
| Vector store | ChromaDB in persistent local mode | Store and search document chunk embeddings locally |
| Document formats, first release | PDF, Markdown, and plain text | Keep ingestion useful while limiting initial complexity |
| PDF text extraction | pypdf | Extract page text and retain page references |
| Configuration | Environment variables and a local `.env` file | Configure model names, Ollama URL, and limits without hard-coding them |
| Tests | pytest | Test document processing, retrieval, and Ollama service behavior without a live model |

Use an Ollama chat model and an Ollama embedding model as separate configurable settings. For example, `llama3.2` and `nomic-embed-text` may be evaluated locally, but the application must not assume either is installed. Confirm the chosen embedding model is available and use that same model for both indexing document chunks and embedding questions.

## 3. Suggested Project Structure

```text
local-ollama-chatbot/
  app.py
  requirements.txt
  .env.example
  .gitignore
  README.md
  src/
    chatbot/
      config.py
      ollama_service.py
      document_loader.py
      text_chunker.py
      vector_store.py
      rag_service.py
  tests/
    test_document_loader.py
    test_text_chunker.py
    test_rag_service.py
    test_ollama_service.py
  data/
    documents/
    chroma/
```

Keep uploaded documents and the Chroma database under local application data, and exclude them from version control. The exact folder location can be adjusted for the operating system. Do not commit `.env`, documents, chat logs, or generated vector data.

## 4. Implementation Phases

### Phase 0: Environment and project setup

**Work**

- Create a Python virtual environment and install the selected packages.
- Install Ollama separately, start its local service, and pull one chat model plus one embedding model.
- Add configuration for the Ollama base URL, model names, data directory, timeout, and retrieval limits.
- Add `.gitignore` entries for virtual environments, `.env`, uploaded data, and vector-store files.
- Document setup and how to verify Ollama and model availability.

**Completion check**

- The project starts in its virtual environment.
- The configured Ollama endpoint can be reached and both configured models can be selected or checked.

**Spec coverage:** Assumptions, FR-3, FR-4, NFR-1, NFR-4.

### Phase 1: Basic chat without RAG

**Work**

- Build a Streamlit chat page with a transcript, text input, send action, new-chat control, and model/status display.
- Store the active conversation in Streamlit session state; do not persist it between restarts in the first version.
- Put Ollama calls in `ollama_service.py`, not in UI event code.
- Send the current user message and the recent conversation history to Ollama.
- Stream the response if supported by the selected client/API; provide a clear busy state and handle request failures.
- Add a configurable history/context limit and retain the draft if a request fails.

**Completion check**

- A user can chat, ask a follow-up that uses earlier messages, clear the conversation, and recover from Ollama being unavailable.

**Spec coverage:** FR-1 through FR-9, NFR-1 through NFR-6.

### Phase 2: Document ingestion and transformation

**Work**

- Add upload and document-list controls.
- Initially support PDF, Markdown, and plain text; validate type and file size before processing.
- Extract text, preserve PDF page numbers, normalize whitespace, and reject empty or unreadable documents with an actionable message.
- Split extracted text into bounded, slightly overlapping chunks.
- Attach source metadata to each chunk: document identifier/name and page where available.
- Avoid duplicate indexing when the same document is uploaded again, using a content hash or stable document identifier.

**Completion check**

- Each supported document can be processed into inspectable chunks with source metadata, while invalid documents fail safely.

**Spec coverage:** FR-10, FR-11, NFR-3, NFR-4.

### Phase 3: Embeddings and local vector search

**Work**

- Implement a vector-store service that uses persistent local ChromaDB storage.
- Generate chunk embeddings with the configured Ollama embedding model and store vectors, text, and metadata.
- Generate an embedding for each user question and retrieve a bounded number of relevant chunks.
- Save embedding-model and chunking configuration with the collection so incompatible indexes can be identified.
- Add remove-document and rebuild-index operations.

**Completion check**

- A document can be indexed, searched by a related question, removed, and re-indexed without making network calls to a hosted vector database.

**Spec coverage:** FR-12, FR-13, FR-15, NFR-1, NFR-4, NFR-6.

### Phase 4: RAG answers with sources

**Work**

- Add a RAG service that combines the current question, appropriate recent chat history, and retrieved source text.
- Build a clear prompt instructing the model to answer from supplied excerpts, identify sources, and say when the excerpts do not contain an answer.
- Include source names and page/section references in the UI alongside the generated answer.
- Limit retrieved chunks and conversation history so prompt content fits the configured model context budget; reserve tokens for the response.
- If retrieval returns no sufficiently relevant result, communicate that clearly rather than implying the answer is document-grounded.

**Completion check**

- Questions answerable from indexed documents receive relevant source references; unsupported questions are not represented as answered from those documents.

**Spec coverage:** FR-2, FR-13, FR-14, NFR-2, NFR-3.

### Phase 5: Hardening, testing, and assessment demo

**Work**

- Add friendly errors for connection failures, missing models, timeouts, unsupported/empty files, and interrupted generation.
- Verify cancellation and loading-state cleanup; ensure repeated submission cannot create duplicate requests.
- Add tests using fake Ollama/vector-store dependencies so the core suite does not need a running model.
- Manually test a small sample PDF, Markdown file, and text file against local Ollama.
- Review data handling: no prompt/content logging by default, no external AI calls, and accurate privacy notice.
- Update the README with setup, architecture, a short RAG explanation, limitations, and a demo walkthrough.

**Completion check**

- Automated tests pass; manual local-model checks pass; the acceptance criteria in the spec are demonstrated and setup is repeatable.

**Spec coverage:** Acceptance Criteria, NFR-1 through NFR-6, Definition of Done.

## 5. Initial Settings to Make Configurable

Keep these values centralized in configuration rather than scattering constants through the app:

- Ollama base URL (default to the local Ollama endpoint).
- Chat model name and embedding model name.
- Supported file types and maximum upload size.
- Chunk size and overlap.
- Maximum retrieved chunks and similarity/relevance threshold.
- Maximum conversation-history size, context budget, response-token allowance, and request timeout.
- Local document and vector-store directories.

Choose concrete values during implementation and document them in the README. Token counting can vary by model; use model-aware tokenization where practical, otherwise apply conservative documented limits and handle Ollama context errors gracefully.

## 6. Key Design and Privacy Rules

- Keep Streamlit UI code separate from document processing, retrieval, and Ollama HTTP/client calls.
- Pass retrieved original text to the chat model; vectors are only for similarity search and are not a substitute for document text.
- Use the same embedding model and compatible dimensions for indexing and query embeddings. Require a rebuild when this configuration changes.
- Keep document content, extracted text, embeddings, and active conversation local by default.
- Never expose uploaded document content or chat messages in routine logs.
- Do not render model output as trusted HTML or executable content.
- Explain that changing the Ollama endpoint sends prompts and documents to that configured endpoint.

## 7. Testing Plan

- **Unit tests:** file validation, text extraction, chunk boundaries/overlap, metadata preservation, context construction, and configuration validation.
- **Service tests:** successful Ollama response, missing model, unavailable endpoint, timeout/cancellation, embedding failure, and streaming interruption using fakes or mocked HTTP.
- **RAG tests:** relevant chunks are added to the prompt, source metadata is returned, irrelevant/no-result searches are handled, removed documents disappear, and context limits are respected.
- **Manual integration checks:** run against local Ollama with a small known document and verify answer content, cited page/source, follow-up context, clear-chat behavior, and offline error behavior.

## 8. Main Risks and Responses

| Risk | Response |
| --- | --- |
| Ollama or a model is not installed/running | Add setup checks and show a specific connection/model message |
| Embedding model changes after indexing | Persist model/config metadata and require index rebuild |
| Poor retrieval returns misleading passages | Limit results, tune chunking, show sources, and allow an explicit no-evidence response |
| Prompt exceeds model context | Bound history and retrieved text, reserve response capacity, and handle request rejection |
| PDF has scanned images rather than selectable text | State that OCR is not supported in the initial version and report when no text is extracted |
| Local data is accidentally committed | Ignore data directories and `.env`; verify repository status before submission |

## 9. Recommended Assessment Demonstration

1. Start the app and show its Ollama connection and selected model.
2. Ask a general question to demonstrate local chat.
3. Upload a short PDF or Markdown document with a known fact.
4. Ask a question whose answer is in that document and show the cited source/page.
5. Ask something absent from the document and show the no-evidence behavior.
6. Remove the document and show that it is no longer retrievable.
7. Stop Ollama or use an invalid endpoint and demonstrate the actionable error state.

## 10. Scope Control

For the first assessment version, do not add authentication, cloud deployment, external model APIs, OCR, web search, multi-user support, or persistent chat history. Revisit these only if the assessment requirements explicitly call for them.
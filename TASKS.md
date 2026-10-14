# Local Ollama Chatbot - Task Checklist

Implementation checklist based on [SPEC.md](SPEC.md) and [PLAN.md](PLAN.md). Complete tasks in order where possible. Check a task only after its stated result is verified.

## Phase 0: Project Setup

- [ ] Create the chatbot project directory and Python virtual environment.
- [x] Add `requirements.txt` with Streamlit, the Ollama Python client, ChromaDB, pypdf, python-dotenv, and pytest.
- [x] Add `.gitignore` entries for the virtual environment, `.env`, uploaded documents, chat data, and ChromaDB files.
- [ ] Create the planned `src/chatbot`, `tests`, and local `data` directories.
- [x] Add `.env.example` for the Ollama URL, chat model, embedding model, data paths, and request limits.
- [ ] Install and start Ollama; verify the local endpoint is reachable.
- [ ] Pull and verify one chat model and one embedding model; record the model names in setup documentation.
- [x] Add initial `README.md` instructions for creating the environment, installing dependencies, and running the app.

**Phase complete when:** A clean setup can start the app environment and connect to the configured local Ollama instance.

## Phase 1: Basic Chat

- [x] Add centralized configuration loading and validation in `src/chatbot/config.py`.
- [x] Implement an Ollama service in `src/chatbot/ollama_service.py` for model listing and chat requests.
- [x] Add a Streamlit chat page in `app.py` with transcript, message input, send action, model selector, and status display.
- [x] Store messages in session state so chat works across Streamlit reruns without persisting between app restarts.
- [x] Send recent conversation history with each follow-up message.
- [x] Stream response text when supported by the installed Ollama client; display a clear generating state.
- [ ] Prevent duplicate submissions while a response is pending.
- [x] Add a new-chat action that clears the UI and the in-memory conversation context.
- [x] Show actionable errors for unavailable Ollama, missing models, timeouts, and interrupted requests.
- [ ] Preserve the user's draft message when a request fails.
- [x] Add tests for configuration and Ollama service success/failure using a fake or mocked client.

**Phase complete when:** A user can have a multi-turn conversation, clear it, and recover from a request failure.

## Phase 2: Document Processing

- [ ] Implement document type and file-size validation for PDF, Markdown, and plain text.
- [ ] Implement text extraction in `src/chatbot/document_loader.py`.
- [ ] Preserve PDF page numbers and attach page metadata to extracted text.
- [ ] Normalize extracted text and report empty, unsupported, or unreadable documents clearly.
- [ ] Implement chunking in `src/chatbot/text_chunker.py` with configurable chunk size and overlap.
- [ ] Ensure each chunk includes a stable document ID, source filename, and page/section metadata when available.
- [ ] Add duplicate-document detection using a content hash or stable identifier.
- [ ] Add tests for validation, extraction, chunk boundaries, overlap, and metadata preservation.
- [ ] Add Streamlit upload and indexed-document list controls.

**Phase complete when:** Supported files become inspectable text chunks with source metadata; invalid files do not enter the index.

## Phase 3: Embeddings and Vector Search

- [ ] Implement an embedding operation in the Ollama service using the configured embedding model.
- [ ] Implement a ChromaDB adapter in `src/chatbot/vector_store.py` using persistent local storage.
- [ ] Store chunk text, embedding vectors, and source metadata in the local collection.
- [ ] Persist the embedding model and indexing configuration used for the collection.
- [ ] Detect an embedding-model or chunking configuration mismatch and explain when rebuilding is required.
- [ ] Embed user questions and retrieve a bounded set of relevant chunks.
- [ ] Add a remove-document operation that deletes all its chunks from the collection.
- [ ] Add an index-rebuild operation for changed embedding or chunking settings.
- [ ] Add tests using a fake embedding service and vector store for index, search, deletion, and rebuild behavior.

**Phase complete when:** A local document can be indexed, searched, removed, and re-indexed without a hosted service.

## Phase 4: RAG Answers and Sources

- [ ] Implement `src/chatbot/rag_service.py` to coordinate query embedding, retrieval, prompt construction, and response generation.
- [ ] Include retrieved original text, not vectors, in the model prompt.
- [ ] Include relevant recent conversation messages without exceeding the configured context budget.
- [ ] Reserve context capacity for the generated answer and bound the number/size of retrieved chunks.
- [ ] Instruct the model to answer from the supplied excerpts and disclose when they do not support an answer.
- [ ] Display source filenames and page/section references with answers that use retrieved content.
- [ ] Show a clear no-relevant-source state when retrieval finds no sufficiently relevant chunks.
- [ ] Add tests for prompt construction, context limits, source references, and no-result behavior.

**Phase complete when:** Document-grounded answers show their sources, and unsupported answers are not presented as sourced.

## Phase 5: Reliability, Privacy, and Verification

- [ ] Verify cancellation and timeout paths always clear the generating state.
- [ ] Verify failed or cancelled requests do not corrupt chat history or lose the user's draft.
- [ ] Verify removed documents are absent from subsequent retrieval results.
- [ ] Verify no prompts, responses, or document text are written to routine logs.
- [ ] Verify local documents, `.env`, and vector-store data are excluded from version control.
- [ ] Add a privacy notice explaining the configured Ollama endpoint and local data behavior.
- [ ] Verify model output is rendered as text/approved formatting, not trusted executable HTML.
- [ ] Run the full automated test suite without requiring a live Ollama model.
- [ ] Manually test chat and RAG against local Ollama using a small PDF, Markdown file, and text file.
- [ ] Manually test follow-up context, clear-chat behavior, source display, no-evidence behavior, and document removal.
- [ ] Manually stop Ollama or configure an invalid endpoint and verify the recovery message.
- [ ] Complete the assessment demonstration steps in `PLAN.md`.
- [ ] Update `README.md` with architecture, setup, supported formats, limitations, privacy notes, and demo instructions.

**Phase complete when:** Automated tests pass, the local integration checks pass, and the app can be set up and demonstrated from the README.

## Definition of Done

- [ ] All required tasks above are complete or explicitly recorded as deferred with a reason.
- [ ] Acceptance criteria in [SPEC.md](SPEC.md) have been verified.
- [ ] The project runs locally with Ollama and does not require a cloud AI service.
- [ ] No secrets, user documents, chat content, or generated vector data are included in the submission.
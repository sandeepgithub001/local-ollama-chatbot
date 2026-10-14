# Local Ollama Chatbot - Requirements Specification

## 1. Overview

This document defines requirements for a standalone chatbot application that uses Ollama to run a large language model locally. The application is a separate project and is not part of the Personal Bookmark Manager.

**Assessment context:** Generative AI Training Assessment  
**Status:** Proposed requirements  
**Primary runtime:** Ollama on the user's machine

## 2. Problem Statement

Users need a simple conversational interface for asking questions of a locally running language model. The application should make local inference accessible without sending prompts or responses to a hosted AI provider.

## 3. Goals

- Provide a usable chat interface for a model served by Ollama.
- Keep prompts and responses on the user's machine by default.
- Show clear status and recovery guidance when Ollama or the selected model is unavailable.
- Support an understandable, testable boundary between the user interface and the Ollama service.

## 4. Out of Scope

- Cloud-hosted model providers or account-based AI services.
- Training or fine-tuning foundation models.
- Web search, external tools, or autonomous actions.
- Multi-user accounts, shared conversations, and remote hosting.
- Persistent chat history in the initial version, unless added as a separately approved requirement.
- Fine-tuning or training models on user documents; RAG supplies relevant information at query time instead.

## 5. Users and Assumptions

### Primary user

A single user running the application locally for learning, experimentation, and general question answering.

### Assumptions

- Ollama is installed and running on the same machine, or at a user-configured Ollama endpoint reachable from it.
- The user has downloaded at least one compatible model in Ollama.
- Model output can be inaccurate or incomplete; the application does not present it as verified fact.
- Initial configuration may use Ollama's local default endpoint, but the endpoint and model should be configurable.

## 6. Functional Requirements

### FR-1: Start a conversation
The user can enter a message and submit it to the selected Ollama model. The interface displays the user's message and the model's response in conversation order.

### FR-2: Continue a conversation
The application sends relevant prior messages in the active conversation so that the model can respond with conversational context. The application must apply a configurable or documented context limit and handle requests that exceed it without crashing.

### FR-3: Select a model
The user can select from models available through Ollama. If model discovery is unavailable, the application reports the issue and provides a way to retry or use a configured model name.

### FR-4: Configure the Ollama endpoint
The application uses a configurable Ollama base URL. Invalid or unreachable endpoint settings produce a clear error and do not prevent the user from correcting the setting.

### FR-5: Show generation state
While a response is being generated, the interface indicates that work is in progress and prevents accidental duplicate submission of the same pending message. The user can cancel generation when supported by the integration.

### FR-6: Handle failures
The application presents actionable feedback for connection failures, missing models, request timeouts, server errors, and malformed or interrupted responses. It must remain usable after an individual request fails.

### FR-7: Clear the conversation
The user can start a fresh conversation. Clearing the conversation removes its messages from the active UI and from any in-memory context used for subsequent requests.

### FR-8: Stream responses
The application should display generated text incrementally when the selected Ollama API mode supports streaming. If streaming is unavailable, it may display the completed response when generation finishes.

### FR-9: Privacy notice
The interface or project documentation explains that prompts are sent to the configured Ollama endpoint and states whether conversations are stored. The initial version must not transmit chat content to an unrelated external service.

### FR-10: Add knowledge documents
The user can add supported local documents to a knowledge base and see which documents are available for questions. The initial supported file types and maximum file size must be documented. Unsupported, empty, or unreadable files produce a clear error and are not indexed.

### FR-11: Transform and chunk documents
Before indexing, the application extracts text from supported documents, normalizes it as needed, and splits it into smaller overlapping chunks. The chunking strategy and limits must be configurable or documented. Each chunk retains metadata identifying its source document and, when available, its page or section.

### FR-12: Create and store embeddings
The application converts each document chunk into an embedding using a model compatible with the configured Ollama setup. Embeddings and their source metadata are stored in a local vector store. The application records which embedding model and relevant indexing settings were used so that incompatible indexes can be detected and rebuilt.

### FR-13: Retrieve relevant information
For a user question, the application embeds the query, searches the vector store for the most relevant document chunks, and includes a bounded number of results in the model request. Retrieval must be limited by a documented relevance threshold or result limit and by the model's available context capacity.

### FR-14: Ground answers in sources
When knowledge-base results are used, the assistant should answer using those excerpts and show the source document names, with page or section references when available. If no sufficiently relevant material is found, the assistant should say that the knowledge base did not provide an answer rather than inventing a sourced claim.

### FR-15: Manage the knowledge base
The user can remove a document and its indexed chunks. Removing a document prevents it from appearing in later retrieval results. Re-indexing is available when the embedding model or chunking settings change.

## 7. Non-Functional Requirements

### NFR-1: Local-first operation
The application must communicate with Ollama directly and must not require an external AI API key or hosted inference service for its core chat workflow.

### NFR-2: Responsiveness
The interface remains responsive while a model is generating. Long-running requests have a configurable timeout or cancellation path.

### NFR-3: Reliability
A failed request must not corrupt the active conversation or terminate the application. The user can retry after addressing the cause.

### NFR-4: Security and privacy
- Do not log full prompts or responses by default.
- Do not expose the Ollama endpoint to untrusted networks by default.
- Validate endpoint configuration and avoid rendering model output as trusted executable markup.
- If the endpoint is changed from localhost, inform the user that chat data will be sent to that endpoint.
- Document contents, extracted text, and embeddings remain local by default. Any external endpoint or storage destination must be clearly disclosed before use.

### NFR-5: Accessibility
The chat workflow is usable with keyboard navigation, visible focus, semantic labels, and sufficient contrast. New messages and generation status are communicated to assistive technology without repeatedly announcing every streamed token.

### NFR-6: Maintainability
Ollama communication is isolated behind a service/interface so it can be tested independently from the UI and replaced or extended without coupling UI components to HTTP details.

## 8. User Experience Requirements

The primary screen contains:

- A conversation transcript with visually distinct user and assistant messages.
- A message composer with a clearly labeled send action.
- A model selector and connection/generation status.
- A control to start a new conversation.
- Empty, loading, response, and error states.

The interface should preserve readable formatting for plain text and code, keep the newest response visible when appropriate, and avoid losing the draft message when a request fails.

## 9. High-Level Design

1. During document ingestion, a document processor extracts and transforms text, then divides it into chunks with source metadata.
2. An embedding service converts each chunk into a vector, which is saved with its metadata in a local vector store.
3. For a question, the application embeds the query and searches the vector store for relevant chunks.
4. The chat service combines the question, appropriate recent conversation history, and retrieved chunks into a prompt that fits the model context limit.
5. The configured Ollama model generates a response; the UI displays it with source references and handles streaming, cancellation, timeout, and errors.

The vector store is a retrieval index, not the language model. The initial implementation may choose an appropriate local vector-store technology, but it must keep the storage behind an interface so that the choice can change without coupling it to the UI.

The initial version should use Ollama's local API. Exact API routes and request/response formats are implementation choices and must be verified against the Ollama version selected for the project.

## 10. Acceptance Criteria

- Given Ollama is running and a model is available, when the user submits a message, the assistant returns a response in the active conversation.
- Given prior messages exist, when the user sends a follow-up, the request includes the active conversation context within the defined limit.
- Given a supported document is added, its extracted text is chunked, embedded, and indexed with source metadata.
- Given a user asks about information in an indexed document, relevant chunks are retrieved and supplied to the model, and the response identifies the source document.
- Given no relevant knowledge-base content is found, the assistant does not claim that an unsupported answer came from the documents.
- Given a document is removed, its chunks are not returned by subsequent searches.
- Given the combined history and retrieved chunks approach the model context limit, the application trims or rejects content predictably instead of sending an oversized request.
- Given response generation is underway, the user can see that state and cannot accidentally submit duplicate requests through repeated clicks.
- Given Ollama is unavailable, the user sees a connection error with a retry or configuration path, and the application remains usable.
- Given the selected model is missing, the user sees a model-specific error and can select or configure another model.
- Given the user clears the conversation, its messages are no longer included in the next request.
- Given a request is cancelled or times out, the UI exits the loading state and preserves the conversation and draft as appropriate.
- Given the user inspects the privacy information, it accurately states the configured endpoint and the application's chat storage behavior.
- Automated tests cover successful requests, error responses, cancellation or timeout behavior, and conversation-context construction without requiring a live Ollama instance.

## 11. Open Decisions

- Which UI and application framework will be used?
- Should chat history persist between application restarts? If so, where and for how long?
- Which Ollama model should be the default for assessment demonstrations?
- Which embedding model and local vector-store implementation will be used, and are both available through the chosen Ollama setup?
- Which document formats, maximum file size, chunk size/overlap, retrieval limit, and relevance threshold should the first version support?
- Should documents and indexes persist across application restarts, and what deletion guarantees are required?
- Should users be able to edit or regenerate a previous message/response?
- What maximum conversation length and request timeout should be used?
- Is the application strictly single-user/local, or should remote clients be supported later?

## 12. Definition of Done

The requirement is considered implemented when the acceptance criteria are met, automated tests pass without depending on a live model, the application has been manually verified against a locally running Ollama instance, and setup/privacy behavior is documented for a new user.

## 13. Concepts in Plain Language

### Transformation

Transformation is the preparation of raw source data before it is used. For this project, a document may be parsed to extract text, have irrelevant formatting removed, and be split into chunks. Transformation does not itself mean that the model has learned or memorized the document.

### Chunk

A chunk is a manageable piece of extracted text. Documents are chunked because embedding and retrieval work on smaller passages, and only a few relevant passages should be sent with a question. A small overlap between neighboring chunks can preserve meaning that crosses a boundary.

### Embedding

An embedding is a list of numbers produced by an embedding model to represent the meaning of text. Similar meanings tend to have vectors that are close according to a similarity measure. An embedding is not a summary and is not directly readable like the original text.

### Vector

A vector is an ordered list of numbers. In this application, the embedding is the vector. A vector store saves vectors alongside metadata, such as the original document name and page, and can efficiently find vectors similar to a query vector.

### Token

A token is a piece of text as counted by a language model. A token may be a whole word, part of a word, punctuation, or other text. Models impose limits in tokens, not simply in characters or words. The exact tokenization depends on the selected model.

### Context and context window

Context is the information supplied to the model for one response. It can include system instructions, recent chat messages, the current question, and retrieved document chunks. The context window is the model's maximum token capacity for the request and response combined. If too much content is included, the application must select or shorten content before sending the request.

### RAG (Retrieval-Augmented Generation)

RAG is a pattern that retrieves relevant information and gives it to a language model when answering. In this project, documents are transformed and chunked, chunks are embedded and stored as vectors, and a question is used to find similar chunks. The selected original text (not just its vector) is added to the prompt so the model can use it and cite its source. RAG does not retrain the model.

### How the terms fit together

1. **Transform:** Extract and prepare text from a local document.
2. **Chunk:** Split the prepared text into smaller passages and retain source metadata.
3. **Embed:** Convert each passage into a numeric vector.
4. **Store:** Save vectors and metadata in a local vector store.
5. **Retrieve:** Convert the user's question into a vector and find similar stored vectors.
6. **Generate:** Add the retrieved original passages and relevant conversation context to the prompt, then ask the Ollama language model to answer within its token/context limit.

For example, if a user asks, "What is the document's refund period?", retrieval should find the passage discussing refunds. The model receives that passage and the question, then responds with the answer and its document source. If no relevant passage is found, it should say so instead of implying that it searched successfully.

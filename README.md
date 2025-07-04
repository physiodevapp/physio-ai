# 🧠 Physio-AI: Clinical Reasoning Assistant for Physiotherapy

Physio-AI is an intelligent assistant designed to support clinical reasoning in physiotherapy.  
It combines **OpenAI's GPT models** with a **vector-based retrieval system** built using **ChromaDB** and **sentence-transformers**, following a **RAG (Retrieval-Augmented Generation)** architecture.

---

## 🔍 What does it do?

- 🗂️ **Ingests clinical content** (e.g. PDFs with subgroup classifications)
- 🧬 **Generates embeddings** using `all-MiniLM-L6-v2`
- 🧠 **Indexes data** into ChromaDB for fast similarity search
- 🤖 **Uses OpenAI** to produce clinically sound, explainable answers based on relevant documents
- 🚀 Exposes a FastAPI endpoint for integration with a frontend (like a chat interface)

---

## ⚙️ Built with

- 🐍 Python 3.10+
- 🧠 OpenAI GPT-3.5 Turbo
- 📦 ChromaDB (local vector store)
- 💬 Sentence-Transformers
- ⚡ FastAPI
- 🔁 Redis (for caching responses)
- 📄 PDF text extraction with PyMuPDF

---

## 🧪 Ideal for

- Physiotherapists looking to **understand clinical subgroups**
- Teaching environments where **clinical reasoning** is emphasized
- Prototyping AI assistants in evidence-based healthcare

---


# Agentic_RAG_System
# Multi-Agent RAG System for Scientific Literature Analysis

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python version">
  <img src="https://img.shields.io/badge/Next.js-13+-black.svg" alt="Next.js version">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/CrewAI-Framework-orange.svg" alt="CrewAI">
</p>

## Overview

This multi-agent RAG (Retrieval Augmented Generation) system addresses fundamental limitations of traditional RAG approaches by decomposing complex information retrieval and synthesis tasks into specialized agent roles. The system particularly excels at scientific literature screening and synthesis, enabling researchers to efficiently process and analyze large volumes of academic papers.

### Key Features

- 🤖 **Multi-Agent Architecture**: Specialized agents for document summarization, query analysis, and information synthesis
- 📚 **Scientific Paper Analysis**: Structured extraction of research metadata and comprehensive summarization  
- 🔍 **Advanced Query Processing**: Handles multi-step reasoning, qualitative assessment, and complex queries
- ⚡ **Efficient Document Matching**: Adaptive cosine similarity with dynamic thresholds
- 🖥️ **Full-Stack Architecture**: FastAPI backend with Next.js frontend
- 🔄 **Asynchronous Processing**: Background task execution with real-time progress tracking

## System Architecture

The system is built on a specialized agent workflow:

### Analysis Crew
1. **Document Summary Agent**: Creates comprehensive summaries preserving key concepts
2. **Query Analysis Agent**: Analyzes user queries and identifies relevant documents
3. **Document Analysis Agent**: Synthesizes information across documents

### Scientific Summary Crew  
1. **Scientific Document Summary Agent**: Creates structured research paper summaries
2. **Report Agent**: Formats summaries into well-organized reports

## Quick Start

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/multi-agent-rag.git
cd multi-agent-rag

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

# Create required directories
mkdir -p logs
mkdir -p ~/Desktop/crew_docs/{documents,summaries,summary_reports}

# Start the FastAPI server
uvicorn fast_crew_api:app --host 0.0.0.0 --port 3001
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local with API endpoint

# Start development server
npm run dev

# Access application at http://localhost:3000
```

## Usage

### Document Processing

1. **Upload Documents**: Place PDF, TXT, or DOCX files in `~/Desktop/crew_docs/documents`
2. **Generate Summaries**: Use the summary crew to create structured scientific paper summaries
3. **Query Documents**: Submit complex queries to analyze document collections

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/crew` | POST | Initiate document analysis or summary generation |
| `/api/crew/{job_id}` | GET | Get job status and results |

### Example API Usage

```javascript
// Start a document analysis job
const analyzeResponse = await fetch('/api/crew', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_query: "Compare methodologies across machine learning papers",
    crew_type: "analysis"
  })
});

const { job_id } = await analyzeResponse.json();

// Poll for results
const resultsResponse = await fetch(`/api/crew/${job_id}`);
const results = await resultsResponse.json();
```

## Configuration

### Required Environment Variables

```env
# Azure OpenAI
AZURE_API_KEY=your_azure_api_key
AZURE_API_BASE=your_azure_endpoint
AZURE_API_VERSION=your_api_version

# Required Models
# - gpt-4o: Complex reasoning and synthesis
# - text-embedding-ada-002: Document embeddings
```

### Customization

The system can be extended with:
- New agent roles for specialized analysis
- Custom document loaders for additional formats
- Domain-specific embedding models

## Performance Characteristics

The system demonstrates superior performance compared to traditional RAG in:

- **Multi-step Reasoning**: Successfully handles queries requiring sequential information processing
- **Document Classification**: Correctly categorizes papers by relevance with 0.76 similarity threshold
- **Scientific Literature Analysis**: Preserves technical accuracy while generating comprehensive summaries
- **Complex Query Processing**: Synthesizes information across multiple documents effectively

## Research & Publications

This system was developed as part of research on overcoming RAG limitations for complex query processing. The approach was validated through comprehensive testing on scientific papers, demonstrating significant improvements in handling:

- Multi-step reasoning queries
- General and complex queries
- Implicit queries requiring contextual understanding
- Document collection analysis

## Contributing

Contributions are welcome! Please read our [contributing guidelines](CONTRIBUTING.md) before submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [CrewAI](https://github.com/joaomdmoura/crewai) framework
- Powered by Azure OpenAI models
- Inspired by research on multi-agent systems and RAG limitations

## Contact

For questions or support, please open an issue or contact the maintainers.

## Future Roadmap

- [ ] Integration with open-source archives (arXiv)
- [ ] LLM training for paper quality assessment
- [ ] Enhanced collaborative research features
- [ ] Cross-lingual support for document analysis
- [ ] Expanded mini-application benchmarking suite

---

<p align="center">
  <i>A research tool designed to empower scientists and researchers with AI-driven document analysis</i>
</p>

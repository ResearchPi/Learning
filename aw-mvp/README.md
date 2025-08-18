# ResearchPi

ResearchPi is designed to help researchers and academics analyze the work of specific researchers by:
1. **Collecting papers** from 5 academic databases
2. **Extracting keywords** using KeyBERT (NLP-based keyword extraction)
3. **Classifying research fields** using DeepSeek R1
4. **Generating comprehensive summaries** in structured JSON format

## Processing Flow

```
Papers → NLP (KeyBERT) → LLM (DeepSeek) → Final Output
   ↓           ↓              ↓                 ↓
5 Sources   Keyword         Research       JSON File with
            Extraction      Field Class.   Summary
```

## Paper Sources

- **arXiv** - Preprints and published papers
- **PubMed** - Biomedical and life sciences
- **DOAJ** - Directory of Open Access Journals
- **Zenodo** - Research outputs and datasets
- **Crossref** - Academic metadata and DOIs

## File Structure

### Core Files

- **`PaperCollector.py`** - Collects research papers from multiple academic databases
- **`KeywordExtractor.py`** - Extracts keywords using KeyBERT NLP model
- **`LLMProcessor.py`** - Processes papers using DeepSeek AI for field classification
- **`ResearchProcessor.py`** - Main orchestrator that combines all components

### Configuration & Setup

- **`setup.sh`** - Automated environment setup script
- **`requirements.txt`** - Python dependencies
- **`.env`** - Environment variables (API key)

### Output

- **`research_analysis_YYYYMMDD_HHMMSS.json`** - Final analysis results
- **`paper_collector_YYYYMMDD_HHMMSS.log`** - Processing logs

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- OpenRouter account and API key

### Quick Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd aw-mvp
   ```

2. **Run the setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

4. **Set up your API key:**
   ```bash
   # Edit .env and add your OpenRouter API key (OPENROUTER_API_KEY="your_api_key_here")
   ```

### Manual Setup

If you prefer manual setup:

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   export OPENROUTER_API_KEY="your_api_key_here"
   ```

## API Key Setup

### OpenRouter Account

1. Go to [OpenRouter](https://openrouter.ai/)
2. Create an account and sign in
3. Go to "API Keys" section
4. Generate a new API key
5. Copy the key to your `.env` file or set as environment variable

### Environment Variables

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_api_key_here
```

## Usage

### Basic Usage

Check main of ResearchProcessor.py


## Output Format

The tool generates a comprehensive JSON file with the following structure:

```json
{
  "metadata": {
    "generation_date": "2025-08-13T18:43:42.044145",
    "total_papers": 164,
    "sources": ["arXiv", "PubMed", "DOAJ", "Zenodo", "Crossref"],
    "nlp_model_used": "KeyBERT",
    "llm_provider": "DeepSeek R1 (Free)"
  },
  "field_classification": {
    "primary_fields": [
      {
        "name": "Medical Imaging",
        "description": "Application of imaging technologies and computational methods to diagnose and analyze medical conditions",
        "confidence": 0.95,
        "key_terms": ["Magnetic Resonance Imaging", "CT", "Prostate Segmentation"],
        "paper_count": 70
      }
    ],
    "secondary_fields": [
      {
        "name": "Computer Vision",
        "description": "Development of algorithms and neural networks for automated image analysis",
        "confidence": 0.95,
        "key_terms": ["Image Segmentation", "Deep Learning", "GANs"],
        "paper_count": 60
      }
    ],
    "interdisciplinary_areas": [
      {
        "name": "Computational Medicine",
        "description": "Integration of imaging, AI, and clinical data for personalized healthcare",
        "confidence": 0.85,
        "key_terms": ["Organ Segmentation", "Patient-Specific Dose"],
        "paper_count": 20
      }
    ]
  },
  "papers": [
    {
      "title": "AI-assisted mesh generation for subject-specific modeling of facial soft tissues",
      "authors": [
        {
          "name": "John Smith",
          "affiliation": "Department of Biomedical Engineering, Rensselaer Polytechnic Institute"
        },
        {
          "name": "Jane Doe",
          "affiliation": "Department of Biomedical Engineering, Rensselaer Polytechnic Institute"
        }
      ],
      "publication_date": "2025-May-19",
      "journal": "International journal of computer assisted radiology and surgery",
      "abstract": "Simulation of reconstructive and cosmetic facial surgeries...",
      "links": {
        "pmid": "40389796",
        "abstract": "https://pubmed.ncbi.nlm.nih.gov/40389796/",
        "pdf": null,
        "doi": "10.1007/s11548-025-03419-9"
      },
      "extracted_keywords": [
        "conventional meshing",
        "mesh editing",
        "landmark digitization mesh"
      ],
      "original_categories": [],
      "keyword_sources": []
    }
  ],
  "summary": "**Research Profile Summary**\n\n**Researcher Information:**\n- **Name:** John Smith\n- **Total Publications:** 164\n- **Primary Institution:** Biomedical Engineering Department, Rensselaer Polytechnic Institute\n\n**Research Focus Areas:**\n- **Medical Imaging** (Confidence: 0.95)\n- **Computer Vision** (Confidence: 0.95)\n- **Deep Learning** (Confidence: 0.90)...(Shortened)",
  "researcher": {
    "name": "John Smith",
    "institution": "Rensselaer Polytechnic Institute",
    "affiliations": [
      "Biomedical Engineering Department, Rensselaer Polytechnic Institute, Troy, NY 12180, USA",
      "Biomedical Imaging Center, Center for Biotechnology and Interdisciplinary Studies, Rensselaer Polytechnic Institute, Troy, NY, USA",
      ...,
    ],
    "analysis_date": "2025-08-13T18:43:42.044448"
  }
}
```

## File Descriptions

### `PaperCollector.py`
- **Purpose**: Collects research papers from 5 academic databases
- **Input**: Researcher name and optional affiliation
- **Output**: List of paper dictionaries with metadata
- **Features**: Automatic deduplication, error handling, rate limiting

### `KeywordExtractor.py`
- **Purpose**: Extracts relevant keywords using KeyBERT NLP model
- **Input**: Paper titles and abstracts
- **Output**: Extracted keywords and categories

### `LLMProcessor.py`
- **Purpose**: Uses DeepSeek AI for research field classification
- **Input**: Papers with keywords and researcher metadata
- **Output**: Field classifications and research summaries

### `ResearchProcessor.py`
- **Purpose**: Main orchestrator that combines all components
- **Input**: Researcher name and institution
- **Output**: Complete research analysis in JSON format

### `setup.sh`
- **Purpose**: Automated environment setup script
- **Features**:
  - Creates Python virtual environment
  - Installs all dependencies
  - Upgrades pip
  - Provides activation instructions
- **Usage**: `./setup.sh` (make executable first with `chmod +x setup.sh`)

### Issues

1. **API Key Errors**: Ensure your OpenRouter API key is correctly set
2. **Import Errors**: Make sure you're in the virtual environment
3. **Memory Issues**: Large paper collections may require more RAM
4. **Rate Limiting**: Some APIs have rate limits; the tool includes delays

### Logs

The tool generates detailed logs in `paper_collector_YYYYMMDD_HHMMSS.log` files. Check these for debugging information.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
# ExamParser

## Environment
```
conda create -n parser python==3.12
conda activate tools

pip install pdfplumber
pip install PyMuPDF
pip install tqdm
```

## Quick Start
- `python exam_parser`
    - input: Data/NPExam/*/*.pdf
    - output: Data/exams/*.json
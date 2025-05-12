"""
"""
import os
import re

from utils_pdf_file import extract_text_from_pdf_page

def split_lines(text):
    return text.splitlines()

def join_lines(lines):
    return '\n'.join(lines)

def clean_and_filter_blank_lines(lines):
    return [line.strip() for line in lines if line.strip()]

def is_page_info(line):
    return bool(re.search(r"共\s*\d+\s*頁\s*第\s*\d+\s*頁", line) or
                re.search(r"第\s*\d+\s*頁\s*共\s*\d+\s*頁", line))

def is_title_line(line):
    return bool(re.match(
        r"^[\u4e00-\u9fa5]{1,5}科\s+(專科護理通論|進階專科護理)",
        line.strip()))

def is_exact_keyword(line):
    return line.strip() in [
        "專科護理通論(共同) 專科護理通論",
        "ˉ",
        "【以下空白】"
    ]

def filter_and_remove(lines):
    filtered = []
    removed = []
    for line in lines:
        if is_page_info(line):
            removed.append(line)
            continue
        if is_title_line(line):
            removed.append(line)
            continue
        if is_exact_keyword(line):
            removed.append(line)
            continue
        filtered.append(line)
    return filtered, removed

def parse_exam_text(text):
    question_blocks = re.split(r'\n(?=\d+\.\s)', text.strip())
    questions = []
    for block in question_blocks:
        lines = block.strip().splitlines()
        if not lines:
            continue
        full_text = ' '.join(line.strip() for line in lines)
        # qid
        qid_match = re.match(r"^(\d+)\.\s*", full_text)
        if not qid_match:
            continue
        qid = int(qid_match.group(1))
        full_text = full_text[qid_match.end():].strip()
        # stem and options
        split = re.split(r'\(([A-D])\)', full_text)
        ## 至少要有 (A)(B)(C)(D)
        if len(split) < 9:  
            raise ValueError(split)
        stem = split[0].strip()
        option_map = {
            split[i]: split[i+1].strip()
            for i in range(1, len(split)-1, 2)
        }
        questions.append({
            "qid": qid,
            "stem": stem,
            "A": option_map.get("A", ""),
            "B": option_map.get("B", ""),
            "C": option_map.get("C", ""),
            "D": option_map.get("D", "")
        })
    return questions

def parse_meta_info(text):
    
    patterns = {
        "year": [
            r"(\d{3})\s*年度專科護理師甄審筆試試題本",
        ],
        "department": [
            r"報考科別[:：]?\s*([^\s\n]+)",
        ],
        "subject": [
            r"科目[:：]?\s*([^\s\n]+)",
        ]
    }
    metadata = {}
    for key, regex_list in patterns.items():
        for pattern in regex_list:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                metadata[key] = match.group(1).strip()
                break
        else:
            raise ValueError(f"Unable to extract {key} from text.")
    return metadata

def exam_parser(file_path):
    """given exam question filepath(*.pdf), return parsered dictionary
    Args:
        filepath: pdf filepath
    Returns:
        question_dict: dict
    """
    assert os.path.isfile(file_path), f"{file_path} not a file!"
    text = extract_text_from_pdf_page(file_path, start_page=2, end_page=None)
    meta_text = extract_text_from_pdf_page(file_path, start_page=1, end_page=1)
    # filter
    lines = split_lines(text)
    clean_lines = clean_and_filter_blank_lines(lines)
    filtered_lines, removed_lines = filter_and_remove(clean_lines)
    # join
    filtered_text = join_lines(filtered_lines)
    removed_text = join_lines(removed_lines)
    exam = parse_exam_text(filtered_text)
    meta_data = parse_meta_info(meta_text)
    return meta_data, exam, meta_text, filtered_text, removed_text

def get_base_name(file_path):
    file_name = os.path.basename(file_path).strip('.pdf')
    return file_name

if __name__ == "__main__":
    from utils import mkdir, txt_dump, json_dump
    SOURCE_DIR = os.path.join("Data", "NPExam")
    DEST_DIR = 'tmp'
    mkdir(DEST_DIR)
    filtered_dir = os.path.join(DEST_DIR, 'filtered')
    removed_dir = os.path.join(DEST_DIR, 'removed')
    meta_dir = os.path.join(DEST_DIR, 'meta')
    #json_dir = os.path.join(DEST_DIR, 'exam')
    json_dir = os.path.join('Data', 'exams')
    mkdir(filtered_dir)
    mkdir(removed_dir)
    mkdir(meta_dir)
    mkdir(json_dir)
    # loop
    years = os.listdir(SOURCE_DIR)
    for year in years:
        exam_dir = os.path.join(SOURCE_DIR, year, "Exam")
        dep_sub_file_names = os.listdir(exam_dir)  # department, subject
        for dep_sub_file_name in dep_sub_file_names:
            source_file_path = os.path.join(exam_dir, dep_sub_file_name)
            # setup dest file path
            base_name = f"{year}_{get_base_name(source_file_path)}"
            meta_txt_file_path = os.path.join(meta_dir, base_name + '.txt')
            filtered_txt_file_path = os.path.join(filtered_dir, base_name + '.txt')
            removed_txt_file_path = os.path.join(removed_dir, base_name + '.txt')
            json_file_path = os.path.join(json_dir, base_name + '.json')
            # parse
            meta, exam, meta_text, filtered_text, removed_text = exam_parser(source_file_path)
            # dump
            txt_dump(meta_txt_file_path, meta_text)
            txt_dump(filtered_txt_file_path, filtered_text)
            txt_dump(removed_txt_file_path, removed_text)
            for qset in exam:
                qset.update(meta)
            json_dump(json_file_path, exam)

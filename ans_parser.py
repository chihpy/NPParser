"""
"""
import os
import re

from utils_pdf_file import extract_text_from_pdf_page, extract_tables_from_pdf

#def validate_answer_dict(ans_dict: dict, expected_qid_count: int = 80):
#    missing = [str(i) for i in range(1, expected_qid_count + 1) if str(i) not in ans_dict]
#    if missing:
#        raise ValueError(f"Missing question IDs: {missing}")

def validate_answer_dict(ans_dict: dict, expected_qid_count: int = 80) -> dict:
    """
    驗證答案字典是否包含所有題號（預設1~80），若缺題號則拋錯。
    若完整，則回傳題號排序後的新 dict，題號以數值排序（key仍為字串）。
    """
    expected_keys = set(str(i) for i in range(1, expected_qid_count + 1))
    actual_keys = set(ans_dict.keys())

    missing = sorted(expected_keys - actual_keys, key=lambda x: int(x))
    if missing:
        raise ValueError(f"Missing question IDs: {missing}")

    # 用 int 排序，然後再轉回 str 作為 key
    sorted_items = sorted(ans_dict.items(), key=lambda item: int(item[0]))
    return dict(sorted_items)



def get_base_name(file_path):
    file_name = os.path.basename(file_path).strip('.pdf')
    return file_name

def extract_tokens(text: str) -> list:
    """
    將原始字串切分為題號與答案交錯排列的 list
    - 題號是連續數字（1~3位數）
    - 答案是 A~D 的英文字或中英混合（如送分、ACD）
    """
    return re.findall(r'\d{1,3}|[A-D]+|送分|[^\d\sA-D]+', text)

def split_lines(text):
    return text.splitlines()

def clean_raw_text(raw):
    # convert to lines
    lines = split_lines(raw)
    rv = []
    rm = []
    flag = False
    for line in lines:
        if "【" in line:
            rm.append(line)
            continue
        if flag:
            rv.extend(line.split())
        else:
            rm.append(line)
        if '題號' in line:
            flag = True
    return rv, rm

def lines_to_qa_dict(lines: list) -> dict:
    """
    將 [題號, 答案, 題號, 答案, ...] 格式的 list 轉換為 dictionary
    key: 題號（str），value: 答案（str）
    """
    q_dict = {}
    for i in range(0, len(lines) - 1, 2):
        qid = lines[i].strip()
        ans = lines[i + 1].strip()
        q_dict[qid] = ans
    return q_dict

def extract_metadata(text: str) -> dict:
    """
    從標頭文字中提取 metadata，例如報考科別與科目。
    支援不規則空白與全形空格。
    """
    # 移除前後空白與全形空白轉半形
    text = text.strip().replace('\u3000', ' ')  # \u3000 是全形空白

    # 提取報考科別
    dept_match = re.search(r'報考科別\s*[:：]\s*(\S+)', text)
    #subject_match = re.search(r'科\s*目\s*[:：]\s*([\S ]+?)\s*(題號|【|共\d+題)?', text)
    #subject_match = re.search(r'科\s*目\s*[:：]\s*([^\s【]+(?:\s*[^\s【]+)*)', text)
    subject_match = re.search(r'科\s*目\s*[:：]\s*(.*)', text)
    return {
        "department": dept_match.group(1) if dept_match else None,
        #"subject": subject_match.group(1).strip() if subject_match else None
        "subject": subject_match.group(1).strip() if subject_match else None
    }



if __name__ == "__main__":
    from utils import mkdir, txt_dump, json_dump
    SOURCE_DIR = os.path.join("Data", "NPExam")
#    DEST_DIR = 'tmp'
#    ans_txt_dir = os.path.join(DEST_DIR, 'ans')
#    mkdir(ans_txt_dir)
    DEST_DIR = os.path.join("Data", "ans")
    mkdir(DEST_DIR)
    years = os.listdir(SOURCE_DIR)
    for year in years:
        ans_dir = os.path.join(SOURCE_DIR, year, "Ans")
        dep_sub_file_names = os.listdir(ans_dir)  # department, subject
        for dep_sub_file_name in dep_sub_file_names:
            source_file_path = os.path.join(ans_dir, dep_sub_file_name)
            text = extract_text_from_pdf_page(source_file_path)
            cleaned_lines, remove_lines = clean_raw_text(text)

            meta_info = '\n'.join(remove_lines)
            meta_dict = extract_metadata(meta_info)
            #text = '\n'.join(cleaned_lines)
            answer_dict = lines_to_qa_dict(cleaned_lines)
            answer_dict = validate_answer_dict(answer_dict)

            meta_dict.update(answer_dict)

            base_name = f"{year}_{get_base_name(source_file_path)}"
            ans_save_file_path = os.path.join(DEST_DIR, base_name + ".json")
            json_dump(ans_save_file_path, meta_dict)
            #ans_txt_file_path = os.path.join(ans_txt_dir, base_name + '.txt')
            #txt_dump(ans_txt_file_path, '\n'.join(remove_lines))

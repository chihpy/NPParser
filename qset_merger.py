"""
這邊直接先分科，然後每科的資料夾有三年
"""
import os
from utils import json_load, json_dump, mkdir

def meta_file_name_extractor(file_name):
    info = file_name.strip('.json').split('_')
    year = info[0]
    subject = '_'.join(info[1:2])  # general, advanced
    department = '_'.join(info[3:])
    #print(f"year: {year}")
    #print(f"subject: {subject}")
    #print(f"department: {department}")
    return year, subject, department

if __name__ == '__main__':
    exam_dir = os.path.join("Data", 'exams')
    ans_dir = os.path.join("Data", 'ans')
    DEST_DIR = os.path.join("Data", 'NPQSet')
    exam_all_file_path = os.path.join("Data", '111-113_np.json')
    
    file_names = os.listdir(exam_dir)
    for file_name in file_names:
        year, subject, department = meta_file_name_extractor(file_name)

        save_dir = os.path.join(DEST_DIR, f"{subject}_{department}")
        mkdir(save_dir)
        
        # read exam
        exam_file_path = os.path.join(exam_dir, file_name)
        exam_data = json_load(exam_file_path)
        # read ans
        ans_file_path = os.path.join(ans_dir, file_name)
        ans_data = json_load(ans_file_path)

        # merge
        ans_dep = ans_data['department']
        ans_sub = ans_data['subject']
        for qset in exam_data:
            qset['ans'] = ans_data[str(qset['qid'])]
            #assert ans_dep == qset['department']
            #assert ans_sub == qset['subject']
            qset['department_en'] = department
            qset['subject_en'] = subject
        
        # dump
        save_file_path = os.path.join(save_dir, f'{year}.json')
        json_dump(save_file_path, exam_data)


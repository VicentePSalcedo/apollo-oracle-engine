from re import compile

from .db import insert_company
from .logger import log_info

LINE_SPLIT_PATTERN = compile(r'\s{2,}')

def parse_sunbiz_file(conn, input_file):
    with open(input_file, 'r', encoding='latin-1') as f_in:
        for i, line in enumerate(f_in):
            if not line.strip():
                continue
            parts = LINE_SPLIT_PATTERN.split(line.strip())

            if len(parts) >= 3:
                corp_num_and_name = parts[0]
                corp_num = corp_num_and_name[:12].strip()
                corp_name = corp_num_and_name[12:].strip().replace('\0', '')
                filing_type = parts[1].strip().replace('\0', '')
                address = ' '.join(parts[2:]).strip().replace('\0','')
                data = {
                    'corp_number': corp_num,
                    'name': corp_name,
                    'category': None,
                    'email': None,
                    'facebook': None,
                    'phone': None,
                    'contacted': False,
                    'unsubscribed': False,
                }

                insert_company(conn, data)
            else:
                log_info(f"Skipping line {i+1} because it has fewer than 3 parts: {line}")

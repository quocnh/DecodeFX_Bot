import re
from typing import List, Dict

class DatasetParser:
    def __init__(self):
        self.qa_pairs = []

    def parse_markdown_file(self, file_path: str) -> List[Dict]:
        """Parse the markdown dataset file into QA pairs"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split content into sections by question
            qa_blocks = re.findall(
                r'KHÁCH_HÀNG: "(.*?)"\n'
                r'BỐI_CẢNH: "(.*?)"\n'
                r'TRẢ_LỜI: "(.*?)"\n'
                r'NHÃN: \[(.*?)\]\n'
                r'ĐỘ_ƯU_TIÊN: "(.*?)"',
                content, re.DOTALL
            )

            # Convert blocks to structured data
            for block in qa_blocks:
                question, context, answer, labels, priority = block
                labels = [label.strip().strip('"') for label in labels.split(',')]
                
                qa_pair = {
                    'KHÁCH_HÀNG': question.strip(),
                    'BỐI_CẢNH': context.strip(),
                    'TRẢ_LỜI': answer.strip(),
                    'NHÃN': labels,
                    'ĐỘ_ƯU_TIÊN': priority.strip()
                }
                self.qa_pairs.append(qa_pair)

            return self.qa_pairs

        except Exception as e:
            print(f"Error parsing dataset: {str(e)}")
            return []

    def get_qa_pairs(self) -> List[Dict]:
        """Return the parsed QA pairs"""
        return self.qa_pairs

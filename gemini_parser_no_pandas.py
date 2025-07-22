import google.generativeai as genai
import json
import csv
from typing import Dict, Optional
import os

class GeminiParser:
    def __init__(self, api_key: str, csv_path: str = "res/GML25_F&B Menu.csv"):
        """Initialize Gemini API parser"""
        self.api_key = api_key
        self.csv_path = csv_path
        
        # Configure Gemini API
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Load CSV data for reference
        self.pairing_data = self.load_csv_data()
        
    def load_csv_data(self) -> str:
        """Load CSV data as string for context"""
        try:
            result_data = []
            
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                # Skip header rows until we find data
                data_start = 0
                for i, row in enumerate(rows):
                    if len(row) > 14 and row[8] and row[8].isdigit():
                        data_start = i
                        break
                
                # Process data rows
                for row in rows[data_start:]:
                    if len(row) > 14:
                        type_num = str(row[8]) if len(row) > 8 else ''
                        type_name = str(row[10]) if len(row) > 10 else ''
                        type_desc = str(row[11]) if len(row) > 11 else ''
                        drink = str(row[12]) if len(row) > 12 else ''
                        food = str(row[13]) if len(row) > 13 else ''
                        keyword = str(row[14]) if len(row) > 14 else ''
                        
                        # Skip rows without valid type numbers
                        if type_num and type_num.isdigit() and 1 <= int(type_num) <= 24:
                            if type_name and type_name not in ['nan', '']:
                                result_data.append({
                                    '번호': type_num,
                                    '타입명': type_name,
                                    '타입_설명': type_desc,
                                    '음료': drink,
                                    '푸드': food,
                                    '성향_키워드': keyword
                                })
            
            # Convert to readable string for Gemini
            if result_data:
                lines = []
                for item in result_data:
                    line = f"번호: {item['번호']}, 타입명: {item['타입명']}, 타입_설명: {item['타입_설명']}, 음료: {item['음료']}, 푸드: {item['푸드']}, 성향_키워드: {item['성향_키워드']}"
                    lines.append(line)
                return '\n'.join(lines)
            else:
                print("Warning: No valid data found in CSV")
                return ""
                
        except Exception as e:
            print(f"Error loading CSV: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def parse_conversation(self, conversation_text: str) -> Dict:
        """Parse conversation using Gemini API"""
        
        prompt = f"""
다음 대화에서 고객 정보를 추출해주세요. 대화에는 'Gems Station'이라는 키워드가 포함되어 있으며, 
고객의 성격 유형과 추천 메뉴가 언급됩니다.

참고 데이터 (타입별 정보):
{self.pairing_data}

대화 내용:
{conversation_text}

다음 형식의 JSON으로 응답해주세요:
{{
    "이름": "고객 이름 (없으면 '고객')",
    "번호": "타입 번호 (1-24 중 하나, 참고 데이터의 '번호' 컬럼 값을 사용)",
    "타입명": "성격 타입 이름 (예: Bold Creator)",
    "타입_설명": "타입에 대한 설명",
    "성향_키워드": "성향 키워드들 (# 포함)",
    "음료": "추천된 음료",
    "푸드": "추천된 음식"
}}

중요: 
- "번호"는 반드시 참고 데이터의 '번호' 컬럼에 있는 1-24 사이의 숫자여야 합니다.
- 대화에서 언급된 음료와 푸드의 조합으로 정확한 타입을 찾으세요.
- 예시:
  - Negroni + 코랄 소스의 랍스터 테일 = 타입 1 (Bold Creator)
  - 서빈버스트 + 망고크림새우 = 타입 12 (Universal Pleaser)
  - Blue Summer Cooler + 로스트 비프 토스트 = 타입 16 (Serene Provider)
- 반드시 음료와 푸드가 같은 타입 번호에 속하는지 확인하세요.

대화에서 직접 언급되지 않은 정보는 위의 참고 데이터에서 매칭되는 타입 정보를 사용하세요.
JSON만 응답하고 다른 설명은 포함하지 마세요.
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Extract JSON from response
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
                
            # Parse JSON
            parsed_data = json.loads(result_text)
            return parsed_data
            
        except Exception as e:
            print(f"Error parsing with Gemini: {e}")
            # Return default structure
            return {
                "이름": "고객",
                "번호": "1",
                "타입명": "Unknown",
                "타입_설명": "",
                "성향_키워드": "",
                "음료": "",
                "푸드": ""
            }
    
    def parse_and_save(self, conversation_text: str, output_path: str = "parsed_conversation.json") -> Dict:
        """Parse conversation and save as JSON"""
        result = self.parse_conversation(conversation_text)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"Saved parsed data to {output_path}")
        return result

# Example usage
if __name__ == "__main__":
    # You need to set your Gemini API key
    API_KEY = os.environ.get('GEMINI_API_KEY', 'your-api-key-here')
    
    parser = GeminiParser(API_KEY)
    
    # Example conversation
    example_text = """
    지수님을 위한 특별한 메뉴를 Gems Station에서 바로 준비해 드리겠습니다.
    지수님은 Bold Creator 타입으로 도전과 전략적 리더십을 추구하시는 분이시군요.
    네그로니와 코랄 소스의 랍스터 테일을 추천드립니다.
    """
    
    result = parser.parse_conversation(example_text)
    print(json.dumps(result, ensure_ascii=False, indent=2))
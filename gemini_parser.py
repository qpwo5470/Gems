import google.generativeai as genai
import json
import pandas as pd
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
            # Read CSV and handle potential empty columns
            df = pd.read_csv(self.csv_path, encoding='utf-8')
            
            # Find columns that contain the actual data (skip empty column names)
            actual_columns = [col for col in df.columns if not col.startswith('Unnamed')]
            
            # Try to find the correct columns by looking for key terms
            type_name_col = None
            type_desc_col = None
            drink_col = None
            food_col = None
            keyword_col = None
            
            for col in df.columns:
                if '타입명' in str(col):
                    type_name_col = col
                elif '타입 설명' in str(col):
                    type_desc_col = col
                elif '음료' in str(col) and '명칭' not in str(col):
                    drink_col = col
                elif '푸드' in str(col) and '명칭' not in str(col):
                    food_col = col
                elif '성향 키워드' in str(col):
                    keyword_col = col
            
            if not all([type_name_col, type_desc_col, drink_col, food_col, keyword_col]):
                # Fallback: try to use column positions
                print("Warning: Could not find all columns by name, using positions")
                cols = df.columns.tolist()
                # Based on the CSV structure, approximate positions
                for i, col in enumerate(cols):
                    if i >= 10 and not type_name_col and df[col].notna().sum() > 10:
                        type_name_col = col
                    elif i >= 11 and not type_desc_col and df[col].notna().sum() > 10:
                        type_desc_col = col
                    elif i >= 12 and not drink_col and df[col].notna().sum() > 10:
                        drink_col = col
                    elif i >= 13 and not food_col and df[col].notna().sum() > 10:
                        food_col = col
                    elif i >= 14 and not keyword_col and df[col].notna().sum() > 10:
                        keyword_col = col
            
            # Create a cleaned dataframe with found columns
            result_data = []
            if type_name_col:
                df_filtered = df[df[type_name_col].notna()]
                for _, row in df_filtered.iterrows():
                    if pd.notna(row.get(type_name_col, '')):
                        result_data.append({
                            '번호': str(row.get('No.', '')),
                            '타입명': str(row.get(type_name_col, '')),
                            '타입 설명': str(row.get(type_desc_col, '')) if type_desc_col else '',
                            '음료': str(row.get(drink_col, '')) if drink_col else '',
                            '푸드': str(row.get(food_col, '')) if food_col else '',
                            '성향 키워드': str(row.get(keyword_col, '')) if keyword_col else ''
                        })
            
            # Convert to readable string for Gemini
            if result_data:
                return pd.DataFrame(result_data).to_string(index=False)
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
    "번호": "타입 번호 (참고 데이터의 번호 컬럼)",
    "타입명": "성격 타입 이름 (예: Bold Creator)",
    "타입_설명": "타입에 대한 설명",
    "성향_키워드": "성향 키워드들 (# 포함)",
    "음료": "추천된 음료",
    "푸드": "추천된 음식"
}}

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
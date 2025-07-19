"""Test the Gemini parser to ensure it returns correct type numbers"""
import os
import json
from gemini_parser import GeminiParser

# Load API key
api_key = os.environ.get('GEMINI_API_KEY')
if not api_key:
    try:
        with open('gemini_api_key.txt', 'r') as f:
            api_key = f.read().strip()
    except:
        print("ERROR: No API key found")
        exit(1)

# Create parser
parser = GeminiParser(api_key, "res/GML25_F&B Menu.csv")

# Test cases
test_conversations = [
    """
    지수님을 위한 특별한 메뉴를 Gems Station에서 바로 준비해 드리겠습니다.
    지수님은 Bold Creator 타입으로 도전과 전략적 리더십을 추구하시는 분이시군요.
    네그로니와 코랄 소스의 랍스터 테일을 추천드립니다.
    """,
    """
    Gems Station에서 민준님을 위한 메뉴를 소개합니다.
    Unexpected Innovator 타입이신 민준님께는 
    네그로니와 파가든 브리오쉬 한우 버거를 추천드립니다.
    """,
    """
    서연님, Gems Station입니다.
    Future Seeker 타입으로 분석되었습니다.
    네그로니와 아보카도 리코타 치즈 토스트가 잘 어울릴 것 같습니다.
    """
]

print("Testing Gemini Parser...")
print("=" * 60)

for i, conversation in enumerate(test_conversations, 1):
    print(f"\nTest Case {i}:")
    print(f"Input: {conversation.strip()}")
    
    try:
        result = parser.parse_conversation(conversation)
        print(f"\nParsed Result:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # Verify type number
        if "번호" in result:
            print(f"\n✅ Type number: {result['번호']}")
            if i == 1 and result['번호'] != "1":
                print("⚠️  Warning: Expected type number 1 for Bold Creator")
            elif i == 2 and result['번호'] != "2":
                print("⚠️  Warning: Expected type number 2 for Unexpected Innovator")
            elif i == 3 and result['번호'] != "3":
                print("⚠️  Warning: Expected type number 3 for Future Seeker")
        else:
            print("❌ No type number found in result")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("-" * 60)
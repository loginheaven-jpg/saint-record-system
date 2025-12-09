"""Apps Script API 클라이언트 - ID 생성용"""

import requests
from typing import Optional

class AppsScriptClient:
    def __init__(self, script_url: str):
        """
        Args:
            script_url: Apps Script 웹앱 URL
        """
        self.script_url = script_url
    
    def generate_member_id(self) -> str:
        """새 성도 ID 생성"""
        return self._call_api('generateMemberId')
    
    def generate_family_id(self) -> str:
        """새 가정 ID 생성"""
        return self._call_api('generateFamilyId')
    
    def generate_event_id(self) -> str:
        """새 신앙이력 ID 생성"""
        return self._call_api('generateEventId')
    
    def _call_api(self, action: str) -> str:
        """Apps Script API 호출"""
        if not self.script_url:
            # URL이 없으면 Mock 동작 (마이그레이션 단계 등)
            import uuid
            return f"M{uuid.uuid4().hex[:5]}"

        try:
            response = requests.get(
                self.script_url,
                params={'action': action},
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('success'):
                return result['id']
            else:
                raise Exception(result.get('error', 'Unknown error'))
                
        except requests.RequestException as e:
            raise Exception(f'Apps Script API 호출 실패: {e}')

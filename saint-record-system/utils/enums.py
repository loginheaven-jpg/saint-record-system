from enum import Enum

class AttendType(str, Enum):
    """출석 유형"""
    PRESENT = '1'   # 출석
    ABSENT = '0'    # 결석
    ONLINE = '2'    # 온라인
    
    @property
    def display_name(self) -> str:
        """UI 표시용 한글명"""
        names = {
            '1': '출석',
            '0': '결석',
            '2': '온라인'
        }
        return names[self.value]
    
    @property
    def is_attended(self) -> bool:
        """출석으로 집계할지 여부"""
        return self.value in ('1', '2')
    
    @classmethod
    def from_display(cls, name: str) -> 'AttendType':
        """한글명에서 Enum으로 변환"""
        mapping = {
            '출석': cls.PRESENT,
            '결석': cls.ABSENT,
            '온라인': cls.ONLINE
        }
        return mapping.get(name, cls.ABSENT)


class MemberStatus(str, Enum):
    """성도 상태"""
    ACTIVE = '재적'
    TRANSFERRED = '전출'
    DECEASED = '사망'
    LONG_ABSENT = '장기장결'


class MemberType(str, Enum):
    """교인 구분"""
    FULL = '회원교인'
    REGISTERED = '등록교인'
    OTHER = '기타'


class ChurchRole(str, Enum):
    """교회 직분"""
    SENIOR_PASTOR = '담임목사'
    PASTOR = '목사'
    EVANGELIST = '강도사'
    ELDER = '장로'
    KWONSA = '권사'
    ORDAINED_DEACON = '안수집사'
    DEACON = '집사'
    MEMBER = '성도'


class GroupRole(str, Enum):
    """목장 직분"""
    LEADER = '목자'
    CO_LEADER = '목녀'
    MEMBER = '목원'

from enum import Enum

class AttendType(str, Enum):
    """출석 유형 (출석/결석 이원화)"""
    PRESENT = '1'   # 출석
    ABSENT = '0'    # 결석

    @property
    def display_name(self) -> str:
        """UI 표시용 한글명"""
        names = {
            '1': '출석',
            '0': '결석'
        }
        return names.get(self.value, '출석')

    @property
    def is_attended(self) -> bool:
        """출석으로 집계할지 여부"""
        return self.value == '1'

    @classmethod
    def from_display(cls, name: str) -> 'AttendType':
        """한글명에서 Enum으로 변환"""
        mapping = {
            '출석': cls.PRESENT,
            '결석': cls.ABSENT
        }
        return mapping.get(name, cls.ABSENT)

    @classmethod
    def from_value(cls, value: str) -> 'AttendType':
        """값에서 Enum으로 변환 (기존 '2' 온라인은 '1' 출석으로 처리)"""
        if value == '2':  # 기존 온라인 데이터는 출석으로 취급
            return cls.PRESENT
        return cls.PRESENT if value == '1' else cls.ABSENT


class MemberStatus(str, Enum):
    """성도 상태 - 출석률 모수는 '재적'"""
    ACTIVE = '재적'        # 정상 출석 (출석률 모수)
    TRANSFERRED = '전출'   # 다른 교회로 전출
    ON_LEAVE = '휴적'      # 일시적 휴직
    VISITOR = '방문'       # 방문자


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
    ASSISTANT = '목부'
    MEMBER = '목원'


class Relationship(str, Enum):
    """가족 관계"""
    HEAD = '가장'
    SPOUSE = '아내'
    SON = '아들'
    DAUGHTER = '딸'
    FATHER = '부친'
    MOTHER = '모친'
    GRANDSON = '손자'
    GRANDDAUGHTER = '손녀'
    BROTHER = '형제'
    SISTER = '자매'
    OTHER = '기타'


class BaptismStatus(str, Enum):
    """신급 (세례 상태)"""
    BAPTISM = '세례'
    CONFIRMATION = '입교'
    LEARNING = '학습'
    INFANT_BAPTISM = '유아세례'
    OTHER = '기타'

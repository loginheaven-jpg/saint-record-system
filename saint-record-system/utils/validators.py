from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date
from .enums import AttendType, MemberType, MemberStatus, ChurchRole, GroupRole, Relationship, BaptismStatus

class MemberBase(BaseModel):
    name: str = Field(..., min_length=1)
    dept_id: str
    group_id: str
    gender: str
    birth_date: Optional[date]
    lunar_solar: str = 'Y'
    phone: str
    address: Optional[str]
    church_role: str = ChurchRole.MEMBER.value
    group_role: str = GroupRole.MEMBER.value
    member_type: str = MemberType.REGISTERED.value
    status: str = MemberStatus.ACTIVE.value
    relationship: str = Relationship.OTHER.value  # 가족관계
    baptism_status: Optional[str] = None  # 신급 (세례/입교/학습/유아세례/기타)
    register_date: Optional[date] = None  # 교회등록일
    photo_url: Optional[str] = ''

class MemberCreate(MemberBase):
    """성도 생성 모델"""
    family_id: Optional[str] = None # 생성 시에는 없을 수도 있음 or 자동생성

class MemberUpdate(BaseModel):
    """성도 수정 모델 - 모든 필드 Optional"""
    name: Optional[str] = None
    dept_id: Optional[str] = None
    group_id: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    lunar_solar: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    church_role: Optional[str] = None
    group_role: Optional[str] = None
    member_type: Optional[str] = None
    status: Optional[str] = None
    relationship: Optional[str] = None  # 가족관계
    baptism_status: Optional[str] = None  # 신급
    register_date: Optional[date] = None  # 교회등록일
    photo_url: Optional[str] = None
    family_id: Optional[str] = None

class AttendanceCreate(BaseModel):
    """출석 저장 모델"""
    member_id: str
    attend_date: date
    attend_type: AttendType
    year: int
    week_no: int

    @validator('year')
    def validate_year(cls, v):
        if v < 2000 or v > 2100:
            raise ValueError('Invalid year')
        return v

    @validator('week_no')
    def validate_week_no(cls, v):
        if v < 1 or v > 53:
            raise ValueError('Invalid week number')
        return v

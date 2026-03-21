"""
Django Allauth 社交帳戶適配器 (SocialAccountAdapter)

負責在 Google OAuth 登入成功後，自動解析學號並提取使用者資訊。
遵循 4 層正規化資料庫架構，透過嚴格的 ORM 查詢綁定系所與年級。
"""

import logging
from typing import Optional, Dict, Any

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from django.db.models import Q

from accounts.student_parser import parse_student_number
from core.models import Campus, ProgramType, Department

User = get_user_model()
logger = logging.getLogger(__name__)


class StudentInfoSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    自訂 Allauth SocialAccountAdapter，在 Google 登入後自動解析學號並綁定學制/系所資訊。
    
    主要功能：
    1. 從 Google 帳戶提取學號（假設在 email local part 中）
    2. 呼叫 student_parser.parse_student_number() 解析學號
    3. 透過 ORM 查詢找出對應的 Campus, ProgramType, Department
    4. 更新或建立 UserProfile，設定 grade_no 與 department FK
    5. 完整的異常捕捉與防禦性設計，確保登入流程不中斷
    """

    def pre_social_login(self, request, sociallogin):
        """
        在社交登入之前被呼叫，用於處理登入前邏輯。
        這裡我們在此階段新增學號解析與檢驗。
        """
        # 暫時不在此階段執行，改在 populate_user 中處理
        super().pre_social_login(request, sociallogin)

    def populate_user(self, request, sociallogin, data) -> User:
        """
        根據社交帳戶資料建立或更新使用者物件。
        在此階段進行學號解析與 UserProfile 更新。
        
        Args:
            request: HTTP request 物件
            sociallogin: SocialLogin 物件
            data: 社交帳戶回傳的使用者資料字典
        
        Returns:
            User: 已填充資料的使用者物件
        """
        user = super().populate_user(request, sociallogin, data)
        
        try:
            # ===== 提取 Email 並解析學號 =====
            email = data.get('email', '') or user.email
            if email and '@ntub.edu.tw' in email:
                student_no = email.split('@')[0]  # 從 email local part 提取
                
                # 呼叫純解析邏輯
                parsed_info = parse_student_number(student_no)
                
                # 檢查解析是否成功
                if parsed_info['errors']:
                    logger.warning(
                        f"Failed to parse student number for {email}: "
                        f"{', '.join(parsed_info['errors'])}"
                    )
                    # 不中斷登入流程，繼續執行
                else:
                    # 成功解析，儲存到 request 物件供後續處理
                    # (在 allauth 的 post_social_login 或其他信號中使用)
                    request.parsed_student_info = parsed_info
                    logger.info(f"Successfully parsed student info for {email}")
            else:
                logger.warning(f"User {email} is not a campus account (@ntub.edu.tw)")
        
        except Exception as e:
            logger.error(
                f"Exception during populate_user: {str(e)}", exc_info=True
            )
            # 不中斷登入，繼續執行
        
        return user

    def save_user(self, request, sociallogin, form=None) -> User:
        """
        儲存使用者，並在此階段執行 UserProfile 的更新邏輯。
        
        Args:
            request: HTTP request 物件
            sociallogin: SocialLogin 物件
            form: (可選) 表單物件
        
        Returns:
            User: 已儲存的使用者物件
        """
        user = super().save_user(request, sociallogin, form)
        
        try:
            # 檢查 populate_user 中是否已解析學號
            parsed_info = getattr(request, 'parsed_student_info', None)
            
            if parsed_info and not parsed_info['errors']:
                # 執行 UserProfile 的綁定與更新
                self._update_user_profile(user, parsed_info)
            else:
                logger.warning(
                    f"No parsed student info for user {user.username}, "
                    f"UserProfile will remain empty"
                )
        
        except Exception as e:
            logger.error(
                f"Exception during save_user: {str(e)}", exc_info=True
            )
            # 不中斷登入，使用者已建立，只是 UserProfile 可能不完整
        
        return user

    def _update_user_profile(self, user: User, parsed_info: Dict[str, Any]) -> None:
        """
        根據解析的學號資訊更新或建立 UserProfile。
        
        遵循 4 層正規化架構，嚴格透過 ORM 查詢：
        1. Campus.objects.filter(name_zh=campus_name).first()
        2. ProgramType.objects.filter(code=program_type_code).first()
        3. Department.objects.filter(campus=..., program_type=..., code=...).first()
        
        Args:
            user: 使用者物件
            parsed_info: parse_student_number() 的回傳字典
        """
        try:
            from accounts.models import UserProfile
            
            # 取出關鍵資訊
            campus_name = parsed_info.get('campus_name')
            program_type_digit = parsed_info.get('program_type_digit')
            campus_dept_digit = parsed_info.get('campus_dept_digit')
            grade_no = parsed_info.get('grade_no')
            student_no = parsed_info.get('student_no')
            
            # ===== 逐序查詢，遵循 4 層正規化 =====
            
            # 1. 查詢 Campus
            campus_obj = None
            if campus_name:
                campus_obj = Campus.objects.filter(
                    name_zh=campus_name
                ).first()
                
                if not campus_obj:
                    logger.warning(
                        f"Campus '{campus_name}' not found in database for student {student_no}"
                    )
            
            # 2. 查詢 ProgramType
            program_type_obj = None
            program_type_code = self._get_program_type_code(program_type_digit)
            if program_type_code:
                program_type_obj = ProgramType.objects.filter(
                    code=program_type_code
                ).first()
                
                if not program_type_obj:
                    logger.warning(
                        f"ProgramType '{program_type_code}' not found in database for student {student_no}"
                    )
            
            # 3. 查詢 Department (最關鍵：需要三層條件)
            department_obj = None
            if campus_obj and program_type_obj and campus_dept_digit:
                department_obj = Department.objects.filter(
                    campus=campus_obj,
                    program_type=program_type_obj,
                    code=campus_dept_digit
                ).first()
                
                if not department_obj:
                    logger.warning(
                        f"Department not found for campus={campus_name}, "
                        f"program_type={program_type_code}, "
                        f"code={campus_dept_digit} for student {student_no}"
                    )
            
            # ===== 建立或更新 UserProfile =====
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            
            # 更新後端資訊
            user_profile.student_no = student_no
            user_profile.program_type = program_type_obj  # 可能為 None
            user_profile.department = department_obj  # 可能為 None
            user_profile.grade_no = grade_no  # 整數，已由 parser 計算
            
            # display_name 預設值：若未設定，使用 first_name 或 email local part
            if not user_profile.display_name:
                user_profile.display_name = (
                    user.first_name 
                    or user.email.split('@')[0] 
                    or user.username
                )
            
            user_profile.save()
            
            logger.info(
                f"Successfully updated UserProfile for {user.username}: "
                f"student_no={student_no}, "
                f"program_type={program_type_obj}, "
                f"department={department_obj}, "
                f"grade_no={grade_no}"
            )
        
        except ImportError:
            logger.error("Cannot import UserProfile model")
        except Exception as e:
            logger.error(
                f"Exception during _update_user_profile: {str(e)}", 
                exc_info=True
            )

    @staticmethod
    def _get_program_type_code(program_type_digit: str) -> Optional[str]:
        """
        根據學制代碼轉換為 ProgramType.code。
        
        Args:
            program_type_digit: 學號第 4 碼 (3, 4, 或 5)
        
        Returns:
            str: ProgramType.code，或 None (若無效)
        """
        mapping = {
            '3': '3',  # 二技日間部
            '4': '4',  # 四技日間部
            '5': '5',  # 五專日間部
        }
        return mapping.get(program_type_digit)

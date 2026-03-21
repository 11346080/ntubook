"""
學號解析邏輯模組
純解析邏輯，不涉及資料庫查詢，返回字典供 adapter.py 使用。

學號規則 (共 8 碼，例如：11346001)：
1. 位數 1-3：入學年份（民國年）- 動態計算年級
2. 位數 4：學制代碼 - 3:二技日間部, 4:四技日間部, 5:五專日間部
3. 位數 5：校區與系所代碼
   - 數字 1-7：臺北校區 (1會計, 2財經, 3財稅, 4國商, 5企管, 6資管, 7應外)
   - 字母 A-C：桃園校區 (A創設, B商設, C數媒)
4. 位數 6-8：班級與流水號
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ========== Mapping Dictionaries ==========

# 學制代碼對應表
PROGRAM_TYPE_MAPPING = {
    '3': {
        'code': '3',
        'name_zh': '二技日間部',
    },
    '4': {
        'code': '4',
        'name_zh': '四技日間部',
    },
    '5': {
        'code': '5',
        'name_zh': '五專日間部',
    },
}

# 臺北校區 - 系所代碼對應表
TAIPEI_DEPARTMENTS = {
    '1': {
        'code': '1',
        'name_zh': '會計系',
    },
    '2': {
        'code': '2',
        'name_zh': '財經系',
    },
    '3': {
        'code': '3',
        'name_zh': '財稅系',
    },
    '4': {
        'code': '4',
        'name_zh': '國商系',
    },
    '5': {
        'code': '5',
        'name_zh': '企管系',
    },
    '6': {
        'code': '6',
        'name_zh': '資管系',
    },
    '7': {
        'code': '7',
        'name_zh': '應外系',
    },
}

# 桃園校區 - 系所代碼對應表
TAOYUAN_DEPARTMENTS = {
    'A': {
        'code': 'A',
        'name_zh': '創設系',
    },
    'B': {
        'code': 'B',
        'name_zh': '商設系',
    },
    'C': {
        'code': 'C',
        'name_zh': '數媒系',
    },
}


# ========== Core Parser Functions ==========

def calculate_current_academic_year() -> int:
    """
    計算當前學年度（民國年）。
    
    邏輯：
    - 當前月份 < 8：當前民國年 - 1
    - 當前月份 >= 8：當前民國年
    
    Returns:
        int: 當前學年度（民國年），例如 112
    """
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    
    # 轉換為民國年
    current_republic_year = current_year - 1911
    
    # 判斷學年度
    if current_month < 8:
        academic_year = current_republic_year - 1
    else:
        academic_year = current_republic_year
    
    return academic_year


def parse_student_number(student_no: str) -> dict:
    """
    解析學號，提取與計算必要的資訊。
    
    Args:
        student_no (str): 學號 (8 碼)，例如 '11346001'
    
    Returns:
        dict: 包含以下鍵值對的字典：
            - 'student_no' (str): 原始學號
            - 'admission_year' (int): 入學民國年 (前 3 碼)
            - 'program_type_digit' (str): 學制代碼 (第 4 碼)
            - 'campus_dept_digit' (str): 校區與系所代碼 (第 5 碼)
            - 'is_taipei' (bool): 是否為臺北校區
            - 'is_taoyuan' (bool): 是否為桃園校區
            - 'grade_no' (int): 計算後的年級 (1-5 之間)
            - 'program_type_info' (dict 或 None): 學制對應資訊
            - 'campus_name' (str): 校區名稱
            - 'department_info' (dict 或 None): 系所對應資訊
            - 'errors' (list): 錯誤訊息列表 (驗證失敗時填充)
    """
    result = {
        'student_no': student_no,
        'admission_year': None,
        'program_type_digit': None,
        'campus_dept_digit': None,
        'is_taipei': False,
        'is_taoyuan': False,
        'grade_no': None,
        'program_type_info': None,
        'campus_name': None,
        'department_info': None,
        'errors': [],
    }
    
    # ===== 驗證學號格式 =====
    if not student_no or len(student_no) != 8:
        result['errors'].append(f"學號必須為 8 碼，收到 {len(student_no) if student_no else 0} 碼")
        logger.warning(f"Invalid student number format: {student_no}")
        return result
    
    try:
        # ===== 提取各位置的代碼 =====
        admission_year_str = student_no[0:3]
        program_type_digit = student_no[3]
        campus_dept_digit = student_no[4]
        
        # 轉換為整數驗證
        admission_year = int(admission_year_str)
        
        result['admission_year'] = admission_year
        result['program_type_digit'] = program_type_digit
        result['campus_dept_digit'] = campus_dept_digit
        
        # ===== 驗證學制代碼 (第 4 碼) =====
        if program_type_digit not in PROGRAM_TYPE_MAPPING:
            result['errors'].append(
                f"無效的學制代碼 '{program_type_digit}'。"
                f"應為 3(二技日間部), 4(四技日間部), 或 5(五專日間部)"
            )
            logger.warning(f"Invalid program type digit: {program_type_digit}")
            return result
        
        result['program_type_info'] = PROGRAM_TYPE_MAPPING[program_type_digit]
        
        # ===== 判斷校區並驗證系所代碼 (第 5 碼) =====
        if campus_dept_digit.isdigit():
            # 臺北校區（數字 1-7）
            if campus_dept_digit not in TAIPEI_DEPARTMENTS:
                result['errors'].append(
                    f"無效的臺北校區系所代碼 '{campus_dept_digit}'。"
                    f"應為 1-7 之間的數字"
                )
                logger.warning(f"Invalid Taipei department digit: {campus_dept_digit}")
                return result
            
            result['is_taipei'] = True
            result['campus_name'] = '臺北校區'
            result['department_info'] = TAIPEI_DEPARTMENTS[campus_dept_digit]
        
        elif campus_dept_digit.isalpha():
            # 桃園校區（字母 A-C）
            campus_dept_upper = campus_dept_digit.upper()
            if campus_dept_upper not in TAOYUAN_DEPARTMENTS:
                result['errors'].append(
                    f"無效的桃園校區系所代碼 '{campus_dept_digit}'。"
                    f"應為 A-C 之間的字母"
                )
                logger.warning(f"Invalid Taoyuan department digit: {campus_dept_digit}")
                return result
            
            result['is_taoyuan'] = True
            result['campus_name'] = '桃園校區'
            result['campus_dept_digit'] = campus_dept_upper  # 統一為大寫
            result['department_info'] = TAOYUAN_DEPARTMENTS[campus_dept_upper]
        
        else:
            result['errors'].append(
                f"校區與系所代碼必須為數字(1-7)或字母(A-C)，收到 '{campus_dept_digit}'"
            )
            logger.warning(f"Invalid campus-dept digit type: {campus_dept_digit}")
            return result
        
        # ===== 動態計算年級 =====
        current_academic_year = calculate_current_academic_year()
        grade_no = current_academic_year - admission_year + 1
        
        # 驗證年級合理性 (應在 1-5 之間)
        if grade_no < 1 or grade_no > 5:
            logger.warning(
                f"Calculated grade {grade_no} is out of range (1-5) "
                f"for student {student_no}. "
                f"Current academic year: {current_academic_year}, "
                f"admission year: {admission_year}"
            )
        
        # 即使年級超出範圍，仍然設定值（防禦性設計，不中斷流程）
        result['grade_no'] = max(1, grade_no)  # 保證至少為 1
        
        logger.info(
            f"Successfully parsed student number {student_no}: "
            f"admission_year={admission_year}, "
            f"program_type={program_type_digit}, "
            f"campus={result['campus_name']}, "
            f"dept_code={result['campus_dept_digit']}, "
            f"grade={result['grade_no']}"
        )
        
        return result
    
    except (ValueError, IndexError) as e:
        result['errors'].append(f"學號解析發生異常: {str(e)}")
        logger.error(f"Exception while parsing student number {student_no}: {str(e)}", exc_info=True)
        return result


# ========== Helper Functions ==========

def get_program_type_code(program_type_digit: str) -> str:
    """根據學制代碼取得 ProgramType.code"""
    info = PROGRAM_TYPE_MAPPING.get(program_type_digit, {})
    return info.get('code', '')


def get_campus_query_name(campus_name: str) -> str:
    """根據校區名稱取得資料庫查詢使用的名稱"""
    # Campus.name_zh 直接使用校區名稱
    return campus_name


def get_department_code(campus_dept_digit: str, is_taipei: bool) -> str:
    """根據校區與系所代碼取得 Department.code"""
    if is_taipei:
        info = TAIPEI_DEPARTMENTS.get(campus_dept_digit, {})
    else:
        info = TAOYUAN_DEPARTMENTS.get(campus_dept_digit, {})
    return info.get('code', '')

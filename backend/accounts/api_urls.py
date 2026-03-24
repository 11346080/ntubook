from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt

from . import views
from .jwt_auth import generate_app_token
from .models import User
from django.conf import settings
import secrets

# ============================================================================
# 嘗試導入新的 API v2 視圖 (如果存在)
# Try to import new API v2 views (if available)
# ============================================================================
try:
    from .api_views import me_api as me_api_v2, user_profile_api, create_profile_api
    HAS_API_V2 = True
except ImportError:
    HAS_API_V2 = False


def _verify_bootstrap_secret(request) -> tuple[bool, str]:
    """Return (is_valid, error_message)."""
    secret = request.headers.get('X-Bootstrap-Secret', '')
    expected = getattr(settings, 'DJANGO_BOOTSTRAP_SECRET', '')
    if not expected:
        return False, 'BOOTSTRAP_ENDPOINT_DISABLED'
    if not secrets.compare_digest(secret, expected):
        return False, 'INVALID_BOOTSTRAP_SECRET'
    return True, ''


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def bootstrap_api(request):
    """
    POST /api/accounts/bootstrap/

    Request body:
        {
            "google_sub": "...",
            "email": "user@ntub.edu.tw",
            "name": "...",
            "picture": "..." (optional)
        }

    Response:
        200: { "app_token": "<jwt>", "is_new_user": bool, "has_profile": bool }
        400: { "error": "MISSING_FIELDS" }
        401: { "error": "INVALID_BOOTSTRAP_SECRET" | "BOOTSTRAP_ENDPOINT_DISABLED" }
        409: { "error": "DUPLICATE_GOOGLE_SUB" } | { "error": "MULTIPLE_ACCOUNTS_WITH_SAME_EMAIL", "reason": "manual_link_required" }
        403: { "error": "LINKING_PROTECTED", "reason": "superuser"|"staff"|"account_status"|"inactive" }
    """
    # 1. Verify bootstrap secret
    valid, err = _verify_bootstrap_secret(request)
    if not valid:
        return Response({'error': err}, status=401)

    # 2. Validate required fields
    google_sub = (request.data.get('google_sub') or '').strip()
    email = (request.data.get('email') or '').strip().lower()

    if not google_sub or not email:
        return Response({'error': 'MISSING_FIELDS'}, status=400)

    # 3. Step 1: look up by google_sub
    existing_by_google_sub = User.objects.filter(google_sub=google_sub)
    count_by_google_sub = existing_by_google_sub.count()

    if count_by_google_sub == 1:
        user = existing_by_google_sub.first()
        has_profile = hasattr(user, 'profile')
        app_token = generate_app_token(user)
        return Response({
            'app_token': app_token,
            'is_new_user': False,
            'has_profile': has_profile,
        })

    if count_by_google_sub > 1:
        return Response({'error': 'DUPLICATE_GOOGLE_SUB'}, status=409)

    # 4. Step 2: look up by email (google_sub IS NULL)
    existing_by_email = User.objects.filter(email=email, google_sub__isnull=True)
    count_by_email = existing_by_email.count()

    if count_by_email > 1:
        return Response({
            'error': 'MULTIPLE_ACCOUNTS_WITH_SAME_EMAIL',
            'reason': 'manual_link_required',
        }, status=409)

    if count_by_email == 1:
        user = existing_by_email.first()
        # Check protection conditions
        if user.is_superuser:
            return Response({'error': 'LINKING_PROTECTED', 'reason': 'superuser'}, status=403)
        if user.is_staff:
            return Response({'error': 'LINKING_PROTECTED', 'reason': 'staff'}, status=403)
        if user.account_status != 'ACTIVE':
            return Response({'error': 'LINKING_PROTECTED', 'reason': 'account_status'}, status=403)
        if not user.is_active:
            return Response({'error': 'LINKING_PROTECTED', 'reason': 'inactive'}, status=403)

        # Auto-link: set google_sub
        user.google_sub = google_sub
        user.save(update_fields=['google_sub', 'updated_at'])
        has_profile = hasattr(user, 'profile')
        app_token = generate_app_token(user)
        return Response({
            'app_token': app_token,
            'is_new_user': False,
            'has_profile': has_profile,
        })

    # 5. Step 3: create new user
    local_part = email.split('@')[0]
    base_username = local_part
    candidate = base_username
    suffix = 0
    while User.objects.filter(username=candidate).exists():
        suffix += 1
        candidate = f'{base_username}_{google_sub[-8:]}_{suffix}'

    user = User.objects.create(
        username=candidate,
        email=email,
        google_sub=google_sub,
        auth_provider='GOOGLE',
    )
    has_profile = False
    app_token = generate_app_token(user)
    return Response({
        'app_token': app_token,
        'is_new_user': True,
        'has_profile': has_profile,
    })


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def me_api(request):
    """
    GET /api/accounts/me/

    Reads app_token from X-App-Token header (forwarded by Next.js Route Handler).
    Returns user info + profile completeness flag.

    200: { "user_id": int, "email": str, "has_profile": bool, "account_status": str }
    401: { "error": "Unauthorized" | "Invalid token" | "Token expired" | "User not found" }
    """
    from .jwt_auth import verify_app_token
    from .models import User

    # Read from X-App-Token header (forwarded by Next.js Route Handler)
    token = request.headers.get('X-App-Token', '')
    if not token:
        return Response({'error': 'Unauthorized'}, status=401)

    payload = verify_app_token(token)
    if payload is None:
        return Response({'error': 'Invalid token'}, status=401)

    try:
        user = User.objects.get(id=payload['user_id'])
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=401)

    has_profile = hasattr(user, 'profile')
    return Response({
        'user_id': user.id,
        'email': user.email,
        'has_profile': has_profile,
        'account_status': user.account_status,
    })


@csrf_exempt
@api_view(['GET', 'POST', 'PATCH'])
@permission_classes([AllowAny])
def profile_create_or_update_api(request):
    """
    GET  /api/accounts/profile/  — read current profile
    POST /api/accounts/profile/  — create new profile
    PATCH /api/accounts/profile/ — update existing profile

    Reads app_token from X-App-Token header.
    """
    from .jwt_auth import verify_app_token
    from .models import User, UserProfile
    from django.db import transaction

    token = request.headers.get('X-App-Token', '')
    if not token:
        return Response({'error': 'Unauthorized'}, status=401)

    payload = verify_app_token(token)
    if payload is None:
        return Response({'error': 'Invalid token'}, status=401)

    try:
        user = User.objects.get(id=payload['user_id'])
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=401)

    try:
        profile = user.profile
        has_existing = True
    except UserProfile.DoesNotExist:
        has_existing = False
        profile = None

    # GET
    if request.method == 'GET':
        if not has_existing:
            return Response({'error': 'Profile not found'}, status=404)
        return Response(_profile_response(profile))

    if request.method == 'POST':
        if has_existing:
            return Response({'error': 'PROFILE_EXISTS'}, status=409)

        display_name = (request.data.get('display_name') or '').strip()
        if not display_name:
            return Response({'error': 'MISSING_FIELDS', 'fields': ['display_name']}, status=400)

        program_type = _resolve_program_type(request.data.get('program_type_id'))
        department = _resolve_department(request.data.get('department_id'))
        class_group = _resolve_class_group(request.data.get('class_group_id'))
        student_no = (request.data.get('student_no') or '').strip() or None
        contact_email = (request.data.get('contact_email') or '').strip() or None

        if program_type is False or department is False or class_group is False:
            return Response({'error': 'INVALID_REFERENCE'}, status=400)

        with transaction.atomic():
            profile = UserProfile.objects.create(
                user=user,
                display_name=display_name,
                student_no=student_no,
                contact_email=contact_email,
                program_type=program_type,
                department=department,
                class_group=class_group,
                grade_no=request.data.get('grade_no'),
            )

        return Response(_profile_response(profile), status=201)

    # PATCH
    if not has_existing:
        return Response({'error': 'Profile not found'}, status=404)

    if 'display_name' in request.data:
        display_name = (request.data.get('display_name') or '').strip()
        if not display_name:
            return Response({'error': 'Display name cannot be empty'}, status=400)
        profile.display_name = display_name

    if 'student_no' in request.data:
        profile.student_no = (request.data.get('student_no') or '').strip() or None

    if 'contact_email' in request.data:
        profile.contact_email = (request.data.get('contact_email') or '').strip() or None

    if 'program_type_id' in request.data:
        value = request.data.get('program_type_id')
        if value:
            pt = _resolve_program_type(value)
            if pt is False:
                return Response({'error': 'INVALID_PROGRAM_TYPE'}, status=400)
            profile.program_type = pt
        else:
            profile.program_type = None

    if 'department_id' in request.data:
        value = request.data.get('department_id')
        if value:
            dept = _resolve_department(value)
            if dept is False:
                return Response({'error': 'INVALID_DEPARTMENT'}, status=400)
            profile.department = dept
        else:
            profile.department = None

    if 'class_group_id' in request.data:
        value = request.data.get('class_group_id')
        if value:
            cg = _resolve_class_group(value)
            if cg is False:
                return Response({'error': 'INVALID_CLASS_GROUP'}, status=400)
            profile.class_group = cg
        else:
            profile.class_group = None

    if 'grade_no' in request.data:
        profile.grade_no = request.data.get('grade_no')

    profile.save()
    return Response(_profile_response(profile))


def _resolve_program_type(value):
    if not value:
        return None
    try:
        from core.models import ProgramType
        return ProgramType.objects.get(id=int(value))
    except (ValueError, TypeError):
        return False
    except Exception:
        return False


def _resolve_department(value):
    if not value:
        return None
    try:
        from core.models import Department
        return Department.objects.get(id=int(value))
    except (ValueError, TypeError):
        return False
    except Exception:
        return False


def _resolve_class_group(value):
    if not value:
        return None
    try:
        from core.models import ClassGroup
        return ClassGroup.objects.get(id=int(value))
    except (ValueError, TypeError):
        return False
    except Exception:
        return False


def _profile_response(profile):
    return {
        'id': profile.id,
        'display_name': profile.display_name,
        'student_no': profile.student_no,
        'program_type_id': profile.program_type.id if profile.program_type else None,
        'department_id': profile.department.id if profile.department else None,
        'class_group_id': profile.class_group.id if profile.class_group else None,
        'grade_no': profile.grade_no,
        'contact_email': profile.contact_email,
        'avatar_url': profile.avatar_url,
    }


urlpatterns = [
    path('bootstrap/', bootstrap_api, name='api-bootstrap'),
    path('me/', me_api, name='api-me'),
    path('profile/', profile_create_or_update_api, name='api-profile'),
    path('profiles/', views.userprofile_list_api, name='api-userprofile-list'),
]

# 如果 API v2 可用，添加 v2 路由
if HAS_API_V2:
    urlpatterns += [
        path('v2/me/', me_api_v2, name='api-me-v2'),
        path('v2/profile/', user_profile_api, name='api-profile-v2'),
        path('v2/profile/create/', create_profile_api, name='api-profile-create-v2'),
    ]

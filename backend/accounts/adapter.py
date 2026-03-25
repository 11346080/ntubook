"""
Django Allauth SocialAccountAdapter for NTUBook.

NOTE: The student number auto-parsing and auto-fill feature has been DISABLED.
Academic info (program_type, department, class_group, grade_no) must now be
filled manually by users on the /first-login page.
This adapter is kept for general social login flow.
"""

import logging
from typing import Optional, Dict, Any

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


class StudentInfoSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom Allauth SocialAccountAdapter.

    NOTE: Student number auto-parsing and auto-fill is DISABLED.
    Academic info (program_type, department, class_group, grade_no) must be
    filled manually by the user on the /first-login page.
    This adapter is kept for general social login flow.
    """

    def pre_social_login(self, request, sociallogin):
        """
        Called before social login.
        NOTE: Auto-parsing is disabled.
        """
        super().pre_social_login(request, sociallogin)

    def populate_user(self, request, sociallogin, data) -> User:
        """
        Populate user from social account data.

        NOTE: Auto-parsing is DISABLED.
        Academic info must be filled manually on /first-login page.
        """
        user = super().populate_user(request, sociallogin, data)
        return user

    def save_user(self, request, sociallogin, form=None) -> User:
        """
        Save user and handle social login completion.

        NOTE: _update_user_profile is DISABLED.
        Profile (academic info) is filled manually on /first-login page.
        """
        user = super().save_user(request, sociallogin, form)
        try:
            parsed_info = getattr(request, 'parsed_student_info', None)
            if parsed_info and not parsed_info['errors']:
                logger.info(
                    "Parsed student info for %s: student_no=%s, "
                    "but profile update is DISABLED -- user fills via first-login page",
                    user.username,
                    parsed_info.get('student_no'),
                )
            else:
                logger.info("No parsed student info for user %s", user.username)
        except Exception as e:
            logger.error("Exception during save_user: %s", str(e))
        return user

    # NOTE: _update_user_profile and _get_program_type_code are DISABLED.
    # They are kept as stubs to avoid breaking any references.
    # All academic profile fields are now filled manually on /first-login page.

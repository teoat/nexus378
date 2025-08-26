#!/usr/bin/env python3
"""
Frenly User Management Integration Service

This service integrates Frenly with the main Nexus platform's user management system,
providing unified user authentication, profile synchronization, and session management.
"""

import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from agents.frenly_meta_agent import FrenlyMetaAgent, AppCommand

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    """Represents a user profile from the main platform."""
    id: str
    username: str
    email: str
    role: str
    permissions: List[str]
    status: str
    created_at: datetime
    last_login: Optional[datetime] = None
    preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserSession:
    """Represents a user session."""
    session_id: str
    user_id: str
    username: str
    role: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    is_active: bool = True


class FrenlyUserIntegration:
    """
    Integrates Frenly with the main Nexus platform's user management.
    
    This service provides:
    - User profile synchronization
    - Unified session management
    - Permission inheritance
    - User activity tracking
    """
    
    def __init__(self, frenly_agent: FrenlyMetaAgent):
        """Initialize the user integration service."""
        self.frenly_agent = frenly_agent
        
        # Configuration for main platform integration
        self.main_platform_config = {
            "base_url": "http://localhost:8000",  # Main platform API base URL
            "auth_endpoint": "/api/auth",
            "users_endpoint": "/api/users",
            "sessions_endpoint": "/api/sessions",
            "timeout": 10
        }
        
        # User cache
        self.user_cache: Dict[str, UserProfile] = {}
        self.session_cache: Dict[str, UserSession] = {}
        self.cache_ttl = 300  # 5 minutes
        
        # User activity tracking
        self.user_activities: List[Dict[str, Any]] = []
        self.max_activities = 1000
        
        logger.info("Frenly User Integration Service initialized")
    
    def set_main_platform_config(self, base_url: str, auth_endpoint: str = None, 
                                users_endpoint: str = None, sessions_endpoint: str = None):
        """Update main platform configuration."""
        self.main_platform_config["base_url"] = base_url
        if auth_endpoint:
            self.main_platform_config["auth_endpoint"] = auth_endpoint
        if users_endpoint:
            self.main_platform_config["users_endpoint"] = users_endpoint
        if sessions_endpoint:
            self.main_platform_config["sessions_endpoint"] = sessions_endpoint
        
        logger.info(f"Updated main platform configuration: {base_url}")
    
    def validate_user_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate a user token with the main platform."""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{self.main_platform_config['base_url']}{self.main_platform_config['auth_endpoint']}/validate",
                headers=headers,
                timeout=self.main_platform_config["timeout"]
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Token validation failed: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error validating token: {e}")
            return None
    
    def get_user_profile(self, user_id: str, force_refresh: bool = False) -> Optional[UserProfile]:
        """Get user profile from main platform or cache."""
        # Check cache first
        if not force_refresh and user_id in self.user_cache:
            cached_profile = self.user_cache[user_id]
            if (datetime.now() - cached_profile.created_at).total_seconds() < self.cache_ttl:
                return cached_profile
        
        try:
            # Fetch from main platform
            response = requests.get(
                f"{self.main_platform_config['base_url']}{self.main_platform_config['users_endpoint']}/{user_id}",
                timeout=self.main_platform_config["timeout"]
            )
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Parse dates
                created_at = datetime.fromisoformat(user_data["created_at"])
                last_login = datetime.fromisoformat(user_data["last_login"]) if user_data.get("last_login") else None
                
                profile = UserProfile(
                    id=user_data["id"],
                    username=user_data["username"],
                    email=user_data["email"],
                    role=user_data["role"],
                    permissions=user_data.get("permissions", []),
                    status=user_data.get("status", "active"),
                    created_at=created_at,
                    last_login=last_login,
                    preferences=user_data.get("preferences", {})
                )
                
                # Cache the profile
                self.user_cache[user_id] = profile
                
                logger.info(f"Retrieved user profile: {username}")
                return profile
                
            else:
                logger.warning(f"Failed to get user profile: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting user profile: {e}")
            return None
    
    def create_user_session(self, user_id: str, token: str, expires_in: int = 3600) -> Optional[UserSession]:
        """Create a new user session."""
        try:
            # Get user profile
            profile = self.get_user_profile(user_id)
            if not profile:
                logger.error(f"Cannot create session: user profile not found for {user_id}")
                return None
            
            # Create session
            session_id = f"frenly_session_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            created_at = datetime.now()
            expires_at = created_at + timedelta(seconds=expires_in)
            
            session = UserSession(
                session_id=session_id,
                user_id=user_id,
                username=profile.username,
                role=profile.role,
                created_at=created_at,
                last_activity=created_at,
                expires_at=expires_at
            )
            
            # Store session
            self.session_cache[session_id] = session
            
            # Log activity
            self.log_user_activity(user_id, "session_created", {
                "session_id": session_id,
                "expires_at": expires_at.isoformat()
            })
            
            logger.info(f"Created user session: {session_id} for {profile.username}")
            return session
            
        except Exception as e:
            logger.error(f"Error creating user session: {e}")
            return None
    
    def validate_session(self, session_id: str) -> Optional[UserSession]:
        """Validate and return a user session."""
        if session_id not in self.session_cache:
            return None
        
        session = self.session_cache[session_id]
        
        # Check if session is expired
        if datetime.now() > session.expires_at:
            self.invalidate_session(session_id)
            return None
        
        # Check if session is active
        if not session.is_active:
            return None
        
        # Update last activity
        session.last_activity = datetime.now()
        
        return session
    
    def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a user session."""
        if session_id in self.session_cache:
            session = self.session_cache[session_id]
            session.is_active = False
            
            # Log activity
            self.log_user_activity(session.user_id, "session_invalidated", {
                "session_id": session_id,
                "reason": "manual_invalidation"
            })
            
            logger.info(f"Invalidated session: {session_id}")
            return True
        
        return False
    
    def get_user_sessions(self, user_id: str) -> List[UserSession]:
        """Get all active sessions for a user."""
        return [session for session in self.session_cache.values() 
                if session.user_id == user_id and session.is_active]
    
    def sync_user_preferences(self, user_id: str) -> bool:
        """Synchronize user preferences with main platform."""
        try:
            profile = self.get_user_profile(user_id, force_refresh=True)
            if not profile:
                return False
            
            # Update Frenly context based on user preferences
            if "frenly_preferences" in profile.preferences:
                prefs = profile.preferences["frenly_preferences"]
                
                # Update app context based on preferences
                if "default_app_mode" in prefs:
                    self.frenly_agent.manage_app(AppCommand(
                        command_type="switch_app_mode",
                        target_mode=prefs["default_app_mode"]
                    ))
                
                if "default_ai_mode" in prefs:
                    self.frenly_agent.manage_app(AppCommand(
                        command_type="change_ai_mode",
                        target_ai_mode=prefs["default_ai_mode"]
                    ))
                
                if "default_dashboard_view" in prefs:
                    self.frenly_agent.manage_app(AppCommand(
                        command_type="change_dashboard_view",
                        target_view=prefs["default_dashboard_view"]
                    ))
            
            logger.info(f"Synchronized preferences for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error synchronizing user preferences: {e}")
            return False
    
    def log_user_activity(self, user_id: str, activity_type: str, details: Dict[str, Any] = None):
        """Log user activity for tracking and analytics."""
        try:
            activity = {
                "user_id": user_id,
                "activity_type": activity_type,
                "timestamp": datetime.now().isoformat(),
                "details": details or {},
                "frenly_context": {
                    "app_mode": self.frenly_agent.app_context.app_mode.value,
                    "ai_mode": self.frenly_agent.app_context.ai_mode.value,
                    "dashboard_view": self.frenly_agent.app_context.dashboard_view.value
                }
            }
            
            self.user_activities.append(activity)
            
            # Maintain activity log size
            if len(self.user_activities) > self.max_activities:
                self.user_activities = self.user_activities[-self.max_activities:]
            
        except Exception as e:
            logger.error(f"Error logging user activity: {e}")
    
    def get_user_activities(self, user_id: str = None, activity_type: str = None, 
                           limit: int = 100) -> List[Dict[str, Any]]:
        """Get user activities with optional filtering."""
        activities = self.user_activities
        
        if user_id:
            activities = [a for a in activities if a["user_id"] == user_id]
        
        if activity_type:
            activities = [a for a in activities if a["activity_type"] == activity_type]
        
        # Return most recent activities first
        return sorted(activities, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get analytics for a specific user."""
        user_activities = self.get_user_activities(user_id)
        
        if not user_activities:
            return {"user_id": user_id, "total_activities": 0}
        
        # Group activities by type
        activities_by_type = {}
        for activity in user_activities:
            activity_type = activity["activity_type"]
            if activity_type not in activities_by_type:
                activities_by_type[activity_type] = 0
            activities_by_type[activity_type] += 1
        
        # Calculate session statistics
        user_sessions = self.get_user_sessions(user_id)
        active_sessions = [s for s in user_sessions if s.is_active]
        
        return {
            "user_id": user_id,
            "total_activities": len(user_activities),
            "activities_by_type": activities_by_type,
            "total_sessions": len(user_sessions),
            "active_sessions": len(active_sessions),
            "last_activity": user_activities[0]["timestamp"] if user_activities else None,
            "frenly_usage": {
                "app_modes_used": list(set(a["frenly_context"]["app_mode"] for a in user_activities)),
                "ai_modes_used": list(set(a["frenly_context"]["ai_mode"] for a in user_activities)),
                "dashboard_views_used": list(set(a["frenly_context"]["dashboard_view"] for a in user_activities))
            }
        }
    
    def get_cross_platform_user_summary(self, user_id: str) -> Dict[str, Any]:
        """Get a comprehensive user summary across platforms."""
        try:
            # Get user profile from main platform
            profile = self.get_user_profile(user_id)
            if not profile:
                return {"error": "User profile not found"}
            
            # Get Frenly-specific analytics
            frenly_analytics = self.get_user_analytics(user_id)
            
            # Get active sessions
            active_sessions = self.get_user_sessions(user_id)
            
            return {
                "user_id": user_id,
                "username": profile.username,
                "email": profile.email,
                "role": profile.role,
                "status": profile.status,
                "permissions": profile.permissions,
                "main_platform": {
                    "created_at": profile.created_at.isoformat(),
                    "last_login": profile.last_login.isoformat() if profile.last_login else None,
                    "preferences": profile.preferences
                },
                "frenly_platform": {
                    "analytics": frenly_analytics,
                    "active_sessions": len(active_sessions),
                    "last_frenly_activity": frenly_analytics.get("last_activity")
                },
                "cross_platform": {
                    "total_sessions": len(active_sessions),
                    "platforms_used": ["main", "frenly"],
                    "last_activity": max(
                        profile.last_login.isoformat() if profile.last_login else "1970-01-01T00:00:00",
                        frenly_analytics.get("last_activity", "1970-01-01T00:00:00")
                    )
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting cross-platform user summary: {e}")
            return {"error": str(e)}
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.session_cache.items():
            if current_time > session.expires_at:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.invalidate_session(session_id)
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get the status of the user integration service."""
        try:
            # Test connection to main platform
            response = requests.get(
                f"{self.main_platform_config['base_url']}/health",
                timeout=5
            )
            main_platform_status = "connected" if response.status_code == 200 else "disconnected"
            
        except requests.exceptions.RequestException:
            main_platform_status = "disconnected"
        
        return {
            "main_platform_status": main_platform_status,
            "main_platform_url": self.main_platform_config["base_url"],
            "cached_users": len(self.user_cache),
            "active_sessions": len([s for s in self.session_cache.values() if s.is_active]),
            "total_sessions": len(self.session_cache),
            "user_activities": len(self.user_activities),
            "cache_ttl": self.cache_ttl
        }


# Example usage
if __name__ == "__main__":
    # Initialize Frenly agent (mock)
    class MockFrenlyAgent:
        def __init__(self):
            self.app_context = type('obj', (object,), {
                'app_mode': type('obj', (object,), {'value': 'regular'}),
                'ai_mode': type('obj', (object,), {'value': 'guided'}),
                'dashboard_view': type('obj', (object,), {'value': 'reconciliation'})
            })()
        
        def manage_app(self, command):
            print(f"Mock command execution: {command.command_type}")
            return type('obj', (object,), {'success': True})()
    
    frenly = MockFrenlyAgent()
    
    # Initialize user integration
    integration = FrenlyUserIntegration(frenly)
    
    # Set main platform configuration
    integration.set_main_platform_config("http://localhost:8000")
    
    # Get integration status
    status = integration.get_integration_status()
    print(f"Integration status: {status}")

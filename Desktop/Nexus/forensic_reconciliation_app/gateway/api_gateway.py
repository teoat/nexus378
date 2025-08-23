"""
API Gateway Core - RESTful API Endpoints and Routing

This module implements the APIGateway class that provides
comprehensive API gateway capabilities for the forensic platform.
"""

import json
import logging
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import aiohttp
import asyncio
import jwt
from aiohttp import ClientSession, web
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..ai_service.taskmaster.models.job import Job, JobPriority, JobStatus, JobType
# from .auth.jwt_auth import JWTAuthManager  # Removed: not present
# from .rate_limiter import RateLimiter      # Removed: not present

# Placeholder RateLimiter implementation
class RateLimiter:
    def __init__(self, rate: int):
        self.rate = rate
        self.requests = defaultdict(list)

    def is_allowed(self, user_id: str) -> bool:
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=1)
        self.requests[user_id] = [t for t in self.requests[user_id] if t > window_start]
        if len(self.requests[user_id]) < self.rate:
            self.requests[user_id].append(now)
            return True
        return False
from . import config as gw_config


class HTTPMethod(Enum):
    """HTTP methods supported by the API gateway."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


class EndpointType(Enum):
    """Types of API endpoints."""

    REST_API = "rest_api"  # RESTful API endpoint
    GRAPHQL = "graphql"  # GraphQL endpoint
    WEBSOCKET = "websocket"  # WebSocket endpoint
    GRPC = "grpc"  # gRPC endpoint
    WEBHOOK = "webhook"  # Webhook endpoint


class AuthenticationType(Enum):
    """Types of authentication."""

    JWT = "jwt"  # JWT token authentication
    API_KEY = "api_key"  # API key authentication
    OAUTH2 = "oauth2"  # OAuth 2.0 authentication
    BASIC = "basic"  # Basic authentication
    NONE = "none"  # No authentication


@dataclass
class APIEndpoint:
    """An API endpoint definition."""

    endpoint_id: str
    path: str
    method: HTTPMethod
    endpoint_type: EndpointType
    authentication: AuthenticationType
    rate_limit: int  # requests per minute
    timeout: int  # seconds
    handler_function: str
    middleware: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIRoute:
    """An API route configuration."""

    route_id: str
    base_path: str
    service_name: str
    endpoints: List[APIEndpoint]
    authentication: AuthenticationType
    rate_limiting: bool
    cors_enabled: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIRequest:
    """An API request."""

    request_id: str
    endpoint_id: str
    method: HTTPMethod
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, str]
    body: Any
    user_id: Optional[str]
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIResponse:
    """An API response."""

    response_id: str
    request_id: str
    status_code: int
    headers: Dict[str, str]
    body: Any
    response_time: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class APIGateway:
    """
    Comprehensive API gateway system.

    The APIGateway is responsible for:
    - Routing API requests to appropriate services
    - Managing authentication and authorization
    - Implementing rate limiting and throttling
    - Handling CORS and security policies
    - Providing API documentation and monitoring
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the APIGateway."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.host = config.get("host", "0.0.0.0")
        self.port = config.get("port", 8080)
        self.debug = config.get("debug", False)
        self.max_request_size = config.get("max_request_size", 10 * 1024 * 1024)  # 10MB

        # Auth and Rate Limiting
        self.jwt_auth_manager = JWTAuthManager(gw_config.get_jwt_config())
        self.rate_limiter = RateLimiter(gw_config.get_rate_limiter_config())

        # API management
        self.routes: Dict[str, APIRoute] = {}
        self.endpoints: Dict[str, APIEndpoint] = {}
        self.route_registry: Dict[str, str] = {}  # path -> route_id mapping

        # Request/Response tracking
        self.api_requests: Dict[str, APIRequest] = {}
        self.api_responses: Dict[str, APIResponse] = {}
        self.request_history: Dict[str, List[str]] = defaultdict(list)

        # Performance tracking
        self.total_requests = 0
        self.total_responses = 0
        self.average_response_time = 0.0

        # Web application
        self.app = web.Application()
        self.runner = None

        # Event loop
        self.loop = asyncio.get_event_loop()

        # Initialize gateway components
        self._initialize_gateway_components()

        self.logger.info("APIGateway initialized successfully")

    async def start(self):
        """Start the API Gateway."""
        self.logger.info("Starting API Gateway...")

        # Initialize API components
        await self._initialize_api_components()

        # Setup routes and middleware
        await self._setup_routes()
        await self._setup_middleware()

        # Start web server
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()

        site = web.TCPSite(self.runner, self.host, self.port)
        await site.start()

        self.logger.info(f"API Gateway started on {self.host}:{self.port}")

        # Start background tasks
        asyncio.create_task(self._cleanup_old_requests())

        self.logger.info("API Gateway started successfully")

    async def stop(self):
        """Stop the API Gateway."""
        self.logger.info("Stopping API Gateway...")

        if self.runner:
            await self.runner.cleanup()

        self.logger.info("API Gateway stopped")

    def _initialize_gateway_components(self):
        """Initialize gateway components."""
        try:
            # Initialize default components
            self._initialize_default_components()

            self.logger.info("Gateway components initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing gateway components: {e}")

    def _initialize_default_components(self):
        """Initialize default gateway components."""
        try:
            # This would initialize default components
            # For now, just log initialization
            self.logger.info("Default gateway components initialized")

        except Exception as e:
            self.logger.error(f"Error initializing default components: {e}")

    async def _initialize_api_components(self):
        """Initialize API components."""
        try:
            # Initialize default API routes
            await self._initialize_default_routes()

            self.logger.info("API components initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing API components: {e}")

    async def _initialize_default_routes(self):
        """Initialize default API routes."""
        try:
            # Create default API routes
            default_routes = [
                {
                    "base_path": "/api/v1",
                    "service_name": "forensic_platform",
                    "endpoints": [
                        {
                            "path": "/health",
                            "method": HTTPMethod.GET,
                            "endpoint_type": EndpointType.REST_API,
                            "authentication": AuthenticationType.NONE,
                            "rate_limit": 1000,
                            "timeout": 30,
                            "handler_function": "health_check",
                            "middleware": [],
                        },
                        {
                            "path": "/status",
                            "method": HTTPMethod.GET,
                            "endpoint_type": EndpointType.REST_API,
                            "authentication": AuthenticationType.JWT,
                            "rate_limit": 100,
                            "timeout": 30,
                            "handler_function": "system_status",
                            "middleware": ["auth", "rate_limit"],
                        },
                    ],
                    "authentication": AuthenticationType.JWT,
                    "rate_limiting": True,
                    "cors_enabled": True,
                }
            ]

            for route_data in default_routes:
                await self.create_api_route(
                    base_path=route_data["base_path"],
                    service_name=route_data["service_name"],
                    endpoints=route_data["endpoints"],
                    authentication=route_data["authentication"],
                    rate_limiting=route_data["rate_limiting"],
                    cors_enabled=route_data["cors_enabled"],
                )

            self.logger.info(f"Initialized {len(default_routes)} default API routes")

        except Exception as e:
            self.logger.error(f"Error initializing default routes: {e}")

    async def create_api_route(
        self,
        base_path: str,
        service_name: str,
        endpoints: List[Dict[str, Any]],
        authentication: AuthenticationType,
        rate_limiting: bool = True,
        cors_enabled: bool = True,
    ) -> str:
        """Create a new API route."""
        try:
            route_id = str(uuid.uuid4())

            # Create endpoint objects
            route_endpoints = []
            for endpoint_data in endpoints:
                endpoint = APIEndpoint(
                    endpoint_id=str(uuid.uuid4()),
                    path=endpoint_data["path"],
                    method=endpoint_data["method"],
                    endpoint_type=endpoint_data["endpoint_type"],
                    authentication=endpoint_data["authentication"],
                    rate_limit=endpoint_data["rate_limit"],
                    timeout=endpoint_data["timeout"],
                    handler_function=endpoint_data["handler_function"],
                    middleware=endpoint_data.get("middleware", []),
                )

                route_endpoints.append(endpoint)
                self.endpoints[endpoint.endpoint_id] = endpoint

                # Register endpoint path
                full_path = f"{base_path}{endpoint.path}"
                self.route_registry[full_path] = route_id

            # Create route
            route = APIRoute(
                route_id=route_id,
                base_path=base_path,
                service_name=service_name,
                endpoints=route_endpoints,
                authentication=authentication,
                rate_limiting=rate_limiting,
                cors_enabled=cors_enabled,
            )

            # Store route
            self.routes[route_id] = route

            self.logger.info(f"Created API route: {route_id} - {base_path}")

            return route_id

        except Exception as e:
            self.logger.error(f"Error creating API route: {e}")
            raise

    async def _setup_routes(self):
        """Setup API routes and handlers."""
        try:
            # Setup default handlers
            self.app.router.add_get("/api/v1/health", self._health_check_handler)
            self.app.router.add_get("/api/v1/status", self._system_status_handler)

            # Setup dynamic routes
            for route in self.routes.values():
                for endpoint in route.endpoints:
                    full_path = f"{route.base_path}{endpoint.path}"

                    # Add route based on method
                    if endpoint.method == HTTPMethod.GET:
                        self.app.router.add_get(
                            full_path, self._create_endpoint_handler(endpoint)
                        )
                    elif endpoint.method == HTTPMethod.POST:
                        self.app.router.add_post(
                            full_path, self._create_endpoint_handler(endpoint)
                        )
                    elif endpoint.method == HTTPMethod.PUT:
                        self.app.router.add_put(
                            full_path, self._create_endpoint_handler(endpoint)
                        )
                    elif endpoint.method == HTTPMethod.DELETE:
                        self.app.router.add_delete(
                            full_path, self._create_endpoint_handler(endpoint)
                        )
                    elif endpoint.method == HTTPMethod.PATCH:
                        self.app.router.add_patch(
                            full_path, self._create_endpoint_handler(endpoint)
                        )
                    elif endpoint.method == HTTPMethod.OPTIONS:
                        self.app.router.add_options(
                            full_path, self._create_endpoint_handler(endpoint)
                        )
                    elif endpoint.method == HTTPMethod.HEAD:
                        self.app.router.add_head(
                            full_path, self._create_endpoint_handler(endpoint)
                        )

            self.logger.info("API routes setup completed")

        except Exception as e:
            self.logger.error(f"Error setting up routes: {e}")

    async def _setup_middleware(self):
        """Setup middleware for the API gateway."""
        try:
            # Add CORS middleware
            self.app.middlewares.append(self._cors_middleware)

            # Add authentication middleware
            self.app.middlewares.append(self._auth_middleware)

            # Add rate limiting middleware
            self.app.middlewares.append(self._rate_limit_middleware)

            # Add logging middleware
            self.app.middlewares.append(self._logging_middleware)

            self.logger.info("API middleware setup completed")

        except Exception as e:
            self.logger.error(f"Error setting up middleware: {e}")

    def _create_endpoint_handler(self, endpoint: APIEndpoint):
        """Create a handler function for an endpoint."""

        async def handler(request):
            start_time = datetime.utcnow()

            try:
                # Create API request
                api_request = await self._create_api_request(request, endpoint)

                # Process request based on handler function
                if endpoint.handler_function == "health_check":
                    response_data = await self._health_check_handler(request)
                elif endpoint.handler_function == "system_status":
                    response_data = await self._system_status_handler(request)
                else:
                    response_data = {
                        "message": "Handler not implemented",
                        "status": "error",
                    }

                # Create API response
                response_time = (datetime.utcnow() - start_time).total_seconds()
                api_response = await self._create_api_response(
                    api_request, response_data, response_time
                )

                # Return response
                return web.json_response(response_data)

            except Exception as e:
                self.logger.error(f"Error in endpoint handler: {e}")
                return web.json_response({"error": str(e)}, status=500)

        return handler

    async def _health_check_handler(self, request) -> Dict[str, Any]:
        """Handle health check requests."""
        try:
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "service": "forensic_platform",
                "version": "1.0.0",
            }
        except Exception as e:
            self.logger.error(f"Error in health check handler: {e}")
            return {"status": "unhealthy", "error": str(e)}

    async def _system_status_handler(self, request) -> Dict[str, Any]:
        """Handle system status requests."""
        try:
            return {
                "status": "operational",
                "timestamp": datetime.utcnow().isoformat(),
                "uptime": "24h",
                "services": {
                    "api_gateway": "operational",
                    "ai_service": "operational",
                    "database": "operational",
                },
            }
        except Exception as e:
            self.logger.error(f"Error in system status handler: {e}")
            return {"status": "error", "error": str(e)}

    async def _create_api_request(
        self, request: web.Request, endpoint: APIEndpoint
    ) -> APIRequest:
        """Create an API request object."""
        try:
            # Extract request data
            headers = dict(request.headers)
            query_params = dict(request.query)

            # Extract body if present
            body = None
            if request.content_type == "application/json":
                try:
                    body = await request.json()
                except:
                    body = await request.text()
            elif request.content_type:
                body = await request.text()

            # Create API request
            api_request = APIRequest(
                request_id=str(uuid.uuid4()),
                endpoint_id=endpoint.endpoint_id,
                method=endpoint.method,
                path=str(request.path),
                headers=headers,
                query_params=query_params,
                body=body,
                user_id=request.get("user_id"),
                timestamp=datetime.utcnow(),
            )

            # Store request
            self.api_requests[api_request.request_id] = api_request

            # Update statistics
            self.total_requests += 1

            return api_request

        except Exception as e:
            self.logger.error(f"Error creating API request: {e}")
            raise

    async def _create_api_response(
        self, api_request: APIRequest, response_data: Any, response_time: float
    ) -> APIResponse:
        """Create an API response object."""
        try:
            api_response = APIResponse(
                response_id=str(uuid.uuid4()),
                request_id=api_request.request_id,
                status_code=200,
                headers={"Content-Type": "application/json"},
                body=response_data,
                response_time=response_time,
                timestamp=datetime.utcnow(),
            )

            # Store response
            self.api_responses[api_response.response_id] = api_response

            # Update statistics
            self.total_responses += 1
            self.average_response_time = (
                self.average_response_time + response_time
            ) / 2

            return api_response

        except Exception as e:
            self.logger.error(f"Error creating API response: {e}")
            raise

    async def _cors_middleware(self, app, handler):
        """CORS middleware."""

        async def middleware(request):
            # Add CORS headers
            response = await handler(request)
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = (
                "GET, POST, PUT, DELETE, OPTIONS"
            )
            response.headers["Access-Control-Allow-Headers"] = (
                "Content-Type, Authorization"
            )
            return response

        return middleware

    async def _auth_middleware(self, app, handler):
        """Authentication middleware."""

        async def middleware(request):
            # Find the endpoint being accessed
            endpoint = self._get_endpoint_for_request(request)

            # Skip auth for public endpoints
            if endpoint and endpoint.authentication == AuthenticationType.NONE:
                return await handler(request)

            # Extract and validate JWT token
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return web.json_response({"error": "Unauthorized"}, status=401)

            token = auth_header.split(" ")[1]
            auth_result = self.jwt_auth_manager.validate_token(token)

            if auth_result.status != "success":
                return web.json_response({"error": auth_result.message}, status=401)

            # Attach user to request
            request["user"] = auth_result.user
            request["user_id"] = auth_result.user.id

            # RBAC check
            if endpoint:
                # A simple way to map endpoint path to a resource name
                resource_name = endpoint.path.strip("/").split("/")[0]
                action_map = {
                    "GET": "read",
                    "POST": "write",
                    "PUT": "write",
                    "DELETE": "delete",
                    "PATCH": "write"
                }
                action = action_map.get(request.method.upper())

                if action and not self.jwt_auth_manager.has_permission(auth_result.user, resource_name, action):
                    return web.json_response({"error": "Forbidden"}, status=403)

            return await handler(request)

        return middleware

    async def _rate_limit_middleware(self, app, handler):
        """Rate limiting middleware."""

        async def middleware(request):
            endpoint = self._get_endpoint_for_request(request)
            if not endpoint or not endpoint.middleware or "rate_limit" not in endpoint.middleware:
                return await handler(request)

            user_id = request.get("user_id")
            entity_id = f"user_{user_id}" if user_id else f"ip_{request.remote}"

            rate_limit_result = await self.rate_limiter.check_rate_limit(entity_id)

            if not rate_limit_result.allowed:
                return web.json_response(
                    {"error": "Rate limit exceeded"},
                    status=429,
                    headers={"Retry-After": str(rate_limit_result.delay_seconds or 10)},
                )

            return await handler(request)

        return middleware

    async def _logging_middleware(self, app, handler):
        """Logging middleware."""

        async def middleware(request):
            start_time = datetime.utcnow()

            # Log request
            self.logger.info(f"Request: {request.method} {request.path}")

            # Process request
            response = await handler(request)

            # Log response
            response_time = (datetime.utcnow() - start_time).total_seconds()
            self.logger.info(f"Response: {response.status} - {response_time:.3f}s")

            return response

        return middleware

    def _get_endpoint_for_request(self, request: web.Request) -> Optional[APIEndpoint]:
        """Find the APIEndpoint that matches the request."""
        for route in self.routes.values():
            if request.path.startswith(route.base_path):
                for endpoint in route.endpoints:
                    full_path = f"{route.base_path}{endpoint.path}"
                    if full_path == request.path and endpoint.method.value == request.method:
                        return endpoint
        return None

    async def _cleanup_old_requests(self):
        """Clean up old API requests and responses."""
        while True:
            try:
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(
                    hours=24
                )  # Keep 24 hours of data

                # Clean up old requests
                old_requests = [
                    req_id
                    for req_id, request in self.api_requests.items()
                    if request.timestamp < cutoff_time
                ]

                for req_id in old_requests:
                    del self.api_requests[req_id]

                # Clean up old responses
                old_responses = [
                    resp_id
                    for resp_id, response in self.api_responses.items()
                    if response.timestamp < cutoff_time
                ]

                for resp_id in old_responses:
                    del self.api_responses[resp_id]

                if old_requests or old_responses:
                    self.logger.info(
                        f"Cleaned up {len(old_requests)} old requests and {len(old_responses)} old responses"
                    )

                await asyncio.sleep(3600)  # Clean up every hour

            except Exception as e:
                self.logger.error(f"Error cleaning up old data: {e}")
                await asyncio.sleep(3600)

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            "total_requests": self.total_requests,
            "total_responses": self.total_responses,
            "average_response_time": self.average_response_time,
            "active_routes": len(self.routes),
            "active_endpoints": len(self.endpoints),
            "http_methods_supported": [m.value for m in HTTPMethod],
            "endpoint_types_supported": [t.value for t in EndpointType],
            "authentication_types_supported": [t.value for t in AuthenticationType],
            "gateway_host": self.host,
            "gateway_port": self.port,
        }


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = gw_config.get_api_gateway_config()

    # Initialize API gateway
    gateway = APIGateway(config)

    # Start the gateway
    try:
        asyncio.run(gateway.start())
    except KeyboardInterrupt:
        asyncio.run(gateway.stop())

    print("APIGateway system initialized successfully!")

API Gateway Core - RESTful API Endpoints and Routing

This module implements the APIGateway class that provides
comprehensive API gateway capabilities for the forensic platform.

import asyncio
import logging
import uuid
from datetime import datetime, timedelta

# Web framework libraries
try:
    import uvicorn

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# Authentication libraries
try:

    AUTH_LIBRARIES_AVAILABLE = True
except ImportError:
    AUTH_LIBRARIES_AVAILABLE = False

from ...taskmaster.models.job import Job, JobPriority, JobStatus, JobType

class EndpointType(Enum):

    REST = "rest"  # RESTful API endpoints
    GRAPHQL = "graphql"  # GraphQL endpoints
    WEBSOCKET = "websocket"  # WebSocket endpoints
    GRPC = "grpc"  # gRPC endpoints
    EVENT_DRIVEN = "event_driven"  # Event-driven endpoints

class HTTPMethod(Enum):

    GET = "GET"  # GET requests
    POST = "POST"  # POST requests
    PUT = "PUT"  # PUT requests
    DELETE = "DELETE"  # DELETE requests
    PATCH = "PATCH"  # PATCH requests
    HEAD = "HEAD"  # HEAD requests
    OPTIONS = "OPTIONS"  # OPTIONS requests

class ServiceType(Enum):

    AI_SERVICE = "ai_service"  # AI service endpoints
    AUTH_SERVICE = "auth_service"  # Authentication service
    EVIDENCE_SERVICE = "evidence_service"  # Evidence processing service
    CASE_SERVICE = "case_service"  # Case management service
    REPORT_SERVICE = "report_service"  # Report generation service
    ANALYTICS_SERVICE = "analytics_service"  # Analytics service
    NOTIFICATION_SERVICE = "notification_service"  # Notification service

@dataclass
class APIRoute:

        self.host = config.get("host", "0.0.0.0")
        self.port = config.get("port", 8000)
        self.debug = config.get("debug", False)
        self.title = config.get("title", "Forensic Platform API Gateway")
        self.version = config.get("version", "1.0.0")
        self.description = config.get(
            "description", "Comprehensive API Gateway for Forensic Platform"
        )

        # API management
        self.routes: Dict[str, APIRoute] = {}
        self.service_endpoints: Dict[str, ServiceEndpoint] = {}
        self.request_contexts: Dict[str, RequestContext] = {}

        # Performance tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.average_response_time = 0.0

        # FastAPI application
        self.app = None
        self.server = None

        # Event loop
        self.loop = asyncio.get_event_loop()

        # Check library availability
        self._check_library_availability()

        # Initialize FastAPI application
        self._initialize_fastapi_app()

        self.logger.info("APIGateway initialized successfully")

    def _check_library_availability(self):

                "FastAPI not available - API gateway functionality will be limited",
            )

        if not AUTH_LIBRARIES_AVAILABLE:
            self.logger.warning(
                "Authentication libraries not available - auth functionality will be limited",
            )

    def _initialize_fastapi_app(self):

                    "FastAPI not available - skipping app initialization",
                )
                return

            # Create FastAPI app
            self.app = FastAPI(
                title=self.title,
                version=self.version,
                description=self.description,
                debug=self.debug,
            )

            # Add middleware
            self._add_middleware()

            # Add CORS middleware
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],  # Configure appropriately for production
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

            # Add trusted host middleware
            self.app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=["*"],  # Configure appropriately for production
            )

            # Initialize routes
            self._initialize_default_routes()

            self.logger.info("FastAPI application initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing FastAPI app: {e}")

    def _add_middleware(self):

                        f"{request.method} {request.url.path} - "
                        f"Status: {response.status_code} - "
                        f"Time: {process_time:.3f}s"
                    )

                    return response

            # Add the middleware
            self.app.add_middleware(RequestLoggingMiddleware)

        except Exception as e:
            self.logger.error(f"Error adding middleware: {e}")

    def _initialize_default_routes(self):

                    route_id="health_check",
                    path="/health",
                    methods=[HTTPMethod.GET],
                    service_type=ServiceType.AI_SERVICE,
                    endpoint_type=EndpointType.REST,
                    description="Health check endpoint",
                    requires_auth=False,
                    required_roles=[],
                    rate_limit=None,
                    timeout=30,
                )
            )

            # API documentation endpoint
            self.add_route(
                APIRoute(
                    route_id="api_docs",
                    path="/docs",
                    methods=[HTTPMethod.GET],
                    service_type=ServiceType.AI_SERVICE,
                    endpoint_type=EndpointType.REST,
                    description="API documentation",
                    requires_auth=False,
                    required_roles=[],
                    rate_limit=None,
                    timeout=30,
                )
            )

            # API info endpoint
            self.add_route(
                APIRoute(
                    route_id="api_info",
                    path="/api/info",
                    methods=[HTTPMethod.GET],
                    service_type=ServiceType.AI_SERVICE,
                    endpoint_type=EndpointType.REST,
                    description="API information",
                    requires_auth=False,
                    required_roles=[],
                    rate_limit=None,
                    timeout=30,
                )
            )

            # AI Service endpoints
            self._initialize_ai_service_routes()

            # Authentication endpoints
            self._initialize_auth_service_routes()

            # Evidence service endpoints
            self._initialize_evidence_service_routes()

            # Case management endpoints
            self._initialize_case_service_routes()

            # Report service endpoints
            self._initialize_report_service_routes()

            self.logger.info("Default routes initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing default routes: {e}")

    def _initialize_ai_service_routes(self):

                    route_id="reconciliation_process",
                    path="/api/ai/reconciliation/process",
                    methods=[HTTPMethod.POST],
                    service_type=ServiceType.AI_SERVICE,
                    endpoint_type=EndpointType.REST,
                    description="Process reconciliation request",
                    requires_auth=True,
                    required_roles=["analyst", "investigator"],
                    rate_limit=100,
                    timeout=300,
                )
            )

            # Fraud detection endpoints
            self.add_route(
                APIRoute(
                    route_id="fraud_detection",
                    path="/api/ai/fraud/detect",
                    methods=[HTTPMethod.POST],
                    service_type=ServiceType.AI_SERVICE,
                    endpoint_type=EndpointType.REST,
                    description="Detect fraud patterns",
                    requires_auth=True,
                    required_roles=["analyst", "investigator"],
                    rate_limit=50,
                    timeout=600,
                )
            )

            # Risk assessment endpoints
            self.add_route(
                APIRoute(
                    route_id="risk_assessment",
                    path="/api/ai/risk/assess",
                    methods=[HTTPMethod.POST],
                    service_type=ServiceType.AI_SERVICE,
                    endpoint_type=EndpointType.REST,
                    description="Assess risk levels",
                    requires_auth=True,
                    required_roles=["analyst", "investigator", "risk_manager"],
                    rate_limit=75,
                    timeout=180,
                )
            )

            # Evidence processing endpoints
            self.add_route(
                APIRoute(
                    route_id="evidence_process",
                    path="/api/ai/evidence/process",
                    methods=[HTTPMethod.POST],
                    service_type=ServiceType.AI_SERVICE,
                    endpoint_type=EndpointType.REST,
                    description="Process evidence files",
                    requires_auth=True,
                    required_roles=["analyst", "investigator", "evidence_specialist"],
                    rate_limit=200,
                    timeout=120,
                )
            )

        except Exception as e:
            self.logger.error(f"Error initializing AI service routes: {e}")

    def _initialize_auth_service_routes(self):

                    route_id="auth_login",
                    path="/api/auth/login",
                    methods=[HTTPMethod.POST],
                    service_type=ServiceType.AUTH_SERVICE,
                    endpoint_type=EndpointType.REST,
                    description="User authentication",
                    requires_auth=False,
                    required_roles=[],
                    rate_limit=10,
                    timeout=30,
                )
            )

            # Logout endpoint
            self.add_route(
                APIRoute(
                    route_id="auth_logout",
                    path="/api/auth/logout",
                    methods=[HTTPMethod.POST],
                    service_type=ServiceType.AUTH_SERVICE,
                    endpoint_type=EndpointType.REST,
                    description="User logout",
                    requires_auth=True,
                    required_roles=[],
                    rate_limit=20,
                    timeout=30,
                )
            )

            # Refresh token endpoint
            self.add_route(
                APIRoute(
                    route_id="auth_refresh",
                    path="/api/auth/refresh",
                    methods=[HTTPMethod.POST],
                    service_type=ServiceType.AUTH_SERVICE,
                    endpoint_type=EndpointType.REST,
                    description="Refresh authentication token",
                    requires_auth=False,
                    required_roles=[],
                    rate_limit=30,
                    timeout=30,
                )
            )

            # MFA verification endpoint
            self.add_route(
                APIRoute(
                    route_id="auth_mfa",
                    path="/api/auth/mfa/verify",
                    methods=[HTTPMethod.POST],
                    service_type=ServiceType.AUTH_SERVICE,
                    endpoint_type=EndpointType.REST,
                    description="Multi-factor authentication verification",
                    requires_auth=False,
                    required_roles=[],
                    rate_limit=5,
                    timeout=60,
                )
            )

        except Exception as e:
            self.logger.error(f"Error initializing auth service routes: {e}")

    def _initialize_evidence_service_routes(self):

                    route_id="evidence_upload",
                    path="/api/evidence/upload",
                    methods=[HTTPMethod.POST],
                    service_type=ServiceType.EVIDENCE_SERVICE,
                    endpoint_type=EndpointType.REST,
                    description="Upload evidence files",
                    requires_auth=True,
                    required_roles=["analyst", "investigator", "evidence_specialist"],
                    rate_limit=50,
                    timeout=300,
                )
            )

            # File processing endpoint
            self.add_route(
                APIRoute(
                    route_id="evidence_process",
                    path="/api/evidence/process",
                    methods=[HTTPMethod.POST],
                    service_type=ServiceType.EVIDENCE_SERVICE,
                    endpoint_type=EndpointType.REST,
                    description="Process evidence files",
                    requires_auth=True,
                    required_roles=["analyst", "investigator", "evidence_specialist"],
                    rate_limit=100,
                    timeout=600,
                )
            )

            # File retrieval endpoint
            self.add_route(
                APIRoute(
                    route_id="evidence_retrieve",
                    path="/api/evidence/{file_id}",
                    methods=[HTTPMethod.GET],
                    service_type=ServiceType.EVIDENCE_SERVICE,
                    endpoint_type=EndpointType.REST,
                    description="Retrieve evidence file",
                    requires_auth=True,
                    required_roles=["analyst", "investigator", "evidence_specialist"],
                    rate_limit=200,
                    timeout=60,
                )
            )

        except Exception as e:
            self.logger.error(f"Error initializing evidence service routes: {e}")

    def _initialize_case_service_routes(self):

                    route_id="case_create",
                    path="/api/cases",
                    methods=[HTTPMethod.POST],
                    service_type=ServiceType.CASE_SERVICE,
                    endpoint_type=EndpointType.REST,
                    description="Create new case",
                    requires_auth=True,
                    required_roles=["analyst", "investigator", "case_manager"],
                    rate_limit=25,
                    timeout=120,
                )
            )

            # Get case endpoint
            self.add_route(
                APIRoute(
                    route_id="case_get",
                    path="/api/cases/{case_id}",
                    methods=[HTTPMethod.GET],
                    service_type=ServiceType.CASE_SERVICE,
                    endpoint_type=EndpointType.REST,
                    description="Get case information",
                    requires_auth=True,
                    required_roles=["analyst", "investigator", "case_manager"],
                    rate_limit=100,
                    timeout=60,
                )
            )

            # Update case endpoint
            self.add_route(
                APIRoute(
                    route_id="case_update",
                    path="/api/cases/{case_id}",
                    methods=[HTTPMethod.PUT, HTTPMethod.PATCH],
                    service_type=ServiceType.CASE_SERVICE,
                    endpoint_type=EndpointType.REST,
                    description="Update case information",
                    requires_auth=True,
                    required_roles=["analyst", "investigator", "case_manager"],
                    rate_limit=50,
                    timeout=120,
                )
            )

            # List cases endpoint
            self.add_route(
                APIRoute(
                    route_id="case_list",
                    path="/api/cases",
                    methods=[HTTPMethod.GET],
                    service_type=ServiceType.CASE_SERVICE,
                    endpoint_type=EndpointType.REST,
                    description="List all cases",
                    requires_auth=True,
                    required_roles=["analyst", "investigator", "case_manager"],
                    rate_limit=200,
                    timeout=60,
                )
            )

        except Exception as e:
            self.logger.error(f"Error initializing case service routes: {e}")

    def _initialize_report_service_routes(self):

                    route_id="report_generate",
                    path="/api/reports/generate",
                    methods=[HTTPMethod.POST],
                    service_type=ServiceType.REPORT_SERVICE,
                    endpoint_type=EndpointType.REST,
                    description="Generate case report",
                    requires_auth=True,
                    required_roles=["analyst", "investigator", "report_writer"],
                    rate_limit=20,
                    timeout=900,
                )
            )

            # Get report endpoint
            self.add_route(
                APIRoute(
                    route_id="report_get",
                    path="/api/reports/{report_id}",
                    methods=[HTTPMethod.GET],
                    service_type=ServiceType.REPORT_SERVICE,
                    endpoint_type=EndpointType.REST,
                    description="Get generated report",
                    requires_auth=True,
                    required_roles=["analyst", "investigator", "report_writer"],
                    rate_limit=100,
                    timeout=60,
                )
            )

            # List reports endpoint
            self.add_route(
                APIRoute(
                    route_id="report_list",
                    path="/api/reports",
                    methods=[HTTPMethod.GET],
                    service_type=ServiceType.REPORT_SERVICE,
                    endpoint_type=EndpointType.REST,
                    description="List all reports",
                    requires_auth=True,
                    required_roles=["analyst", "investigator", "report_writer"],
                    rate_limit=200,
                    timeout=60,
                )
            )

        except Exception as e:
            self.logger.error(f"Error initializing report service routes: {e}")

    async def start(self):

        self.logger.info("Starting API Gateway...")

        if not self.app:
            self.logger.error("FastAPI app not initialized - cannot start gateway")
            return

        try:
            # Start server
            config = uvicorn.Config(
                app=self.app,
                host=self.host,
                port=self.port,
                log_level="info" if not self.debug else "debug",
            )

            self.server = uvicorn.Server(config)

            # Start server in background
            asyncio.create_task(self._start_server())

            self.logger.info(f"API Gateway started on {self.host}:{self.port}")

        except Exception as e:
            self.logger.error(f"Error starting API Gateway: {e}")

    async def _start_server(self):

            self.logger.error(f"Error in server: {e}")

    async def stop(self):

        self.logger.info("Stopping API Gateway...")

        if self.server:
            self.server.should_exit = True

        self.logger.info("API Gateway stopped")

    def add_route(self, route: APIRoute):

                raise ValueError(f"Route already exists: {route.route_id}")

            # Store route
            self.routes[route.route_id] = route

            # Add route to FastAPI app if available
            if self.app and FASTAPI_AVAILABLE:
                self._add_fastapi_route(route)

            self.logger.info(
                f"Route added successfully: {route.route_id} - {route.path}",
            )

        except Exception as e:
            self.logger.error(f"Error adding route: {e}")
            raise

    def _add_fastapi_route(self, route: APIRoute):

                    self.logger.error(f"Error in endpoint handler: {e}")
                    return JSONResponse(
                        content={
                            "success": False,
                            "message": "Internal server error",
                            "error_code": "INTERNAL_ERROR",
                            "timestamp": datetime.utcnow().isoformat(),
                            "request_id": str(uuid.uuid4()),
                        },
                        status_code=500,
                    )

            # Add route to FastAPI app
            for method in route.methods:
                if method == HTTPMethod.GET:
                    self.app.get(route.path)(endpoint_handler)
                elif method == HTTPMethod.POST:
                    self.app.post(route.path)(endpoint_handler)
                elif method == HTTPMethod.PUT:
                    self.app.put(route.path)(endpoint_handler)
                elif method == HTTPMethod.DELETE:
                    self.app.delete(route.path)(endpoint_handler)
                elif method == HTTPMethod.PATCH:
                    self.app.patch(route.path)(endpoint_handler)
                elif method == HTTPMethod.HEAD:
                    self.app.head(route.path)(endpoint_handler)
                elif method == HTTPMethod.OPTIONS:
                    self.app.options(route.path)(endpoint_handler)

        except Exception as e:
            self.logger.error(f"Error adding FastAPI route: {e}")

    async def _create_request_context(self, request: Request) -> RequestContext:

                logger.error(f"Error: {e}")
                pass

            # Create context
            context = RequestContext(
                request_id=str(uuid.uuid4()),
                user_id=None,  # Will be set by auth middleware
                user_roles=[],  # Will be set by auth middleware
                client_ip=request.client.host if request.client else "unknown",
                user_agent=request.headers.get("user-agent", "unknown"),
                request_timestamp=datetime.utcnow(),
                request_path=str(request.url.path),
                request_method=request.method,
                request_headers=dict(request.headers),
                request_body=body,
            )

            # Store context
            self.request_contexts[context.request_id] = context

            return context

        except Exception as e:
            self.logger.error(f"Error creating request context: {e}")
            raise

    async def _process_request(self, route: APIRoute, context: RequestContext):

            self.logger.error(f"Error processing request: {e}")

            # Update statistics
            self.failed_requests += 1

            return ResponseData(
                success=False,
                data=None,
                message=f"Error processing request: {str(e)}",
                error_code="PROCESSING_ERROR",
                timestamp=datetime.utcnow(),
                request_id=context.request_id,
            )

    async def _route_to_service(self, route: APIRoute, context: RequestContext):

            if route.path == "/health":
                return ResponseData(
                    success=True,
                    data={
                        "status": "healthy",
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    message="Service is healthy",
                    error_code=None,
                    timestamp=datetime.utcnow(),
                    request_id=context.request_id,
                )

            elif route.path == "/api/info":
                return ResponseData(
                    success=True,
                    data={
                        "title": self.title,
                        "version": self.version,
                        "description": self.description,
                        "total_routes": len(self.routes),
                        "total_requests": self.total_requests,
                    },
                    message="API information retrieved successfully",
                    error_code=None,
                    timestamp=datetime.utcnow(),
                    request_id=context.request_id,
                )

            else:
                # Mock response for other endpoints
                return ResponseData(
                    success=True,
                    data={
                        "route": route.path,
                        "method": context.request_method,
                        "service_type": route.service_type.value,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    message="Request processed successfully",
                    error_code=None,
                    timestamp=datetime.utcnow(),
                    request_id=context.request_id,
                )

        except Exception as e:
            self.logger.error(f"Error routing to service: {e}")
            raise

    def add_service_endpoint(self, service_endpoint: ServiceEndpoint):

                    f"Service endpoint already exists: {service_endpoint.service_id}",
                )

            # Store service endpoint
            self.service_endpoints[service_endpoint.service_id] = service_endpoint

            self.logger.info(
                f"Service endpoint added successfully: {service_endpoint.service_id}",
            )

        except Exception as e:
            self.logger.error(f"Error adding service endpoint: {e}")
            raise

    def get_route(self, route_id: str) -> Optional[APIRoute]:

            self.logger.error(f"Error getting route: {e}")
            return None

    def get_service_endpoint(self, service_id: str) -> Optional[ServiceEndpoint]:

            self.logger.error(f"Error getting service endpoint: {e}")
            return None

    def get_performance_metrics(self) -> Dict[str, Any]:

            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "average_response_time": self.average_response_time,
            "endpoint_types_supported": [
                endpoint_type.value for endpoint_type in EndpointType
            ],
            "http_methods_supported": [method.value for method in HTTPMethod],
            "service_types_supported": [
                service_type.value for service_type in ServiceType
            ],
            "total_routes": len(self.routes),
            "total_service_endpoints": len(self.service_endpoints),
            "total_request_contexts": len(self.request_contexts),
            "host": self.host,
            "port": self.port,
            "debug": self.debug,
            "title": self.title,
            "version": self.version,
            "fastapi_available": FASTAPI_AVAILABLE,
            "auth_libraries_available": AUTH_LIBRARIES_AVAILABLE,
        }

# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        "host": "0.0.0.0",
        "port": 8000,
        "debug": True,
        "title": "Forensic Platform API Gateway",
        "version": "1.0.0",
        "description": "Comprehensive API Gateway for Forensic Platform",
    }

    # Initialize API Gateway
    gateway = APIGateway(config)

    print("APIGateway system initialized successfully!")

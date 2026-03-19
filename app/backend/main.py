from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.database import connect_to_mongo, close_mongo_connection, get_database

# Repositories
from repositories.user_repository import UserRepository
from repositories.document_repository import DocumentRepository
from repositories.concept_repository import ConceptRepository
from repositories.legal_section_repository import LegalSectionRepository
from repositories.relation_repository import RelationRepository
from repositories.section_relation_repository import SectionRelationRepository
from repositories.triplet_repository import TripletRepository

# Services
from services.user_service import UserService
from services.document_service import DocumentService
from services.concept_service import ConceptService
from services.legal_section_service import LegalSectionService
from services.relation_service import RelationService
from services.section_relation_service import SectionRelationService
from services.triplet_service import TripletService

# Controllers
from controllers.user_controller import UserController
from controllers.document_controller import DocumentController
from controllers.concept_controller import ConceptController
from controllers.legal_section_controller import LegalSectionController
from controllers.relation_controller import RelationController
from controllers.section_relation_controller import SectionRelationController
from controllers.triplet_controller import TripletController

# Routers
from routers.user_router import create_user_router_with_state
from routers.document_router import create_document_router_with_state
from routers.concept_router import create_concept_router_with_state
from routers.legal_section_router import create_legal_section_router_with_state
from routers.relation_router import create_relation_router_with_state
from routers.section_relation_router import create_section_relation_router_with_state
from routers.triplet_router import create_triplet_router_with_state


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await connect_to_mongo()
    print("Connected to MongoDB")
    
    # Manual Dependency Injection
    db = get_database()
    
    # Initialize repositories
    user_repository = UserRepository(db)
    document_repository = DocumentRepository(db)
    concept_repository = ConceptRepository(db)
    legal_section_repository = LegalSectionRepository(db)
    relation_repository = RelationRepository(db)
    section_relation_repository = SectionRelationRepository(db)
    triplet_repository = TripletRepository(db)
    
    # Initialize services
    user_service = UserService(user_repository)
    document_service = DocumentService(document_repository)
    concept_service = ConceptService(concept_repository)
    legal_section_service = LegalSectionService(legal_section_repository)
    relation_service = RelationService(relation_repository)
    section_relation_service = SectionRelationService(section_relation_repository)
    triplet_service = TripletService(triplet_repository)
    
    # Initialize controllers
    user_controller = UserController(user_service)
    document_controller = DocumentController(document_service)
    concept_controller = ConceptController(concept_service)
    legal_section_controller = LegalSectionController(legal_section_service)
    relation_controller = RelationController(relation_service)
    section_relation_controller = SectionRelationController(section_relation_service)
    triplet_controller = TripletController(triplet_service)
    
    # Store in app state
    app.state.user_controller = user_controller
    app.state.document_controller = document_controller
    app.state.concept_controller = concept_controller
    app.state.legal_section_controller = legal_section_controller
    app.state.relation_controller = relation_controller
    app.state.section_relation_controller = section_relation_controller
    app.state.triplet_controller = triplet_controller

    yield

    # shutdown
    await close_mongo_connection()
    print("Disconnected from MongoDB")


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    
    # Include routers
    app.include_router(create_user_router_with_state())
    app.include_router(create_document_router_with_state())
    app.include_router(create_concept_router_with_state())
    app.include_router(create_legal_section_router_with_state())
    app.include_router(create_relation_router_with_state())
    app.include_router(create_section_relation_router_with_state())
    app.include_router(create_triplet_router_with_state())
    
    return app


app = create_app()
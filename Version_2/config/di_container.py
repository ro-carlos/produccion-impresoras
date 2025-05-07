from typing import Dict, Any, Optional
from datetime import date

from domain.models import SimulationConfig
from domain.services import (
    InventoryService, BOMService, 
    ManufacturingService, PurchasingService
)

from infrastructure.database import Database
from infrastructure.repositories import (
    SQLiteProductRepository, SQLiteBOMRepository, 
    SQLiteSupplierRepository, SQLiteStockRepository,
    SQLiteManufacturingOrderRepository, SQLitePurchaseOrderRepository,
    SQLiteEventRepository
)
from infrastructure.data_export import DataExporter, DataImporter

from application.services import SimulationApplicationService

from config.settings import (
    DB_FILE, DEFAULT_PRODUCTS, DEFAULT_BOM, 
    DEFAULT_SUPPLIERS, DEFAULT_STOCK
)

class DIContainer:
    """
    Contenedor de inyección de dependencias para la aplicación.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el contenedor de inyección de dependencias.
        
        Args:
            config: Configuración de la simulación
        """
        self.config = config
        self.db = None
        self.is_initialized = False
        
        # Repositorios
        self.product_repository = None
        self.bom_repository = None
        self.supplier_repository = None
        self.stock_repository = None
        self.manufacturing_repository = None
        self.purchase_repository = None
        self.event_repository = None
        
        # Servicios de dominio
        self.inventory_service = None
        self.bom_service = None
        self.manufacturing_service = None
        self.purchasing_service = None
        
        # Servicios de aplicación
        self.simulation_service = None
        
        # Utilidades
        self.data_exporter = None
        self.data_importer = None
    
    def initialize(self) -> None:
        """Inicializa todos los componentes del contenedor."""
        if self.is_initialized:
            return
        
        self._initialize_database()
        self._initialize_repositories()
        self._initialize_domain_services()
        self._initialize_application_services()
        self._initialize_utilities()
        
        self.is_initialized = True
    
    def _initialize_database(self) -> None:
        """Inicializa la base de datos."""
        self.db = Database(str(DB_FILE))
        self.db.initialize_db()
    
    def _initialize_repositories(self) -> None:
        """Inicializa los repositorios."""
        self.product_repository = SQLiteProductRepository(self.db)
        self.bom_repository = SQLiteBOMRepository(self.db)
        self.supplier_repository = SQLiteSupplierRepository(self.db)
        self.stock_repository = SQLiteStockRepository(self.db)
        self.manufacturing_repository = SQLiteManufacturingOrderRepository(self.db)
        self.purchase_repository = SQLitePurchaseOrderRepository(self.db)
        self.event_repository = SQLiteEventRepository(self.db)
    
    def _initialize_domain_services(self) -> None:
        """Inicializa los servicios de dominio."""
        self.inventory_service = InventoryService(
            self.stock_repository,
            self.product_repository,
            self.event_repository
        )
        
        self.bom_service = BOMService(
            self.bom_repository,
            self.product_repository
        )
        
        self.manufacturing_service = ManufacturingService(
            self.manufacturing_repository,
            self.bom_service,
            self.inventory_service,
            self.event_repository,
            self.product_repository
        )
        
        self.purchasing_service = PurchasingService(
            self.purchase_repository,
            self.supplier_repository,
            self.inventory_service,
            self.event_repository,
            self.product_repository
        )
    
    def _initialize_application_services(self) -> None:
        """Inicializa los servicios de aplicación."""
        simulation_config = SimulationConfig(
            initial_day=date.fromisoformat(self.config["initial_day"]),
            demand_mean=self.config["demand_mean"],
            demand_std_dev=self.config["demand_std_dev"],
            production_capacity_per_day=self.config["production_capacity_per_day"],
            warehouse_capacity=self.config["warehouse_capacity"]
        )
        
        self.simulation_service = SimulationApplicationService(
            inventory_service=self.inventory_service,
            bom_service=self.bom_service,
            manufacturing_service=self.manufacturing_service,
            purchasing_service=self.purchasing_service,
            
            product_repository=self.product_repository,
            bom_repository=self.bom_repository,
            supplier_repository=self.supplier_repository,
            stock_repository=self.stock_repository,
            manufacturing_repository=self.manufacturing_repository,
            purchase_repository=self.purchase_repository,
            event_repository=self.event_repository,
            
            config=simulation_config
        )
    
    def _initialize_utilities(self) -> None:
        """Inicializa las utilidades."""
        self.data_exporter = DataExporter(
            self.product_repository,
            self.bom_repository,
            self.supplier_repository,
            self.stock_repository,
            self.manufacturing_repository,
            self.purchase_repository,
            self.event_repository
        )
        
        self.data_importer = DataImporter(
            self.product_repository,
            self.bom_repository,
            self.supplier_repository,
            self.stock_repository,
            self.manufacturing_repository,
            self.purchase_repository,
            self.event_repository
        )
    
    def seed_database(self) -> None:
        """Puebla la base de datos con datos iniciales."""
        # Verificar si la base de datos ya tiene datos
        products = self.product_repository.get_all()
        if products:
            return  # La base de datos ya está poblada
        
        # Añadir productos
        for product_data in DEFAULT_PRODUCTS:
            from domain.models import Product
            product = Product(**product_data)
            self.product_repository.add(product)
        
        # Añadir BOM
        for bom_data in DEFAULT_BOM:
            from domain.models import BOM
            bom = BOM(**bom_data)
            self.bom_repository.add(bom)
        
        # Añadir proveedores
        for supplier_data in DEFAULT_SUPPLIERS:
            from domain.models import Supplier
            supplier = Supplier(**supplier_data)
            self.supplier_repository.add(supplier)
        
        # Añadir stock inicial
        for stock_data in DEFAULT_STOCK:
            self.inventory_service.update_stock(
                stock_data["product_id"],
                stock_data["quantity"],
                "Stock inicial"
            )

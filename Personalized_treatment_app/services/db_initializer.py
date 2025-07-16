# services/db_initializer.py

from services.auto_allocator import populate_default_specialist_mappings

def initialize_app():
    """
    Perform one-time setup operations like populating default report-specialist mappings.
    This will only add new mappings if they don't exist.
    """
    print("🔧 Initializing application...")
    populate_default_specialist_mappings()
    print("✅ Initialization complete.")

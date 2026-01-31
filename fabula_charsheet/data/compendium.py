import os
import yaml
import logging
from pathlib import Path
from data.models import Weapon, Armor, Shield, Accessory, Item, Spell, Skill, HeroicSkill, Therioform, Dance, Arcanum, Invention

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Compendium:
    def __init__(self):
        self.weapons = []
        self.armors = []
        self.shields = []
        self.accessories = []
        self.items = []
        self.spells = SpellCompendium()
        self.skills = []
        self.heroic_skills = HeroicSkillCompendium()
        self.therioforms = []
        self.dances = []
        self.arcana = []
        self.inventions = []

    def clear(self):
        """Resets all lists to empty."""
        self.weapons = []
        self.armors = []
        self.shields = []
        self.accessories = []
        self.items = []
        self.spells.clear()
        self.skills = []
        self.heroic_skills.clear()
        self.therioforms = []
        self.dances = []
        self.arcana = []
        self.inventions = []

    def get_all_items(self):
        """Returns a consolidated list of all equipment/items."""
        all_items = []
        for w in self.weapons: all_items.append(("weapon", w))
        for a in self.armors: all_items.append(("armor", a))
        for s in self.shields: all_items.append(("shield", s))
        for acc in self.accessories: all_items.append(("accessory", acc))
        for i in self.items: all_items.append(("item", i))
        return all_items

    def get_class_name_from_skill(self, skill):
        # Placeholder logic: In a real app, you'd map skills to classes
        # This prevents crashes if the method is called
        return "Elementalist" # Default fallback

class SpellCompendium:
    def __init__(self):
        self.spells = {} # Map class_name -> list of spells

    def clear(self):
        self.spells = {}

    def get_spells(self, class_name):
        return self.spells.get(str(class_name), [])

class HeroicSkillCompendium:
    def __init__(self):
        self.heroic_skills = []

    def clear(self):
        self.heroic_skills = []

# --- SINGLETON INSTANTIATION ---
# Crucial: Instantiate immediately so imports never see 'None'
COMPENDIUM = Compendium()

def init(assets_directory: Path | str) -> None:
    """
    Loads all data from the assets directory into the global COMPENDIUM object.
    """
    if isinstance(assets_directory, str):
        assets_directory = Path(assets_directory)

    # Clear existing data before reloading
    COMPENDIUM.clear()
    
    logger.info(f"Loading compendium from {assets_directory}")

    # 1. Load Equipment
    equipment_dir = assets_directory / 'equipment'
    if equipment_dir.exists():
        # Mapping YAML keys/filenames to Compendium lists and Model classes
        load_map = {
            "weapons": (COMPENDIUM.weapons, Weapon),
            "armors": (COMPENDIUM.armors, Armor),
            "shields": (COMPENDIUM.shields, Shield),
            "accessories": (COMPENDIUM.accessories, Accessory),
            "items": (COMPENDIUM.items, Item)
        }

        for category_name, (target_list, model_class) in load_map.items():
            file_path = equipment_dir / f"{category_name}.yaml"
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if data and isinstance(data, list):
                            for item_data in data:
                                try:
                                    target_list.append(model_class(**item_data))
                                except Exception as e:
                                    logger.error(f"Error creating {model_class.__name__}: {e}")
                except Exception as e:
                    logger.error(f"Failed to load {file_path}: {e}")

    # 2. Load Spells
    spells_dir = assets_directory / 'spells'
    if spells_dir.exists():
        for yaml_file in spells_dir.glob("*.yaml"):
            class_name = yaml_file.stem # Filename is class name (e.g. 'elementalist.yaml')
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data:
                        spell_list = [Spell(**s) for s in data]
                        COMPENDIUM.spells.spells[class_name] = spell_list
            except Exception as e:
                logger.error(f"Failed to load spells from {yaml_file}: {e}")

    # 3. Load Heroic Skills
    hs_path = assets_directory / 'heroic_skills.yaml'
    if hs_path.exists():
        try:
            with open(hs_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data:
                    COMPENDIUM.heroic_skills.heroic_skills = [HeroicSkill(**h) for h in data]
        except Exception as e:
            logger.error(f"Failed to load heroic skills: {e}")

    # 4. Load Special (Therioforms, Dances, etc)
    special_files = {
        "therioforms.yaml": (COMPENDIUM.therioforms, Therioform),
        "dances.yaml": (COMPENDIUM.dances, Dance),
        "arcana.yaml": (COMPENDIUM.arcana, Arcanum),
        "inventions.yaml": (COMPENDIUM.inventions, Invention)
    }
    
    for filename, (target_list, model_class) in special_files.items():
        file_path = assets_directory / filename
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data:
                        for item in data:
                            target_list.append(model_class(**item))
            except Exception as e:
                logger.error(f"Failed to load {filename}: {e}")

    logger.info("Compendium initialization complete.")

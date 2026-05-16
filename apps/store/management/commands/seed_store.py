from django.core.management.base import BaseCommand
from apps.store.models import Category, Product

STORE_DATA = {
    "accessories": {
        "categories": [
            {"id": "cases",       "name": "Cases & Covers",    "icon": "□"},
            {"id": "chargers",    "name": "Chargers & Cables",  "icon": "⚡"},
            {"id": "audio",       "name": "Audio",              "icon": "♪"},
            {"id": "power",       "name": "Power Banks",        "icon": "▮"},
            {"id": "mounts",      "name": "Mounts & Stands",    "icon": "△"},
            {"id": "peripherals", "name": "Peripherals",        "icon": "◇"},
        ],
        "products": [
            {"id": "a1",  "name": "Premium Leather Case",       "price": 49.99,  "old_price": 69.99,  "category_id": "cases",       "rating": 4.8, "reviews": 234, "in_stock": True,  "badge": "Sale",        "color": "#4A5568", "variants": ["Black","Tan","Navy"],            "desc": "Hand-stitched Italian leather with microfiber lining. Precision cutouts for all ports."},
            {"id": "a2",  "name": "Wireless Charging Pad",      "price": 34.99,  "old_price": None,   "category_id": "chargers",    "rating": 4.5, "reviews": 189, "in_stock": True,  "badge": None,          "color": "#2D3748", "variants": ["White","Black"],                 "desc": "15W fast wireless charging with intelligent temperature control."},
            {"id": "a3",  "name": "Noise-Cancelling Earbuds",   "price": 129.99, "old_price": 159.99, "category_id": "audio",       "rating": 4.9, "reviews": 412, "in_stock": True,  "badge": "Best Seller", "color": "#1A202C", "variants": [],                               "desc": "Active noise cancellation with 32-hour battery life and spatial audio."},
            {"id": "a4",  "name": "Ultra-Fast Car Charger",     "price": 24.99,  "old_price": None,   "category_id": "chargers",    "rating": 4.3, "reviews": 156, "in_stock": True,  "badge": None,          "color": "#4A5568", "variants": [],                               "desc": "Dual USB-C 65W output for simultaneous device charging."},
            {"id": "a5",  "name": "Tempered Glass Protector",   "price": 14.99,  "old_price": None,   "category_id": "cases",       "rating": 4.6, "reviews": 567, "in_stock": True,  "badge": None,          "color": "#718096", "variants": [],                               "desc": "9H hardness, oleophobic coating, bubble-free installation kit included."},
            {"id": "a6",  "name": "Magnetic Phone Mount",       "price": 29.99,  "old_price": None,   "category_id": "mounts",      "rating": 4.4, "reviews": 201, "in_stock": False, "badge": "Out of Stock","color": "#2D3748", "variants": [],                               "desc": "N52 magnets with 360° rotation. Dashboard and vent compatible."},
            {"id": "a7",  "name": "Power Bank 20000mAh",        "price": 59.99,  "old_price": 79.99,  "category_id": "power",       "rating": 4.7, "reviews": 334, "in_stock": True,  "badge": "Sale",        "color": "#1A202C", "variants": [],                               "desc": "Slim aluminum design with LED display and triple output ports."},
            {"id": "a8",  "name": "Braided USB-C Cable 2m",     "price": 19.99,  "old_price": None,   "category_id": "chargers",    "rating": 4.2, "reviews": 445, "in_stock": True,  "badge": None,          "color": "#4A5568", "variants": [],                               "desc": "Military-grade aramid fiber with 100W PD support."},
            {"id": "a9",  "name": "Bluetooth Speaker Mini",     "price": 44.99,  "old_price": None,   "category_id": "audio",       "rating": 4.5, "reviews": 278, "in_stock": True,  "badge": "New",         "color": "#2D3748", "variants": [],                               "desc": "IPX7 waterproof with 12-hour battery and rich bass radiator."},
            {"id": "a10", "name": "Phone Grip Ring",            "price": 12.99,  "old_price": None,   "category_id": "peripherals", "rating": 4.1, "reviews": 612, "in_stock": True,  "badge": None,          "color": "#A0AEC0", "variants": [],                               "desc": "Zinc alloy ring stand with 180° flip and 360° rotation."},
            {"id": "a11", "name": "Laptop Stand Pro",           "price": 89.99,  "old_price": None,   "category_id": "mounts",      "rating": 4.8, "reviews": 167, "in_stock": True,  "badge": None,          "color": "#4A5568", "variants": [],                               "desc": "CNC aluminum with adjustable height and integrated cable routing."},
            {"id": "a12", "name": "Wireless Mouse Slim",        "price": 39.99,  "old_price": None,   "category_id": "peripherals", "rating": 4.4, "reviews": 223, "in_stock": True,  "badge": "New",         "color": "#718096", "variants": [],                               "desc": "Ultra-thin profile with silent clicks and tri-mode connectivity."},
        ],
    },
    "clothing": {
        "categories": [
            {"id": "tops",      "name": "Tops",       "icon": "▽"},
            {"id": "bottoms",   "name": "Bottoms",    "icon": "△"},
            {"id": "outerwear", "name": "Outerwear",  "icon": "◈"},
            {"id": "dresses",   "name": "Dresses",    "icon": "◇"},
            {"id": "shoes",     "name": "Shoes",      "icon": "□"},
            {"id": "acc",       "name": "Accessories","icon": "○"},
        ],
        "products": [
            {"id": "c1",  "name": "Merino Wool Sweater",   "price": 128, "old_price": 168,  "category_id": "tops",      "rating": 4.8, "reviews": 189, "in_stock": True,  "badge": "Sale",        "color": "#8B7355", "variants": ["Oatmeal","Charcoal","Burgundy"],  "desc": "Extra-fine merino wool in a relaxed silhouette with ribbed hem and cuffs."},
            {"id": "c2",  "name": "Tailored Chino Pants",  "price": 95,  "old_price": None, "category_id": "bottoms",   "rating": 4.6, "reviews": 234, "in_stock": True,  "badge": None,          "color": "#A0926B", "variants": ["Khaki","Navy","Olive"],           "desc": "Slim-tapered fit in brushed cotton twill with stretch comfort."},
            {"id": "c3",  "name": "Linen Button-Down",     "price": 85,  "old_price": None, "category_id": "tops",      "rating": 4.5, "reviews": 167, "in_stock": True,  "badge": "New",         "color": "#C4B9A0", "variants": ["White","Sky","Sand"],             "desc": "Relaxed linen with mother-of-pearl buttons and French seams."},
            {"id": "c4",  "name": "Classic Denim Jacket",  "price": 165, "old_price": 210,  "category_id": "outerwear", "rating": 4.9, "reviews": 312, "in_stock": True,  "badge": "Best Seller", "color": "#5B6C82", "variants": ["Indigo","Black"],                 "desc": "Selvedge denim, vintage wash, copper hardware, blanket-lined."},
            {"id": "c5",  "name": "Cotton Crew T-Shirt",   "price": 45,  "old_price": None, "category_id": "tops",      "rating": 4.3, "reviews": 523, "in_stock": True,  "badge": None,          "color": "#D4CFC4", "variants": ["White","Black","Grey","Navy"],     "desc": "Heavyweight 220gsm organic cotton with reinforced collar."},
            {"id": "c6",  "name": "Wool Blend Overcoat",   "price": 295, "old_price": None, "category_id": "outerwear", "rating": 4.8, "reviews": 98,  "in_stock": True,  "badge": None,          "color": "#3D3D3D", "variants": [],                                "desc": "Double-breasted in Italian wool-cashmere blend. Fully lined."},
            {"id": "c7",  "name": "Silk Evening Blouse",   "price": 142, "old_price": None, "category_id": "tops",      "rating": 4.7, "reviews": 145, "in_stock": True,  "badge": None,          "color": "#8B6F6F", "variants": ["Ivory","Blush","Black"],          "desc": "Mulberry silk charmeuse with French cuff details."},
            {"id": "c8",  "name": "Cashmere Scarf",        "price": 115, "old_price": 155,  "category_id": "acc",       "rating": 4.9, "reviews": 201, "in_stock": True,  "badge": "Sale",        "color": "#B8A88A", "variants": ["Camel","Grey","Black"],           "desc": "Grade-A Mongolian cashmere in a generous oversized wrap."},
            {"id": "c9",  "name": "Leather Belt Classic",  "price": 68,  "old_price": None, "category_id": "acc",       "rating": 4.4, "reviews": 334, "in_stock": True,  "badge": None,          "color": "#5C4033", "variants": [],                                "desc": "Full-grain bridle leather with brushed brass buckle."},
            {"id": "c10", "name": "Oxford Dress Shirt",    "price": 92,  "old_price": None, "category_id": "tops",      "rating": 4.6, "reviews": 267, "in_stock": False, "badge": "Out of Stock","color": "#B8C4D4", "variants": ["White","Blue","Pink"],            "desc": "Thomas Mason cotton oxford with removable collar stays."},
            {"id": "c11", "name": "Suede Chelsea Boots",   "price": 225, "old_price": None, "category_id": "shoes",     "rating": 4.8, "reviews": 178, "in_stock": True,  "badge": None,          "color": "#7D6B5D", "variants": [],                                "desc": "Italian suede, Goodyear welted, natural crepe sole."},
            {"id": "c12", "name": "Pleated Midi Skirt",    "price": 108, "old_price": None, "category_id": "dresses",   "rating": 4.5, "reviews": 156, "in_stock": True,  "badge": "New",         "color": "#9B8B7A", "variants": [],                                "desc": "Fluid pleated construction in matte satin with concealed zip."},
        ],
    },
    "jewelry": {
        "categories": [
            {"id": "rings",     "name": "Rings",       "icon": "○"},
            {"id": "necklaces", "name": "Necklaces",   "icon": "◡"},
            {"id": "earrings",  "name": "Earrings",    "icon": "◆"},
            {"id": "bracelets", "name": "Bracelets",   "icon": "◠"},
            {"id": "watches",   "name": "Watches",     "icon": "◎"},
            {"id": "acc",       "name": "Accessories", "icon": "◇"},
        ],
        "products": [
            {"id": "j1",  "name": "Diamond Solitaire Ring",  "price": 2450, "old_price": 2950, "category_id": "rings",     "rating": 5.0, "reviews": 89,  "in_stock": True,  "badge": "Sale",        "color": "#1A1A2E", "variants": ["White Gold","Yellow Gold","Platinum"], "desc": "0.75ct brilliant-cut diamond, VS1 clarity, set in your choice of precious metal."},
            {"id": "j2",  "name": "Gold Chain Necklace 18K", "price": 1280, "old_price": None, "category_id": "necklaces", "rating": 4.8, "reviews": 134, "in_stock": True,  "badge": None,          "color": "#2D2040", "variants": ["16 inch","18 inch","20 inch"],          "desc": "Solid 18K gold curb chain with lobster clasp. Hallmarked."},
            {"id": "j3",  "name": "Pearl Drop Earrings",     "price": 680,  "old_price": None, "category_id": "earrings",  "rating": 4.9, "reviews": 167, "in_stock": True,  "badge": "Best Seller", "color": "#1E1E32", "variants": [],                                      "desc": "South Sea pearl drops on 14K gold wire with diamond accent."},
            {"id": "j4",  "name": "Tennis Bracelet Silver",  "price": 890,  "old_price": 1100, "category_id": "bracelets", "rating": 4.7, "reviews": 98,  "in_stock": True,  "badge": "Sale",        "color": "#252540", "variants": ["Silver","Gold"],                        "desc": "4mm round-cut cubic zirconia in sterling silver. Box clasp with safety."},
            {"id": "j5",  "name": "Sapphire Pendant",        "price": 1650, "old_price": None, "category_id": "necklaces", "rating": 4.9, "reviews": 76,  "in_stock": True,  "badge": None,          "color": "#1A1A3E", "variants": [],                                      "desc": "Natural blue sapphire surrounded by diamond halo on 18K chain."},
            {"id": "j6",  "name": "Rose Gold Bangle",        "price": 520,  "old_price": None, "category_id": "bracelets", "rating": 4.6, "reviews": 201, "in_stock": True,  "badge": "New",         "color": "#2D1F2D", "variants": [],                                      "desc": "Polished 14K rose gold with subtle brushed texture detail."},
            {"id": "j7",  "name": "Emerald Cut Ring",        "price": 3200, "old_price": None, "category_id": "rings",     "rating": 5.0, "reviews": 45,  "in_stock": True,  "badge": None,          "color": "#1A2E1A", "variants": [],                                      "desc": "1.2ct emerald-cut diamond flanked by tapered baguettes."},
            {"id": "j8",  "name": "Layered Chain Set",       "price": 420,  "old_price": None, "category_id": "necklaces", "rating": 4.5, "reviews": 267, "in_stock": True,  "badge": None,          "color": "#2A2A3E", "variants": [],                                      "desc": "Three delicate chains at 16, 18, and 20 inches in 14K gold."},
            {"id": "j9",  "name": "Vintage Brooch Pearl",    "price": 340,  "old_price": None, "category_id": "acc",       "rating": 4.4, "reviews": 112, "in_stock": False, "badge": "Out of Stock","color": "#3D2D3D", "variants": [],                                      "desc": "Art deco inspired design with freshwater pearls and marcasite."},
            {"id": "j10", "name": "Chronograph Watch",       "price": 4500, "old_price": 5200, "category_id": "watches",   "rating": 4.9, "reviews": 67,  "in_stock": True,  "badge": "Sale",        "color": "#1A1A1A", "variants": [],                                      "desc": "Swiss automatic movement, sapphire crystal, 100m water resistance."},
            {"id": "j11", "name": "Anklet Chain Delicate",   "price": 180,  "old_price": None, "category_id": "acc",       "rating": 4.3, "reviews": 189, "in_stock": True,  "badge": None,          "color": "#2D2D40", "variants": [],                                      "desc": "Fine cable chain in 14K gold with adjustable length."},
            {"id": "j12", "name": "Cufflink Set Gold",       "price": 290,  "old_price": None, "category_id": "acc",       "rating": 4.6, "reviews": 145, "in_stock": True,  "badge": "New",         "color": "#1E1E2E", "variants": [],                                      "desc": "18K gold-plated with onyx inlay and toggle back."},
        ],
    },
}


class Command(BaseCommand):
    help = "Seed the database with store categories and products from store-data.js"

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Delete all existing store data before seeding")

    def handle(self, *args, **options):
        if options["clear"]:
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared all existing store data."))

        total_cats = 0
        total_products = 0

        for store_type, data in STORE_DATA.items():
            for cat in data["categories"]:
                # Categories share ids across stores (e.g. "acc"), so scope the pk
                pk = f"{store_type}__{cat['id']}"
                obj, created = Category.objects.update_or_create(
                    id=pk,
                    defaults={
                        "name": cat["name"],
                        "icon": cat["icon"],
                        "store_type": store_type,
                    },
                )
                total_cats += 1

            for p in data["products"]:
                cat_pk = f"{store_type}__{p['category_id']}"
                obj, created = Product.objects.update_or_create(
                    id=p["id"],
                    defaults={
                        "name": p["name"],
                        "category_id": cat_pk,
                        "price": p["price"],
                        "old_price": p["old_price"],
                        "rating": p["rating"],
                        "reviews": p["reviews"],
                        "in_stock": p["in_stock"],
                        "badge": p["badge"],
                        "color": p["color"],
                        "variants": p["variants"],
                        "desc": p["desc"],
                        "store_type": store_type,
                    },
                )
                total_products += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done. {total_cats} categories and {total_products} products seeded."
        ))

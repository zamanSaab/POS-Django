import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone


CATEGORIES = {
    "accessories": [
        ("cases", "Cases & Covers", "📱"),
        ("audio", "Audio", "🎧"),
        ("chargers", "Chargers & Cables", "🔌"),
        ("wearables", "Wearables", "⌚"),
        ("storage", "Storage", "💾"),
        ("cameras", "Cameras", "📷"),
    ],
    "clothing": [
        ("tops", "Tops & Shirts", "👕"),
        ("bottoms", "Bottoms", "👖"),
        ("outerwear", "Outerwear", "🧥"),
        ("footwear", "Footwear", "👟"),
        ("accessories-c", "Accessories", "🧣"),
        ("activewear", "Activewear", "🏃"),
    ],
    "jewelry": [
        ("rings", "Rings", "💍"),
        ("necklaces", "Necklaces", "📿"),
        ("earrings", "Earrings", "💎"),
        ("bracelets", "Bracelets", "⌚"),
        ("watches", "Watches", "🕐"),
        ("brooches", "Brooches", "✨"),
    ],
}

PRODUCTS = {
    "accessories": [
        {"id": "a1", "name": "Obsidian Shield Pro Case", "category": "cases", "price": "49.99", "old_price": "69.99", "badge": "Sale", "color": "#1a1a2e", "desc": "Military-grade protection with premium matte finish.", "variants": ["iPhone 15 Pro", "iPhone 15", "Galaxy S24"], "rating": "4.8", "reviews": 342},
        {"id": "a2", "name": "AuraSound Elite Headphones", "category": "audio", "price": "299.99", "old_price": None, "badge": "Best Seller", "color": "#2d1b69", "desc": "Studio-quality sound with active noise cancellation.", "variants": ["Midnight Black", "Ivory White", "Rose Gold"], "rating": "4.9", "reviews": 891},
        {"id": "a3", "name": "VoltEdge 140W GaN Charger", "category": "chargers", "price": "79.99", "old_price": "99.99", "badge": "Sale", "color": "#0d3b2e", "desc": "4-port GaN charger powering all your devices simultaneously.", "variants": ["Standard", "Travel Kit"], "rating": "4.7", "reviews": 256},
        {"id": "a4", "name": "Apex Ultra Smart Watch", "category": "wearables", "price": "449.99", "old_price": None, "badge": "New", "color": "#1c1c1e", "desc": "Advanced health monitoring with titanium build.", "variants": ["45mm", "49mm"], "rating": "4.8", "reviews": 423},
        {"id": "a5", "name": "NanoVault 2TB SSD", "category": "storage", "price": "189.99", "old_price": "229.99", "badge": "Sale", "color": "#2c3e50", "desc": "Lightning-fast portable SSD with military encryption.", "variants": ["1TB", "2TB", "4TB"], "rating": "4.9", "reviews": 567},
        {"id": "a6", "name": "LensMax Pro Camera Kit", "category": "cameras", "price": "129.99", "old_price": None, "badge": None, "color": "#1a1a1a", "desc": "Professional smartphone camera lens system.", "variants": ["iPhone", "Android Universal"], "rating": "4.6", "reviews": 189},
        {"id": "a7", "name": "Crystal Armor Glass Screen", "category": "cases", "price": "29.99", "old_price": "39.99", "badge": "Sale", "color": "#e8e8e8", "desc": "9H hardness tempered glass with oleophobic coating.", "variants": ["iPhone 15 Pro Max", "iPhone 15 Pro", "Galaxy S24 Ultra"], "rating": "4.7", "reviews": 1204},
        {"id": "a8", "name": "BassCore Wireless Earbuds", "category": "audio", "price": "149.99", "old_price": None, "badge": "New", "color": "#2d1b69", "desc": "Premium earbuds with 36-hour battery and spatial audio.", "variants": ["Midnight", "Pearl White"], "rating": "4.8", "reviews": 734},
        {"id": "a9", "name": "MagSafe Duo Elite Pad", "category": "chargers", "price": "119.99", "old_price": "149.99", "badge": "Sale", "color": "#f5f5f7", "desc": "Simultaneous wireless charging for phone and watch.", "variants": ["Standard"], "rating": "4.6", "reviews": 298},
        {"id": "a10", "name": "HaloFit Smart Ring", "category": "wearables", "price": "349.99", "old_price": None, "badge": "New", "color": "#1c1c1e", "desc": "24/7 health tracking in a titanium smart ring.", "variants": ["Size 7", "Size 8", "Size 9", "Size 10"], "rating": "4.5", "reviews": 156},
        {"id": "a11", "name": "FlashDrive Luxe 512GB", "category": "storage", "price": "89.99", "old_price": None, "badge": None, "color": "#gold", "desc": "Ultra-slim USB-C flash drive with premium gold finish.", "variants": ["256GB", "512GB", "1TB"], "rating": "4.7", "reviews": 321},
        {"id": "a12", "name": "Gimbal Pro Stabilizer", "category": "cameras", "price": "199.99", "old_price": "249.99", "badge": "Sale", "color": "#1a1a1a", "desc": "3-axis stabilizer for cinematic smartphone videos.", "variants": ["Standard", "Pro Bundle"], "rating": "4.8", "reviews": 412},
    ],
    "clothing": [
        {"id": "c1", "name": "Onyx Merino Turtleneck", "category": "tops", "price": "189.99", "old_price": None, "badge": "Best Seller", "color": "#1a1a1a", "desc": "Superfine merino wool turtleneck with cashmere blend.", "variants": ["XS", "S", "M", "L", "XL"], "rating": "4.9", "reviews": 567},
        {"id": "c2", "name": "Slate Slim-Fit Trousers", "category": "bottoms", "price": "229.99", "old_price": "279.99", "badge": "Sale", "color": "#708090", "desc": "Italian wool-blend trousers with precision tailoring.", "variants": ["28x30", "30x30", "32x30", "34x32"], "rating": "4.8", "reviews": 342},
        {"id": "c3", "name": "Obsidian Moto Jacket", "category": "outerwear", "price": "599.99", "old_price": None, "badge": "New", "color": "#1a1a1a", "desc": "Full-grain leather motorcycle jacket with satin lining.", "variants": ["S", "M", "L", "XL", "XXL"], "rating": "4.9", "reviews": 234},
        {"id": "c4", "name": "Phantom Runner Elite", "category": "footwear", "price": "299.99", "old_price": "349.99", "badge": "Sale", "color": "#2d1b69", "desc": "Carbon-plate performance runner with luxury finish.", "variants": ["US 7", "US 8", "US 9", "US 10", "US 11", "US 12"], "rating": "4.7", "reviews": 891},
        {"id": "c5", "name": "Silk Duchess Scarf", "category": "accessories-c", "price": "149.99", "old_price": None, "badge": None, "color": "#8b1a1a", "desc": "Hand-painted 100% silk scarf from Como, Italy.", "variants": ["One Size"], "rating": "4.8", "reviews": 156},
        {"id": "c6", "name": "Velocity Compression Set", "category": "activewear", "price": "179.99", "old_price": "219.99", "badge": "Sale", "color": "#0d3b2e", "desc": "4-way stretch compression training set with cooling tech.", "variants": ["XS", "S", "M", "L", "XL"], "rating": "4.6", "reviews": 423},
        {"id": "c7", "name": "Ivory Linen Blazer", "category": "tops", "price": "449.99", "old_price": None, "badge": "New", "color": "#f5f0e8", "desc": "Unstructured summer blazer in premium Italian linen.", "variants": ["36R", "38R", "40R", "42R", "44R"], "rating": "4.8", "reviews": 189},
        {"id": "c8", "name": "Noir Denim Selvedge", "category": "bottoms", "price": "279.99", "old_price": None, "badge": None, "color": "#1a1a2e", "desc": "Japanese selvedge denim with hand-finished details.", "variants": ["28", "30", "32", "34", "36"], "rating": "4.9", "reviews": 534},
        {"id": "c9", "name": "Alpine Down Overcoat", "category": "outerwear", "price": "899.99", "old_price": "1099.99", "badge": "Sale", "color": "#2c3e50", "desc": "800-fill down overcoat with cashmere outer shell.", "variants": ["S", "M", "L", "XL"], "rating": "4.9", "reviews": 298},
        {"id": "c10", "name": "Velvet Chelsea Boots", "category": "footwear", "price": "399.99", "old_price": None, "badge": "Best Seller", "color": "#4a0404", "desc": "Hand-crafted velvet Chelsea boots on leather sole.", "variants": ["US 7", "US 8", "US 9", "US 10", "US 11"], "rating": "4.8", "reviews": 412},
        {"id": "c11", "name": "Cashmere Beanie Luxe", "category": "accessories-c", "price": "119.99", "old_price": "149.99", "badge": "Sale", "color": "#8b7355", "desc": "100% Grade A cashmere ribbed beanie.", "variants": ["One Size"], "rating": "4.7", "reviews": 267},
        {"id": "c12", "name": "Carbon Yoga Set", "category": "activewear", "price": "249.99", "old_price": None, "badge": "New", "color": "#1a1a1a", "desc": "Studio-to-street yoga set in buttery-soft Pima cotton.", "variants": ["XS", "S", "M", "L", "XL"], "rating": "4.8", "reviews": 345},
    ],
    "jewelry": [
        {"id": "j1", "name": "Eternity Diamond Band", "category": "rings", "price": "2999.99", "old_price": None, "badge": "Best Seller", "color": "#e8d5b7", "desc": "Full eternity band with 2ct total weight VS1 diamonds.", "variants": ["Size 5", "Size 6", "Size 7", "Size 8"], "rating": "4.9", "reviews": 234},
        {"id": "j2", "name": "Celestial Pearl Necklace", "category": "necklaces", "price": "1299.99", "old_price": "1599.99", "badge": "Sale", "color": "#f8f8ff", "desc": "South Sea pearl strand with 18K white gold clasp.", "variants": ["16 inch", "18 inch", "20 inch"], "rating": "4.8", "reviews": 156},
        {"id": "j3", "name": "Sapphire Halo Earrings", "category": "earrings", "price": "1899.99", "old_price": None, "badge": "New", "color": "#0f52ba", "desc": "Ceylon sapphire studs with pavé diamond halo in platinum.", "variants": ["Standard"], "rating": "4.9", "reviews": 89},
        {"id": "j4", "name": "Tennis Chain Bracelet", "category": "bracelets", "price": "4499.99", "old_price": "5499.99", "badge": "Sale", "color": "#e8d5b7", "desc": "5ct diamond tennis bracelet in 18K yellow gold.", "variants": ["6.5 inch", "7 inch", "7.5 inch"], "rating": "4.9", "reviews": 312},
        {"id": "j5", "name": "Tourbillon Prestige Watch", "category": "watches", "price": "12999.99", "old_price": None, "badge": "New", "color": "#1a1a1a", "desc": "Swiss tourbillon movement in rose gold with alligator strap.", "variants": ["40mm", "44mm"], "rating": "5.0", "reviews": 67},
        {"id": "j6", "name": "Art Deco Brooch", "category": "brooches", "price": "899.99", "old_price": "1099.99", "badge": "Sale", "color": "#2d1b69", "desc": "Vintage-inspired art deco brooch with sapphires and diamonds.", "variants": ["Standard"], "rating": "4.7", "reviews": 45},
        {"id": "j7", "name": "Infinity Rose Gold Ring", "category": "rings", "price": "799.99", "old_price": None, "badge": None, "color": "#b76e79", "desc": "14K rose gold infinity band with pavé diamonds.", "variants": ["Size 5", "Size 6", "Size 7", "Size 8", "Size 9"], "rating": "4.8", "reviews": 423},
        {"id": "j8", "name": "Layered Gold Necklace Set", "category": "necklaces", "price": "599.99", "old_price": "749.99", "badge": "Sale", "color": "#ffd700", "desc": "Three-piece layered necklace set in 14K gold vermeil.", "variants": ["Standard"], "rating": "4.8", "reviews": 567},
        {"id": "j9", "name": "Diamond Huggie Earrings", "category": "earrings", "price": "1199.99", "old_price": None, "badge": "Best Seller", "color": "#e8d5b7", "desc": "Pavé diamond huggies in 18K white gold.", "variants": ["Small", "Medium", "Large"], "rating": "4.9", "reviews": 678},
        {"id": "j10", "name": "Emerald Cuff Bracelet", "category": "bracelets", "price": "2199.99", "old_price": None, "badge": "New", "color": "#50c878", "desc": "Colombian emerald bangle in hammered 18K gold.", "variants": ["Small", "Medium", "Large"], "rating": "4.8", "reviews": 123},
        {"id": "j11", "name": "Chronograph Sport Watch", "category": "watches", "price": "3499.99", "old_price": "3999.99", "badge": "Sale", "color": "#1c1c1e", "desc": "Swiss automatic chronograph with ceramic bezel.", "variants": ["42mm", "44mm"], "rating": "4.7", "reviews": 234},
        {"id": "j12", "name": "Pearl & Gold Brooch", "category": "brooches", "price": "449.99", "old_price": None, "badge": None, "color": "#f8f8ff", "desc": "Freshwater pearl cluster brooch in 14K yellow gold.", "variants": ["Standard"], "rating": "4.6", "reviews": 78},
    ],
}

ORDER_STATUSES = ["processing", "shipped", "out_for_delivery", "delivered", "cancelled"]
PAYMENT_METHODS = ["card", "cash", "wallet", "bank"]
PKR_RATE = Decimal("280")


class Command(BaseCommand):
    help = "Seed the database with development data. Only runs when DEBUG=True."

    def handle(self, *args, **options):
        from django.conf import settings
        from django.core.management.base import CommandError
        if not settings.DEBUG:
            raise CommandError("Seed command is disabled in non-DEBUG environments.")
        self.stdout.write("Seeding database...")
        self._seed_users()
        self._seed_categories()
        self._seed_products()
        self._seed_orders()
        self._seed_notifications()
        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))

    def _seed_users(self):
        from apps.accounts.models import User
        if not User.objects.filter(email="admin@luxepos.com").exists():
            User.objects.create_superuser(
                email="admin@luxepos.com",
                name="LUXE Admin",
                password="admin123",
            )
            self.stdout.write("  Created admin user")

        if not User.objects.filter(email="customer@example.com").exists():
            User.objects.create_user(
                email="customer@example.com",
                name="Jane Smith",
                password="customer123",
                role="customer",
                phone="+92 300 1234567",
                shipping_address="House 12, Block B",
                shipping_city="Lahore",
                shipping_zip="54000",
            )
            self.stdout.write("  Created customer user")

    def _seed_categories(self):
        from apps.store.models import Category
        for store_type, cats in CATEGORIES.items():
            for cat_id, name, icon in cats:
                Category.objects.get_or_create(
                    id=cat_id,
                    defaults={"name": name, "icon": icon, "store_type": store_type},
                )
        self.stdout.write("  Categories seeded")

    def _seed_products(self):
        from apps.store.models import Product, Category
        for store_type, products in PRODUCTS.items():
            for p in products:
                cat = Category.objects.filter(id=p["category"]).first()
                Product.objects.get_or_create(
                    id=p["id"],
                    defaults={
                        "name": p["name"],
                        "category": cat,
                        "price": (Decimal(p["price"]) * PKR_RATE).quantize(Decimal("1")),
                        "old_price": (Decimal(p["old_price"]) * PKR_RATE).quantize(Decimal("1")) if p["old_price"] else None,
                        "badge": p.get("badge"),
                        "color": p["color"],
                        "desc": p["desc"],
                        "variants": p["variants"],
                        "store_type": store_type,
                        "rating": Decimal(str(p["rating"])),
                        "reviews": p["reviews"],
                        "in_stock": True,
                    },
                )
        self.stdout.write("  Products seeded")

    def _seed_orders(self):
        from apps.accounts.models import User
        from apps.store.models import Product
        from apps.orders.models import Order, OrderItem, OrderTimeline

        customer = User.objects.filter(email="customer@example.com").first()
        products = list(Product.objects.all())
        if not products:
            return

        sample_orders = [
            {"customer_name": "Jane Smith", "email": "customer@example.com", "phone": "+92 300 1234567", "status": "delivered", "payment_method": "card", "city": "Lahore", "zip": "54000"},
            {"customer_name": "Ali Khan", "email": "ali@example.com", "phone": "+92 321 5550102", "status": "shipped", "payment_method": "card", "city": "Karachi", "zip": "74000"},
            {"customer_name": "Sara Ahmed", "email": "sara@example.com", "phone": "+92 333 5550103", "status": "processing", "payment_method": "wallet", "city": "Islamabad", "zip": "44000"},
            {"customer_name": "Hassan Raza", "email": "hassan@example.com", "phone": "+92 345 5550104", "status": "out_for_delivery", "payment_method": "card", "city": "Rawalpindi", "zip": "46000"},
            {"customer_name": "Ayesha Malik", "email": "ayesha@example.com", "phone": "+92 300 5550105", "status": "cancelled", "payment_method": "cash", "city": "Faisalabad", "zip": "38000"},
            {"customer_name": "Bilal Shah", "email": "bilal@example.com", "phone": "+92 322 5550106", "status": "delivered", "payment_method": "bank", "city": "Multan", "zip": "60000"},
            {"customer_name": "Mina Tariq", "email": "mina@example.com", "phone": "+92 336 5550107", "status": "processing", "payment_method": "card", "city": "Peshawar", "zip": "25000"},
            {"customer_name": "Omar Farooq", "email": "omar@example.com", "phone": "+92 301 5550108", "status": "shipped", "payment_method": "wallet", "city": "Quetta", "zip": "87300"},
        ]

        for i, od in enumerate(sample_orders):
            if Order.objects.filter(customer_name=od["customer_name"], email=od["email"]).exists():
                continue
            selected = random.sample(products, min(2, len(products)))
            subtotal = sum(p.price * random.randint(1, 3) for p in selected)
            discount = Decimal("0")
            delivery_fee = Decimal("0") if subtotal >= Decimal("10000") else Decimal("250")
            tax = subtotal * Decimal("0.08")
            total = subtotal + tax + delivery_fee

            order = Order.objects.create(
                user=customer if i == 0 else None,
                customer_name=od["customer_name"],
                email=od["email"],
                phone=od["phone"],
                status=od["status"],
                payment_method=od["payment_method"],
                payment_status="confirmed" if od["payment_method"] != "cash" else "pending",
                subtotal=subtotal,
                discount=discount,
                tax=tax,
                delivery_fee=delivery_fee,
                total=total,
                shipping_address=f"{100 + i} Main Street",
                shipping_city=od["city"],
                shipping_zip=od["zip"],
            )

            for p in selected:
                qty = random.randint(1, 3)
                OrderItem.objects.create(
                    order=order,
                    product=p,
                    name=p.name,
                    price=p.price,
                    qty=qty,
                    variant=p.variants[0] if p.variants else "",
                )

            OrderTimeline.objects.create(order=order, step="Order Placed", status="done", time=order.created_at, detail="Order confirmed.")
            if od["status"] != "cancelled":
                OrderTimeline.objects.create(order=order, step="Processing", status="done" if od["status"] != "processing" else "current", time=order.created_at, detail="Preparing order.")

        self.stdout.write("  Orders seeded")

    def _seed_notifications(self):
        from apps.accounts.models import User
        from apps.notifications.models import Notification

        customer = User.objects.filter(email="customer@example.com").first()
        if not customer:
            return

        notifications = [
            ("order", "Order Delivered", "Your order ORD-0001 has been delivered successfully."),
            ("order", "Order Shipped", "Your order ORD-0002 is on its way!"),
            ("promo", "Weekend Sale", "Enjoy 20% off all accessories this weekend. Use code LUXE20."),
            ("promo", "New Arrivals", "Discover our latest jewelry collection — now available in store."),
            ("stock", "Back in Stock", "AuraSound Elite Headphones are back in stock. Grab yours now!"),
            ("system", "Profile Updated", "Your account profile has been updated successfully."),
            ("system", "Welcome to LUXE POS", "Thank you for joining LUXE POS. Explore our luxury collections."),
            ("order", "Order Processing", "Your order ORD-0003 is being prepared."),
            ("promo", "Members Exclusive", "As a valued member, enjoy early access to our summer collection."),
            ("stock", "Low Stock Alert", "Tourbillon Prestige Watch — only 2 left in stock."),
        ]

        for notif_type, title, body in notifications:
            if not Notification.objects.filter(user=customer, title=title).exists():
                Notification.objects.create(user=customer, type=notif_type, title=title, body=body)

        self.stdout.write("  Notifications seeded")

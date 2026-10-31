"""Category rules for eBay/Amazon resale items.

Keyword-based matching with confidence scoring. Each rule has:
- category_id: unique identifier
- category_path: human-readable path like "Electronics > Phones > Smartphones"
- keywords: list of keywords that trigger this category (case-insensitive substring match)
- platforms: optional list of platforms this rule applies to ("ebay", "amazon", or both)
- min_price/max_price: optional price range filters
- confidence: base confidence score (0-1) for this rule
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CategoryRule:
    """A rule for mapping items to categories based on keywords."""

    category_id: str
    category_path: str
    keywords: list[str]
    platforms: list[str] = field(default_factory=lambda: ["ebay", "amazon"])
    min_price: float | None = None
    max_price: float | None = None
    confidence: float = 0.8

    def matches(self, title: str, platform: str = "", price: float | None = None) -> float:
        """Return confidence if this rule matches, else 0.0."""
        title_lower = title.lower()

        # Platform check
        if platform and self.platforms and platform.lower() not in [p.lower() for p in self.platforms]:
            return 0.0

        # Price range check
        if price is not None:
            if self.min_price is not None and price < self.min_price:
                return 0.0
            if self.max_price is not None and price > self.max_price:
                return 0.0

        # Keyword matching - any keyword match triggers the rule
        for kw in self.keywords:
            if kw.lower() in title_lower:
                return self.confidence

        return 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "category_id": self.category_id,
            "category_path": self.category_path,
            "keywords": self.keywords,
            "platforms": self.platforms,
            "min_price": self.min_price,
            "max_price": self.max_price,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CategoryRule":
        return cls(
            category_id=data["category_id"],
            category_path=data["category_path"],
            keywords=data["keywords"],
            platforms=data.get("platforms", ["ebay", "amazon"]),
            min_price=data.get("min_price"),
            max_price=data.get("max_price"),
            confidence=data.get("confidence", 0.8),
        )


# Default category rules for common resale items
DEFAULT_RULES: list[CategoryRule] = [
    # Electronics
    CategoryRule("electronics-phones-smartphones", "Electronics > Phones > Smartphones",
        ["iphone", "android", "smartphone", "galaxy s", "pixel", "oneplus", "motorola"],
        confidence=0.95),
    CategoryRule("electronics-phones-accessories", "Electronics > Phones > Accessories",
        ["phone case", "screen protector", "charger cable", "wireless charger", "pop socket", "phone mount"],
        confidence=0.9),
    CategoryRule("electronics-laptops", "Electronics > Computers > Laptops",
        ["laptop", "macbook", "notebook", "chromebook", "thinkpad", "xps", "surface laptop"],
        confidence=0.95),
    CategoryRule("electronics-tablets", "Electronics > Computers > Tablets",
        ["ipad", "tablet", "galaxy tab", "surface pro", "kindle fire", "android tablet"],
        confidence=0.95),
    CategoryRule("electronics-audio-headphones", "Electronics > Audio > Headphones",
        ["headphones", "earbuds", "airpods", "earphones", "headset", "bluetooth headphones"],
        confidence=0.95),
    CategoryRule("electronics-audio-speakers", "Electronics > Audio > Speakers",
        ["bluetooth speaker", "portable speaker", "smart speaker", "soundbar", "bookshelf speaker"],
        confidence=0.9),
    CategoryRule("electronics-cameras", "Electronics > Cameras > Digital Cameras",
        ["camera", "dslr", "mirrorless", "gopro", "action cam", "point and shoot"],
        confidence=0.9),
    CategoryRule("electronics-gaming-consoles", "Electronics > Gaming > Consoles",
        ["playstation", "xbox", "nintendo switch", "ps5", "ps4", "xbox series", "nintendo ds"],
        confidence=0.95),
    CategoryRule("electronics-gaming-games", "Electronics > Gaming > Video Games",
        ["video game", "game cartridge", "game disc", "switch game", "ps5 game", "xbox game"],
        confidence=0.9),
    CategoryRule("electronics-wearables", "Electronics > Wearables > Smartwatches",
        ["apple watch", "galaxy watch", "smartwatch", "fitbit", "garmin watch", "wearable"],
        confidence=0.9),
    CategoryRule("electronics-tv", "Electronics > TV & Video > Televisions",
        ["tv", "television", "smart tv", "oled tv", "4k tv", "qled", "led tv"],
        confidence=0.9),
    CategoryRule("electronics-components", "Electronics > Components > Parts",
        ["motherboard", "cpu", "gpu", "ram", "ssd", "hard drive", "power supply", "graphics card"],
        confidence=0.85),

    # Clothing & Accessories
    CategoryRule("clothing-mens-shirts", "Clothing > Men > Shirts",
        ["men's shirt", "mens shirt", "t-shirt", "tee shirt", "polo", "button down", "flannel"],
        confidence=0.9),
    CategoryRule("clothing-womens-tops", "Clothing > Women > Tops",
        ["women's top", "womens top", "blouse", "tank top", "camisole", "women's shirt"],
        confidence=0.9),
    CategoryRule("clothing-pants-jeans", "Clothing > Pants > Jeans",
        ["jeans", "denim", "levis", "wranger", "lee jeans"],
        confidence=0.95),
    CategoryRule("clothing-shoes-sneakers", "Clothing > Shoes > Sneakers",
        ["sneakers", "running shoes", "nike", "adidas", "jordan", "yeezy", "new balance", "converse"],
        confidence=0.95),
    CategoryRule("clothing-shoes-boots", "Clothing > Shoes > Boots",
        ["boots", "work boots", "hiking boots", "cowboy boots", "ankle boots", "timberland"],
        confidence=0.9),
    CategoryRule("clothing-jackets", "Clothing > Outerwear > Jackets",
        ["jacket", "coat", "hoodie", "windbreaker", "puffer", "blazer", "denim jacket"],
        confidence=0.9),
    CategoryRule("clothing-accessories", "Clothing > Accessories",
        ["belt", "wallet", "hat", "cap", "beanie", "scarf", "gloves", "sunglasses", "watch band"],
        confidence=0.85),

    # Home & Garden
    CategoryRule("home-kitchen-cookware", "Home > Kitchen > Cookware",
        ["pot", "pan", "skillet", "dutch oven", "baking sheet", "cast iron", "nonstick"],
        confidence=0.9),
    CategoryRule("home-kitchen-appliances", "Home > Kitchen > Appliances",
        ["blender", "air fryer", "instant pot", "coffee maker", "toaster", "microwave", "stand mixer"],
        confidence=0.9),
    CategoryRule("home-furniture", "Home > Furniture",
        ["sofa", "couch", "chair", "table", "desk", "bed frame", "dresser", "bookshelf", "ottoman"],
        confidence=0.85),
    CategoryRule("home-decor", "Home > Decor",
        ["wall art", "vase", "candle", "picture frame", "mirror", "rug", "throw pillow", "blanket"],
        confidence=0.8),
    CategoryRule("home-garden-tools", "Home > Garden > Tools",
        ["lawn mower", "hedge trimmer", "leaf blower", "pressure washer", "garden hose", "shovel"],
        confidence=0.9),

    # Books & Media
    CategoryRule("books-fiction", "Books > Fiction",
        ["novel", "fiction", "paperback", "hardcover", "bestseller", "mystery", "romance", "sci-fi", "fantasy"],
        confidence=0.9),
    CategoryRule("books-nonfiction", "Books > Non-Fiction",
        ["biography", "memoir", "history", "self help", "business book", "cookbook", "textbook", "guide"],
        confidence=0.85),
    CategoryRule("books-comics", "Books > Comics & Graphic Novels",
        ["comic", "graphic novel", "manga", "anime", "marvel", "dc comics", "omnibus"],
        confidence=0.95),
    CategoryRule("media-dvd", "Media > Movies & TV > DVD",
        ["dvd", "blu-ray", "bluray", "4k uhd", "movie collection", "tv series"],
        confidence=0.9),
    CategoryRule("media-vinyl", "Media > Music > Vinyl",
        ["vinyl", "record", "lp ", "ep ", "45 rpm", "33 rpm", "turntable"],
        confidence=0.95),

    # Sports & Outdoors
    CategoryRule("sports-fitness", "Sports > Fitness > Equipment",
        ["dumbbell", "kettlebell", "yoga mat", "resistance band", "treadmill", "elliptical", "weight bench"],
        confidence=0.9),
    CategoryRule("sports-outdoor-camping", "Sports > Outdoors > Camping",
        ["tent", "sleeping bag", "camp stove", "backpack", "hiking", "camping", "lantern"],
        confidence=0.9),
    CategoryRule("sports-bikes", "Sports > Cycling > Bikes",
        ["bicycle", "bike", "mountain bike", "road bike", "ebike", "electric bike"],
        confidence=0.95),
    CategoryRule("sports-golf", "Sports > Golf",
        ["golf club", "golf ball", "golf bag", "putter", "driver", "iron set"],
        confidence=0.95),

    # Toys & Games
    CategoryRule("toys-lego", "Toys > Building Toys > LEGO",
        ["lego", "duplo", "technic", "minifigure", "brick"],
        confidence=0.98),
    CategoryRule("toys-boardgames", "Toys > Games > Board Games",
        ["board game", "card game", "catan", "ticket to ride", "pandemic", "dungeons & dragons"],
        confidence=0.9),
    CategoryRule("toys-action-figures", "Toys > Action Figures",
        ["action figure", "funko pop", "collectible figure", "statue", "hot toys"],
        confidence=0.9),
    CategoryRule("toys-dolls", "Toys > Dolls",
        ["doll", "barbie", "american girl", "baby doll", "fashion doll"],
        confidence=0.9),

    # Beauty & Personal Care
    CategoryRule("beauty-makeup", "Beauty > Makeup",
        ["lipstick", "foundation", "mascara", "eyeshadow", "blush", "concealer", "makeup palette"],
        confidence=0.9),
    CategoryRule("beauty-skincare", "Beauty > Skincare",
        ["moisturizer", "serum", "cleanser", "toner", "sunscreen", "retinol", "hyaluronic acid"],
        confidence=0.9),
    CategoryRule("beauty-hair", "Beauty > Hair Care",
        ["shampoo", "conditioner", "hair dryer", "flat iron", "curling iron", "hair oil"],
        confidence=0.85),

    # Automotive
    CategoryRule("auto-parts", "Automotive > Parts & Accessories",
        ["brake pads", "rotor", "oil filter", "air filter", "spark plug", "battery", "wiper blade"],
        confidence=0.9),
    CategoryRule("auto-tools", "Automotive > Tools",
        ["jack", "torque wrench", "socket set", "obd2", "code reader", "multimeter"],
        confidence=0.9),

    # Collectibles
    CategoryRule("collectibles-cards", "Collectibles > Trading Cards",
        ["pokemon card", "magic card", "yugioh", "sports card", "baseball card", "trading card"],
        confidence=0.98),
    CategoryRule("collectibles-coins", "Collectibles > Coins & Currency",
        ["coin", "silver dollar", "gold coin", "proof set", "mint set", "currency"],
        confidence=0.9),
    CategoryRule("collectibles-funko", "Collectibles > Figures > Funko Pop",
        ["funko pop", "pop vinyl", "funko", "vinyl figure"],
        confidence=0.95),

    # Jewelry & Watches
    CategoryRule("jewelry-watches", "Jewelry > Watches",
        ["watch", "rolex", "omega", "seiko", "citizen", "timex", "automatic watch", "quartz watch"],
        confidence=0.95),
    CategoryRule("jewelry-fine", "Jewelry > Fine Jewelry",
        ["gold ring", "diamond", "necklace", "bracelet", "earrings", "pendant", "14k", "18k", "sterling silver"],
        confidence=0.85),

    # Musical Instruments
    CategoryRule("music-guitars", "Musical Instruments > Guitars",
        ["guitar", "acoustic guitar", "electric guitar", "bass guitar", "fender", "gibson", "ibanez"],
        confidence=0.95),
    CategoryRule("music-keyboards", "Musical Instruments > Keyboards",
        ["keyboard", "digital piano", "synthesizer", "midi controller", "stage piano"],
        confidence=0.9),
    CategoryRule("music-audio-gear", "Musical Instruments > Pro Audio",
        ["audio interface", "microphone", "studio monitor", "mixer", "daq", "phantom power"],
        confidence=0.85),
]


def get_default_rules() -> list[CategoryRule]:
    """Return the built-in default category rules."""
    return DEFAULT_RULES.copy()


def find_best_match(rules: list[CategoryRule], title: str, platform: str = "", price: float | None = None) -> tuple[CategoryRule | None, float]:
    """Find the best matching rule for an item. Returns (rule, confidence)."""
    best_rule = None
    best_confidence = 0.0

    for rule in rules:
        confidence = rule.matches(title, platform, price)
        if confidence > best_confidence:
            best_confidence = confidence
            best_rule = rule

    return best_rule, best_confidence
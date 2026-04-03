// js/db.js
// Mock DB representing future Firestore structure

export const products = [
    {
        id: 1,
        name: "Valcambi Gold Bar 10 gram",
        category: "coins",
        price: 850.00,
        description: "10 gram pure gold bar from Valcambi Suisse.",
        image: "assets/images/Alpha Coin & Jewelry 02.png" // Placeholder
    },
    {
        id: 2,
        name: "Gold Canadian Maple Leaf 1 oz",
        category: "coins",
        price: 2400.00,
        description: "1 oz .9999 fine gold Canadian Maple Leaf.",
        image: "assets/images/Alpha Coin & Jewelry 03.png"
    },
    {
        id: 3,
        name: "American Gold Eagle 1/2 oz",
        category: "coins",
        price: 1250.00,
        description: "1/2 oz American Gold Eagle.",
        image: "assets/images/20260320_144235.jpg"
    },
    {
        id: 4,
        name: "Gibson 1950s Fridge",
        category: "antiques",
        price: 400.00,
        description: "Authentic Vintage Gibson 1950s refrigerator.",
        image: "assets/images/20260317_160901.jpg"
    },
    {
        id: 5,
        name: "Prairie Diamond Engagement Ring",
        category: "jewelry",
        price: 1200.00,
        description: "Exquisite 14k gold diamond ring.",
        image: "assets/images/ring.png"
    },
    {
        id: 6,
        name: "Silver Bar 100 oz",
        category: "coins",
        price: 3200.00,
        description: "100 oz .999 fine silver bar.",
        image: "assets/images/Screenshot_20260320_000432_Google.png"
    }
];

export const getProductsByCategory = (category) => {
    return products.filter(p => p.category === category);
};

export const getProductById = (id) => {
    return products.find(p => p.id === id);
};

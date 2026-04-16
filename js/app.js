// js/app.js
import { products, getProductsByCategory, getProductById, recordPurchase } from './db.js';

// Elements
const appContent = document.getElementById('app-content');
const loader = document.getElementById('loader');
const navLinks = document.querySelectorAll('.nav-link');
const mobileBtn = document.getElementById('mobile-btn');

// --- Routing & Rendering ---

const views = {
    home: () => `
        <section class="hero view-section active">
            <div class="hero-content">
                <h1>Alpha Coin & Jewelry</h1>
                <p>Invest in coins and bullion. Discover exquisite jewelry and timeless antiques. We provide the highest caliber of service.</p>
                <div class="hero-buttons">
                    <button class="btn-primary" onclick="app.navigate('shop')">Shop Collection</button>
                    <button class="btn-outline" onclick="app.navigate('coins')">Sell To Us</button>
                </div>
            </div>
        </section>
        <section class="category-grid">
            <div class="category-card" onclick="app.navigate('jewelry')">
                <img src="assets/images/scraped/Home Page/jewelryicon-768x768.png" alt="Jewelry" class="category-img" onerror="this.style.display='none';">
                <div class="category-content">
                    <h3>Jewelry & Repair</h3>
                    <p>Broken jewelry? We can fix that. Looking for the perfect piece? Explore our designs.</p>
                </div>
            </div>
            <div class="category-card" onclick="app.navigate('coins')">
                <img src="assets/images/scraped/Home Page/coin-600x600.jpg" alt="Coins" class="category-img" onerror="this.style.display='none';">
                <div class="category-content">
                    <h3>Coins & Bullion</h3>
                    <p>Looking to invest? We sell and buy gold, silver coins, and bullion at fair market value.</p>
                </div>
            </div>
            <div class="category-card" onclick="app.navigate('antiques')">
                <img src="assets/images/scraped/Antiques Page/antique-blank-camera-269810-1067x800.jpg" alt="Antiques" class="category-img" onerror="this.style.display='none';">
                <div class="category-content">
                    <h3>Antiques</h3>
                    <p>Unique finds and timeless treasures. Discover the perfect antique piece for your collection.</p>
                </div>
            </div>
        </section>
    `,
    cart: () => renderCartPage(),
    shop: () => renderProductPage('All Products', products),
    coins: () => renderProductPage('Coins & Bullion', getProductsByCategory('coins')),
    jewelry: () => renderProductPage('Fine Jewelry', getProductsByCategory('jewelry')),
    antiques: () => renderProductPage('Antiques', getProductsByCategory('antiques')),
    contact: () => `
        <div class="page-header view-section active">
            <h2>Contact Us</h2>
            <p>We'd love to hear from you. Sell us your goods or ask a question.</p>
        </div>
        <div class="container" style="max-width: 600px; margin-bottom: 60px;">
            <div class="glass-effect" style="padding: 30px; border-radius: 16px;">
                <form onsubmit="event.preventDefault(); alert('Message sent successfully!');">
                    <div class="form-group">
                        <label>Your Name</label>
                        <input type="text" required>
                    </div>
                    <div class="form-group">
                        <label>Email Address</label>
                        <input type="email" required>
                    </div>
                    <div class="form-group">
                        <label>Message / Inquiry Details</label>
                        <textarea rows="5" required></textarea>
                    </div>
                    <button type="submit" class="btn-primary full-width">Send Message</button>
                </form>
            </div>
        </div>
    `,
    about: () => `
        <div class="page-header view-section active">
            <h2>About Alpha Coin & Jewelry</h2>
        </div>
        <div class="container" style="margin-bottom: 60px; column-count: 1; max-width:800px;">
            <img src="assets/images/Higginson Jewelry & Antiques 02.png" style="width:100%; border-radius:16px; margin-bottom:20px; border:2px solid var(--gold-primary);" alt="Store">
            <h3 style="margin-bottom:15px;">Our Mission</h3>
            <p style="margin-bottom:15px;">Our mission is to sell and buy silver and gold coins and bullion. We also sell fine jewelry and antiques, and repair jewelry. Our store is founded on hard work and respect.</p>
            <p>We will buy your piece(s) at the current market value and at a fair price. We are dedicated to transparent, honest dealings and ensuring our customers are 100% satisfied.</p>
        </div>
    `,
    services: () => `
        <div class="page-header view-section active"><h2>Our Services</h2></div>
        <div class="container" style="margin-bottom:60px;">
            <div class="category-grid" style="padding:0;">
                <div class="category-card"><div class="category-content"><h3>Jewelry Repair</h3><p>Highest caliber watch battery replacement, rhodium plating, and ring sizing.</p></div></div>
                <div class="category-card"><div class="category-content"><h3>Appraisals</h3><p>Professional valuations of your coins, bullion, and antiques.</p></div></div>
                <div class="category-card"><div class="category-content"><h3>Buying</h3><p>We purchase silver, gold, platinum, and historical pieces at fair market price.</p></div></div>
        </div>
    `,
    'venmo-setup': () => `
        <section style="padding: 100px 20px; text-align:center; min-height: 70vh;">
            <div class="glass-effect" style="max-width: 600px; margin: 0 auto; padding: 40px; border-radius: 16px;">
                <h2 style="color:#008CFF; margin-bottom:20px;"><i class="fab fa-vimeo-v"></i> Venmo Setup</h2>
                <p style="margin-bottom:30px; font-size:1.1rem;">Connect your business Venmo account to automatically receive customer payments.</p>
                <form onsubmit="event.preventDefault(); alert('Venmo Profile linked successfully!'); app.navigate('cart');">
                    <div class="form-group" style="text-align:left;">
                        <label style="color:var(--text-color);">Business Venmo Username</label>
                        <input type="text" placeholder="@yourbusiness" required style="width:100%; padding:15px; margin-top:5px; border-radius:8px; border:1px solid rgba(255,255,255,0.2); background:rgba(0,0,0,0.5); color:white;">
                    </div>
                    <button type="submit" class="btn-primary" style="width:100%; padding:15px; background:#008CFF; font-size:1.1rem; border:none; margin-top:20px; cursor:pointer;">Connect Venmo Account</button>
                </form>
            </div>
        </section>
    `,
    'cashapp-setup': () => `
        <section style="padding: 100px 20px; text-align:center; min-height: 70vh;">
            <div class="glass-effect" style="max-width: 600px; margin: 0 auto; padding: 40px; border-radius: 16px;">
                <h2 style="color:#00D632; margin-bottom:20px;"><i class="fas fa-dollar-sign"></i> CashApp Setup</h2>
                <p style="margin-bottom:30px; font-size:1.1rem;">Connect your business CashApp $Cashtag to securely receive instant payouts.</p>
                <form onsubmit="event.preventDefault(); alert('CashApp connected successfully!'); app.navigate('cart');">
                    <div class="form-group" style="text-align:left;">
                        <label style="color:var(--text-color);">Business $Cashtag</label>
                        <input type="text" placeholder="$YourBusiness" required style="width:100%; padding:15px; margin-top:5px; border-radius:8px; border:1px solid rgba(255,255,255,0.2); background:rgba(0,0,0,0.5); color:white;">
                    </div>
                    <button type="submit" class="btn-primary" style="width:100%; padding:15px; background:#00D632; font-size:1.1rem; border:none; margin-top:20px; cursor:pointer;">Connect CashApp Account</button>
                </form>
            </div>
        </section>
    `
};

function renderProductPage(title, items) {
    let html = `
        <div class="page-header view-section active">
            <h2>${title}</h2>
            <p>Discover our state-of-the-art collection.</p>
        </div>
        <div class="container" style="margin-bottom: 60px;">
            <div class="product-grid">
    `;
    
    if(items.length === 0) {
        html += `<p style="grid-column: 1/-1; text-align: center; color: var(--text-muted);">No items currently in stock in this category.</p>`;
    } else {
        items.forEach(item => {
            const imageHtml = item.image ? 
                `<img src="${item.image}" alt="${item.name}" class="product-img" onerror="this.src=''; this.style.background='#333'">` : 
                `<div class="dropzone">Click or Drop Image Here</div>`;
                
            html += `
                <div class="product-card">
                    ${imageHtml}
                    <div class="product-info">
                        <h3 class="product-title">${item.name}</h3>
                        <p style="font-size:0.9rem; color:var(--text-muted); margin-bottom:15px;">${item.description}</p>
                        <div class="product-price">$${item.price.toFixed(2)}</div>
                        <button class="btn-outline full-width" onclick="app.addToCart(${item.id})">Add to Cart</button>
                    </div>
                </div>
            `;
        });
    }

    html += `</div></div>`;
    return html;
}

function renderCartPage() {
    let html = `
        <div class="page-header view-section active">
            <h2>Your Shopping Cart</h2>
            <p>Review your items and proceed securely to checkout.</p>
        </div>
        <div class="container" style="margin-bottom: 60px; max-width: 900px;">
    `;
    
    if (app.cartItems.length === 0) {
        html += `<div class="glass-effect" style="padding:40px; text-align:center; border-radius:16px;">
                    <h3>Your cart is empty.</h3>
                    <button class="btn-primary" style="margin-top:20px;" onclick="app.navigate('shop')">Continue Shopping</button>
                 </div></div>`;
        return html;
    }

    let subtotal = 0;
    let listItemsHtml = `<div class="cart-items" style="margin-bottom:30px;">`;
    app.cartItems.forEach((item, index) => {
        subtotal += item.price;
        listItemsHtml += `
            <div class="cart-item glass-effect" style="display:flex; align-items:center; padding:15px; border-radius:12px; margin-bottom:15px;">
                <img src="${item.image}" alt="${item.name}" style="width:80px; height:80px; object-fit:cover; border-radius:8px; margin-right:20px;" onerror="this.style.display='none';">
                <div style="flex-grow:1;">
                    <h4 style="margin-bottom:5px; font-family:var(--font-sans); color:white;">${item.name}</h4>
                    <span style="color:var(--gold-primary); font-weight:bold; font-size:1.1rem;">$${item.price.toFixed(2)}</span>
                </div>
                <button class="icon-btn" onclick="app.removeFromCart(${index})" style="color:#ff4c4c; font-size:1.2rem; cursor:pointer;"><i class="fas fa-trash"></i></button>
            </div>
        `;
    });
    listItemsHtml += `</div>`;

    // Hypothetical shipping substitution requested by client
    const total = subtotal;

    let summaryHtml = `
        <div class="glass-effect" style="padding:30px; border-radius:16px; margin-bottom:30px;">
            <h3 style="margin-bottom:15px;">Order Summary</h3>
            <hr style="border:0; border-top:1px solid rgba(255,255,255,0.1); margin:15px 0;">
            <div style="display:flex; justify-content:space-between; margin-bottom:10px;"><span>Subtotal</span> <span>$${subtotal.toFixed(2)}</span></div>
            <div style="text-align:center; font-weight:bold; color:red; margin-bottom:10px; width:100%;">Estimated Shipping To Address: In Progress</div>
            <div style="text-align:center; font-weight:bold; color:red; margin-bottom:10px; width:100%;">Estimated Income Tax (7.5%): In Progress</div>
            <hr style="border:0; border-top:1px solid rgba(255,255,255,0.1); margin:15px 0;">
            <div style="display:flex; justify-content:space-between; margin-bottom:20px; font-size:1.4rem; font-weight:bold; color:var(--gold-primary);"><span>Total Include Tax</span> <span>$${total.toFixed(2)}</span></div>
            
            <h4 style="margin-bottom:15px;">Select Payment Method to Checkout</h4>
            <div style="display:flex; gap:10px; width: 100%;">
                <button class="btn-primary" style="flex:1; padding:10px 5px; font-size:0.85rem; background:#333333; color:white; border:1px solid rgba(255,255,255,0.2);" onclick="app.checkout('Credit/Debit Card')"><i class="fas fa-credit-card"></i> Credit/Debit Card</button>
                <button class="btn-primary" style="flex:1; padding:10px 5px; font-size:0.85rem; background:#008CFF; color:white; border:none;" onclick="app.navigate('venmo-setup')"><i class="fab fa-vimeo-v"></i> Venmo</button>
                <button class="btn-primary" style="flex:1; padding:10px 5px; font-size:0.85rem; background:#00D632; color:white; border:none;" onclick="app.navigate('cashapp-setup')"><i class="fas fa-dollar-sign"></i> CashApp</button>
                <button class="btn-primary" style="flex:1; padding:10px 5px; font-size:0.85rem; background:#003087; color:white; border:none;" onclick="app.checkout('PayPal')"><i class="fab fa-paypal"></i> PayPal</button>
                <button class="btn-primary" style="flex:1; padding:10px 5px; font-size:0.85rem; background:#7417ea; color:white; border:none;" onclick="app.checkout('Zelle')">Zelle</button>
                <button class="btn-primary" style="flex:1; padding:10px 5px; font-size:0.85rem; background:#F7931A; color:white; border:none;" onclick="app.checkout('Cryptocurrency')"><i class="fab fa-bitcoin"></i> Cryptocurrency</button>
            </div>
        </div>
    `;

    html += listItemsHtml + summaryHtml + `</div>`;
    return html;
}

// App Logic
const app = {
    cartItems: [],
    init() {
        // Remove loader
        setTimeout(() => loader.classList.add('hidden'), 800);
        
        // Cart listener
        document.getElementById('cart-btn').addEventListener('click', () => {
            this.navigate('cart');
        });
        
        // Setup Nav Listeners
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = e.currentTarget.getAttribute('data-target');
                this.navigate(target);
                
                // Update active class
                navLinks.forEach(l => l.classList.remove('active'));
                const sameTargetLinks = document.querySelectorAll(`[data-target="${target}"]`);
                sameTargetLinks.forEach(l => l.classList.add('active'));
            });
        });

        // Initialize view based on hash or default to home
        const initialView = window.location.hash.replace('#', '') || 'home';
        this.navigate(initialView);
    },

    navigate(viewName) {
        if (views[viewName]) {
            appContent.innerHTML = views[viewName]();
            window.scrollTo(0, 0);
            window.location.hash = viewName;
            this.setupDropzones();
        }
    },

    setupDropzones() {
        const dropzones = document.querySelectorAll('.dropzone');
        dropzones.forEach(zone => {
            zone.addEventListener('dragover', (e) => {
                e.preventDefault();
                zone.classList.add('drag-over');
            });
            zone.addEventListener('dragleave', () => {
                zone.classList.remove('drag-over');
            });
            zone.addEventListener('drop', (e) => {
                e.preventDefault();
                e.stopPropagation();
                zone.classList.remove('drag-over');
                
                // Allow user to upload dropping file
                if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                    const file = e.dataTransfer.files[0];
                    if (file.type.startsWith('image/')) {
                        const reader = new FileReader();
                        reader.onload = (event) => {
                            zone.style.backgroundImage = "url('" + event.target.result + "')";
                            zone.style.backgroundSize = 'cover';
                            zone.style.backgroundPosition = 'center';
                            zone.innerText = '';
                        };
                        reader.readAsDataURL(file);
                    }
                }
            });
            zone.addEventListener('click', (e) => {
                // Prevent routing if we click the dropzone for the demo
                e.stopPropagation();
                // Create a hidden input to trigger file selection
                const input = document.createElement('input');
                input.type = 'file';
                input.accept = 'image/*';
                input.onchange = (event) => {
                    const file = event.target.files[0];
                    if (file) {
                        const reader = new FileReader();
                        reader.onload = (ev) => {
                            zone.style.backgroundImage = "url('" + ev.target.result + "')";
                            zone.style.backgroundSize = 'cover';
                            zone.style.backgroundPosition = 'center';
                            zone.innerText = '';
                        };
                        reader.readAsDataURL(file);
                    }
                };
                input.click();
            });
        });
    },

    addToCart(productId) {
        const item = getProductById(productId);
        if(item) {
            this.cartItems.push(item);
            this.updateCartBadge();
            if(window.syncCart) window.syncCart();
        }
    },

    removeFromCart(index) {
        this.cartItems.splice(index, 1);
        this.updateCartBadge();
        this.navigate('cart'); // re-render view
        if(window.syncCart) window.syncCart();
    },

    updateCartBadge() {
        const badge = document.getElementById('cart-badge');
        if(badge) {
            badge.innerText = this.cartItems.length;
            badge.style.transform = 'scale(1.5)';
            setTimeout(() => badge.style.transform = 'scale(1)', 200);
        }
    },

    async checkout(paymentMethod) {
        // Disabled during demo phase per user request until business bank accounts are linked
        console.log(`Selected payment method: ${paymentMethod}. Checkout disabled in demo phase.`);
        // To prevent user confusion if they click it repeatedly expecting something
        // alert("Checkout is temporarily disabled while we connect our banking systems. Check back soon!");
    }
};

// Make app globally accessible for onClick events in HTML strings
window.app = app;

document.addEventListener('DOMContentLoaded', () => {
    app.init();
});

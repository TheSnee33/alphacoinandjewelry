// js/app.js
import { products, getProductsByCategory } from './db.js';

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
                <div class="dropzone">Click or Drop Image Here</div>
                <div class="category-content">
                    <h3>Jewelry & Repair</h3>
                    <p>Broken jewelry? We can fix that. Looking for the perfect piece? Explore our designs.</p>
                </div>
            </div>
            <div class="category-card" onclick="app.navigate('coins')">
                <div class="dropzone">Click or Drop Image Here</div>
                <div class="category-content">
                    <h3>Coins & Bullion</h3>
                    <p>Looking to invest? We sell and buy gold, silver coins, and bullion at fair market value.</p>
                </div>
            </div>
            <div class="category-card" onclick="app.navigate('antiques')">
                <div class="dropzone">Click or Drop Image Here</div>
                <div class="category-content">
                    <h3>Antiques</h3>
                    <p>Unique finds and timeless treasures. Discover the perfect antique piece for your collection.</p>
                </div>
            </div>
        </section>
    `,
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
        </div>
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

// App Logic
const app = {
    cart: 0,
    init() {
        // Remove loader
        setTimeout(() => loader.classList.add('hidden'), 800);
        
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
        this.cart++;
        document.getElementById('cart-badge').innerText = this.cart;
        // Simple animation
        const badge = document.getElementById('cart-badge');
        badge.style.transform = 'scale(1.5)';
        setTimeout(() => badge.style.transform = 'scale(1)', 200);
    }
};

// Make app globally accessible for onClick events in HTML strings
window.app = app;

document.addEventListener('DOMContentLoaded', () => {
    app.init();
});

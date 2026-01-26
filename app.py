from flask import Flask, render_template_string, request, jsonify, session
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Sample products
products = [
    {
        "id": 1,
        "name": "Wireless Headphones",
        "price": 99.99,
        "image": "https://picsum.photos/300/200?random=1",
        "category": "Electronics",
        "description": "High-quality wireless headphones with noise cancellation",
        "rating": 4.5,
        "reviews": [],
        "inStock": True,
        "features": ["Noise Cancellation", "30hr Battery", "Wireless"]
    },
    {
        "id": 2,
        "name": "Smart Watch",
        "price": 199.99,
        "image": "https://picsum.photos/300/200?random=2",
        "category": "Electronics",
        "description": "Feature-rich smartwatch with health monitoring",
        "rating": 4.2,
        "reviews": [],
        "inStock": True,
        "features": ["Heart Rate Monitor", "GPS", "Water Resistant"]
    },
    {
        "id": 3,
        "name": "Running Shoes",
        "price": 79.99,
        "image": "https://picsum.photos/300/200?random=3",
        "category": "Fashion",
        "description": "Comfortable running shoes for all terrains",
        "rating": 4.7,
        "reviews": [],
        "inStock": False,
        "features": ["Lightweight", "Breathable", "Durable"]
    },
    {
        "id": 4,
        "name": "Coffee Maker",
        "price": 49.99,
        "image": "https://picsum.photos/300/200?random=4",
        "category": "Home",
        "description": "Automatic coffee maker with timer",
        "rating": 4.3,
        "reviews": [],
        "inStock": True,
        "features": ["24hr Timer", "Auto Shut-off", "Programmable"]
    },
    {
        "id": 5,
        "name": "Backpack",
        "price": 39.99,
        "image": "https://picsum.photos/300/200?random=5",
        "category": "Fashion",
        "description": "Waterproof backpack with laptop compartment",
        "rating": 4.6,
        "reviews": [],
        "inStock": True,
        "features": ["Waterproof", "Laptop Sleeve", "Multiple Pockets"]
    },
    {
        "id": 6,
        "name": "Desk Lamp",
        "price": 29.99,
        "image": "https://picsum.photos/300/200?random=6",
        "category": "Home",
        "description": "LED desk lamp with adjustable brightness",
        "rating": 4.4,
        "reviews": [],
        "inStock": True,
        "features": ["Adjustable Brightness", "USB Port", "Modern Design"]
    }
]

product_reviews = {}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShopEasy - Online Store</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        .product-card:hover {
            transform: translateY(-5px);
            transition: all 0.3s ease;
        }
        .cart-badge, .wishlist-badge {
            position: absolute;
            top: -8px;
            right: -8px;
            background: #ef4444;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            font-size: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .wishlist-badge {
            background: #10b981;
            left: -8px;
            right: auto;
        }
        .search-box:focus {
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        .review-star:hover {
            transform: scale(1.2);
            transition: transform 0.2s;
        }
        .wishlist-btn:hover {
            transform: scale(1.1);
            transition: transform 0.2s;
        }
        .discount-badge {
            position: absolute;
            top: 10px;
            left: 10px;
            background: #ef4444;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }
    </style>
</head>
<body class="bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-lg sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4">
            <div class="flex justify-between items-center py-4">
                <div class="flex items-center">
                    <i class="fas fa-shopping-bag text-blue-600 text-2xl mr-2"></i>
                    <span class="text-xl font-bold text-gray-800">ShopEasy</span>
                </div>
                
                <!-- Search Bar -->
                <div class="flex-1 max-w-2xl mx-4">
                    <div class="relative">
                        <input type="text" 
                               id="searchInput"
                               placeholder="Search products..." 
                               class="w-full px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:border-blue-500 search-box">
                        <i class="fas fa-search absolute right-3 top-3 text-gray-400"></i>
                    </div>
                </div>

                <!-- Cart & Wishlist Icons -->
                <div class="flex space-x-4">
                    <!-- Wishlist Icon -->
                    <div class="relative">
                        <button onclick="toggleWishlist()" class="p-2 text-gray-600 hover:text-red-500 relative">
                            <i class="fas fa-heart text-xl"></i>
                            <span id="wishlistCount" class="wishlist-badge">0</span>
                        </button>
                    </div>
                    
                    <!-- Cart Icon -->
                    <div class="relative">
                        <button onclick="toggleCart()" class="p-2 text-gray-600 hover:text-blue-600 relative">
                            <i class="fas fa-shopping-cart text-xl"></i>
                            <span id="cartCount" class="cart-badge">0</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-16">
        <div class="max-w-7xl mx-auto px-4 text-center">
            <h1 class="text-4xl md:text-6xl font-bold mb-4">Welcome to ShopEasy</h1>
            <p class="text-xl mb-8">Discover amazing products at great prices</p>
            <div class="flex justify-center space-x-4">
                <button onclick="scrollToProducts()" class="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition duration-300">
                    Start Shopping
                </button>
                <button onclick="scrollToNewFeature()" class="bg-green-500 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-600 transition duration-300">
                    <i class="fas fa-star mr-2"></i>New: Enhanced Cart & Wishlist
                </button>
            </div>
        </div>
    </section>

    <!-- NEW FEATURE: Enhanced Shopping Features -->
    <section id="newFeatures" class="max-w-7xl mx-auto px-4 py-12">
        <div class="text-center mb-12">
            <h2 class="text-3xl font-bold text-gray-800 mb-4">
                <i class="fas fa-shopping-cart text-blue-500 mr-2"></i>
                Enhanced Shopping Experience
            </h2>
            <p class="text-gray-600 text-lg">New features to make your shopping better!</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            <!-- Feature 1: Wishlist -->
            <div class="bg-white p-6 rounded-lg shadow-md border border-green-200">
                <div class="text-center mb-4">
                    <i class="fas fa-heart text-red-500 text-4xl mb-3"></i>
                    <h3 class="text-xl font-semibold text-gray-800">Save for Later</h3>
                </div>
                <p class="text-gray-600 text-center">Add items to your wishlist and come back to them later. Never forget what you wanted!</p>
            </div>

            <!-- Feature 2: Stock Status -->
            <div class="bg-white p-6 rounded-lg shadow-md border border-blue-200">
                <div class="text-center mb-4">
                    <i class="fas fa-box text-blue-500 text-4xl mb-3"></i>
                    <h3 class="text-xl font-semibold text-gray-800">Real-time Stock</h3>
                </div>
                <p class="text-gray-600 text-center">See which items are in stock and which are out of stock before adding to cart.</p>
            </div>

            <!-- Feature 3: Product Features -->
            <div class="bg-white p-6 rounded-lg shadow-md border border-purple-200">
                <div class="text-center mb-4">
                    <i class="fas fa-list-check text-purple-500 text-4xl mb-3"></i>
                    <h3 class="text-xl font-semibold text-gray-800">Detailed Features</h3>
                </div>
                <p class="text-gray-600 text-center">View all product features and specifications before making a decision.</p>
            </div>
        </div>
    </section>

    <!-- Products Section -->
    <section id="products" class="max-w-7xl mx-auto px-4 py-12">
        <h2 class="text-3xl font-bold text-gray-800 mb-8 text-center">Featured Products</h2>
        
        <!-- Category Filters -->
        <div class="flex flex-wrap justify-center gap-2 mb-8">
            <button onclick="filterProducts('all')" class="px-4 py-2 bg-blue-600 text-white rounded-lg">All</button>
            <button onclick="filterProducts('Electronics')" class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300">Electronics</button>
            <button onclick="filterProducts('Fashion')" class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300">Fashion</button>
            <button onclick="filterProducts('Home')" class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300">Home</button>
            <button onclick="showWishlistItems()" class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600">
                <i class="fas fa-heart mr-2"></i>Wishlist
            </button>
        </div>

        <!-- Products Grid -->
        <div id="productsGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {% for product in products %}
            <div class="bg-white rounded-lg shadow-md product-card border border-gray-200 relative" data-category="{{ product.category }}">
                <!-- Stock Status Badge -->
                {% if not product.inStock %}
                <div class="discount-badge bg-gray-500">Out of Stock</div>
                {% endif %}
                
                <!-- Wishlist Button -->
                <button onclick="toggleWishlistItem({{ product.id }})" 
                        class="absolute top-2 right-2 p-2 rounded-full bg-white shadow-md wishlist-btn">
                    <i id="wishlistIcon-{{ product.id }}" class="far fa-heart text-gray-400 hover:text-red-500"></i>
                </button>

                <img src="{{ product.image }}" alt="{{ product.name }}" class="w-full h-48 object-cover rounded-t-lg">
                <div class="p-4">
                    <div class="flex justify-between items-start mb-2">
                        <h3 class="text-lg font-semibold text-gray-800">{{ product.name }}</h3>
                        <span class="text-green-600 font-bold">${{ product.price }}</span>
                    </div>
                    <p class="text-gray-600 text-sm mb-3">{{ product.description }}</p>
                    
                    <!-- Product Features -->
                    <div class="mb-3">
                        <div class="flex flex-wrap gap-1">
                            {% for feature in product.features %}
                            <span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">{{ feature }}</span>
                            {% endfor %}
                        </div>
                    </div>
                    
                    <div class="flex justify-between items-center">
                        <div class="flex items-center">
                            {% for i in range(5) %}
                                {% if i < product.rating|int %}
                                    <i class="fas fa-star text-yellow-400"></i>
                                {% else %}
                                    <i class="far fa-star text-yellow-400"></i>
                                {% endif %}
                            {% endfor %}
                            <span class="text-sm text-gray-500 ml-1">{{ product.rating }}</span>
                        </div>
                        <button onclick="addToCart({{ product.id }})" 
                                class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition duration-300 {% if not product.inStock %}opacity-50 cursor-not-allowed{% endif %}"
                                {% if not product.inStock %}disabled{% endif %}>
                            <i class="fas fa-cart-plus mr-2"></i>
                            {% if product.inStock %}Add to Cart{% else %}Out of Stock{% endif %}
                        </button>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </section>

    <!-- Shopping Cart Sidebar -->
    <div id="cartSidebar" class="fixed top-0 right-0 h-full w-96 bg-white shadow-2xl transform translate-x-full transition-transform duration-300 z-50">
        <div class="p-4 border-b border-gray-200 flex justify-between items-center">
            <h3 class="text-lg font-semibold">Your Shopping Cart</h3>
            <button onclick="toggleCart()" class="text-gray-500 hover:text-gray-700">
                <i class="fas fa-times text-xl"></i>
            </button>
        </div>
        <div id="cartItems" class="p-4 h-3/4 overflow-y-auto">
            <div id="emptyCart" class="text-center text-gray-500 py-8">
                <i class="fas fa-shopping-cart text-4xl mb-4 text-gray-300"></i>
                <p>Your cart is empty</p>
            </div>
        </div>
        <div class="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 bg-white">
            <div class="flex justify-between items-center mb-2">
                <span class="font-semibold">Subtotal:</span>
                <span id="cartSubtotal" class="font-bold">$0.00</span>
            </div>
            <div class="flex justify-between items-center mb-4">
                <span class="font-semibold">Total:</span>
                <span id="cartTotal" class="font-bold text-lg text-green-600">$0.00</span>
            </div>
            <button onclick="checkout()" class="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition duration-300">
                <i class="fas fa-credit-card mr-2"></i>Proceed to Checkout
            </button>
        </div>
    </div>

    <!-- Wishlist Sidebar -->
    <div id="wishlistSidebar" class="fixed top-0 right-0 h-full w-96 bg-white shadow-2xl transform translate-x-full transition-transform duration-300 z-50">
        <div class="p-4 border-b border-gray-200 flex justify-between items-center">
            <h3 class="text-lg font-semibold">Your Wishlist</h3>
            <button onclick="toggleWishlist()" class="text-gray-500 hover:text-gray-700">
                <i class="fas fa-times text-xl"></i>
            </button>
        </div>
        <div id="wishlistItems" class="p-4 h-3/4 overflow-y-auto">
            <div id="emptyWishlist" class="text-center text-gray-500 py-8">
                <i class="fas fa-heart text-4xl mb-4 text-gray-300"></i>
                <p>Your wishlist is empty</p>
                <p class="text-sm mt-2">Add items you love by clicking the heart icon</p>
            </div>
        </div>
        <div class="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 bg-white">
            <button onclick="addAllToCart()" class="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition duration-300 mb-2">
                <i class="fas fa-cart-plus mr-2"></i>Add All to Cart
            </button>
            <button onclick="clearWishlist()" class="w-full bg-gray-200 text-gray-700 py-2 rounded-lg font-semibold hover:bg-gray-300 transition duration-300">
                Clear Wishlist
            </button>
        </div>
    </div>

    <!-- Overlays -->
    <div id="cartOverlay" class="fixed inset-0 bg-black bg-opacity-50 hidden z-40" onclick="toggleCart()"></div>
    <div id="wishlistOverlay" class="fixed inset-0 bg-black bg-opacity-50 hidden z-40" onclick="toggleWishlist()"></div>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-8 mt-12">
        <div class="max-w-7xl mx-auto px-4 text-center">
            <p>&copy; 2024 ShopEasy. All rights reserved. | Built with ❤️ using Flask</p>
            <div class="mt-4 space-x-4">
                <a href="#" class="text-gray-400 hover:text-white"><i class="fab fa-facebook"></i></a>
                <a href="#" class="text-gray-400 hover:text-white"><i class="fab fa-twitter"></i></a>
                <a href="#" class="text-gray-400 hover:text-white"><i class="fab fa-instagram"></i></a>
            </div>
        </div>
    </footer>

    <script>
        let cart = [];
        let wishlist = [];
        let currentRatings = {};
        
        // Load cart and wishlist from session
        function loadData() {
            fetch('/get_cart')
                .then(response => response.json())
                .then(data => {
                    cart = data;
                    updateCartUI();
                });
            
            fetch('/get_wishlist')
                .then(response => response.json())
                .then(data => {
                    wishlist = data;
                    updateWishlistUI();
                    updateWishlistIcons();
                });
        }

        // Wishlist functions
        function toggleWishlistItem(productId) {
            fetch('/toggle_wishlist', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({product_id: productId})
            })
            .then(response => response.json())
            .then(data => {
                wishlist = data.wishlist;
                updateWishlistUI();
                updateWishlistIcons();
                showNotification(data.message, data.success ? 'success' : 'error');
            });
        }

        function updateWishlistIcons() {
            wishlist.forEach(item => {
                const icon = document.getElementById(`wishlistIcon-${item.id}`);
                if (icon) {
                    icon.classList.remove('far', 'text-gray-400');
                    icon.classList.add('fas', 'text-red-500');
                }
            });
            
            // Reset icons for items not in wishlist
            {% for product in products %}
                if (!wishlist.find(item => item.id === {{ product.id }})) {
                    const icon = document.getElementById(`wishlistIcon-{{ product.id }}`);
                    if (icon) {
                        icon.classList.remove('fas', 'text-red-500');
                        icon.classList.add('far', 'text-gray-400');
                    }
                }
            {% endfor %}
        }

        function updateWishlistUI() {
            const wishlistCount = document.getElementById('wishlistCount');
            const wishlistItems = document.getElementById('wishlistItems');
            const emptyWishlist = document.getElementById('emptyWishlist');

            wishlistCount.textContent = wishlist.length;

            if (wishlist.length === 0) {
                emptyWishlist.style.display = 'block';
                wishlistItems.innerHTML = '<div id="emptyWishlist" class="text-center text-gray-500 py-8"><i class="fas fa-heart text-4xl mb-4 text-gray-300"></i><p>Your wishlist is empty</p><p class="text-sm mt-2">Add items you love by clicking the heart icon</p></div>';
            } else {
                emptyWishlist.style.display = 'none';
                wishlistItems.innerHTML = wishlist.map(item => `
                    <div class="flex items-center border-b border-gray-200 py-4">
                        <img src="${item.image}" alt="${item.name}" class="w-16 h-16 object-cover rounded">
                        <div class="flex-1 ml-4">
                            <h4 class="font-semibold">${item.name}</h4>
                            <p class="text-green-600 font-bold">$${item.price}</p>
                            <div class="flex space-x-2 mt-2">
                                <button onclick="addToCart(${item.id})" 
                                        class="flex-1 bg-blue-600 text-white py-1 px-3 rounded text-sm hover:bg-blue-700">
                                    Add to Cart
                                </button>
                                <button onclick="toggleWishlistItem(${item.id})" 
                                        class="bg-red-500 text-white py-1 px-3 rounded text-sm hover:bg-red-600">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                `).join('');
            }
        }

        function addAllToCart() {
            wishlist.forEach(item => {
                if (item.inStock) {
                    addToCart(item.id);
                }
            });
            showNotification('Available items added to cart!', 'success');
        }

        function clearWishlist() {
            fetch('/clear_wishlist', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                wishlist = [];
                updateWishlistUI();
                updateWishlistIcons();
                showNotification('Wishlist cleared!', 'success');
            });
        }

        function showWishlistItems() {
            const products = document.querySelectorAll('.product-card');
            products.forEach(product => {
                const productId = parseInt(product.querySelector('button').onclick.toString().match(/\d+/)[0]);
                const inWishlist = wishlist.find(item => item.id === productId);
                if (inWishlist) {
                    product.style.display = 'block';
                } else {
                    product.style.display = 'none';
                }
            });
        }

        // Toggle wishlist sidebar
        function toggleWishlist() {
            const sidebar = document.getElementById('wishlistSidebar');
            const overlay = document.getElementById('wishlistOverlay');
            sidebar.classList.toggle('translate-x-full');
            overlay.classList.toggle('hidden');
        }

        // Existing cart functions (keep them as they are)
        function addToCart(productId) {
            fetch('/add_to_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({product_id: productId})
            })
            .then(response => response.json())
            .then(data => {
                cart = data.cart;
                updateCartUI();
                showNotification('Product added to cart!', 'success');
            });
        }

        function removeFromCart(productId) {
            fetch('/remove_from_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({product_id: productId})
            })
            .then(response => response.json())
            .then(data => {
                cart = data.cart;
                updateCartUI();
            });
        }

        function updateCartUI() {
            const cartCount = document.getElementById('cartCount');
            const cartItems = document.getElementById('cartItems');
            const cartTotal = document.getElementById('cartTotal');
            const cartSubtotal = document.getElementById('cartSubtotal');
            const emptyCart = document.getElementById('emptyCart');

            cartCount.textContent = cart.reduce((total, item) => total + item.quantity, 0);

            if (cart.length === 0) {
                emptyCart.style.display = 'block';
                cartItems.innerHTML = '<div id="emptyCart" class="text-center text-gray-500 py-8"><i class="fas fa-shopping-cart text-4xl mb-4 text-gray-300"></i><p>Your cart is empty</p></div>';
            } else {
                emptyCart.style.display = 'none';
                let subtotal = 0;
                cartItems.innerHTML = cart.map(item => {
                    subtotal += item.price * item.quantity;
                    return `
                        <div class="flex items-center border-b border-gray-200 py-4">
                            <img src="${item.image}" alt="${item.name}" class="w-16 h-16 object-cover rounded">
                            <div class="flex-1 ml-4">
                                <h4 class="font-semibold">${item.name}</h4>
                                <p class="text-green-600 font-bold">$${item.price}</p>
                                <div class="flex items-center mt-2">
                                    <button onclick="updateQuantity(${item.id}, ${item.quantity - 1})" class="px-2 py-1 bg-gray-200 rounded-l">-</button>
                                    <span class="px-3 py-1 bg-gray-100">${item.quantity}</span>
                                    <button onclick="updateQuantity(${item.id}, ${item.quantity + 1})" class="px-2 py-1 bg-gray-200 rounded-r">+</button>
                                    <button onclick="removeFromCart(${item.id})" class="ml-4 text-red-500 hover:text-red-700">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    `;
                }).join('');
                cartSubtotal.textContent = `$${subtotal.toFixed(2)}`;
                cartTotal.textContent = `$${subtotal.toFixed(2)}`;
            }
        }

        function updateQuantity(productId, newQuantity) {
            if (newQuantity < 1) {
                removeFromCart(productId);
                return;
            }
            
            fetch('/update_quantity', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({product_id: productId, quantity: newQuantity})
            })
            .then(response => response.json())
            .then(data => {
                cart = data.cart;
                updateCartUI();
            });
        }

        function toggleCart() {
            const sidebar = document.getElementById('cartSidebar');
            const overlay = document.getElementById('cartOverlay');
            sidebar.classList.toggle('translate-x-full');
            overlay.classList.toggle('hidden');
        }

        function filterProducts(category) {
            const products = document.querySelectorAll('.product-card');
            products.forEach(product => {
                if (category === 'all' || product.dataset.category === category) {
                    product.style.display = 'block';
                } else {
                    product.style.display = 'none';
                }
            });
        }

        document.getElementById('searchInput').addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const products = document.querySelectorAll('.product-card');
            
            products.forEach(product => {
                const name = product.querySelector('h3').textContent.toLowerCase();
                const description = product.querySelector('p').textContent.toLowerCase();
                
                if (name.includes(searchTerm) || description.includes(searchTerm)) {
                    product.style.display = 'block';
                } else {
                    product.style.display = 'none';
                }
            });
        });

        function scrollToProducts() {
            document.getElementById('products').scrollIntoView({ behavior: 'smooth' });
        }

        function scrollToNewFeature() {
            document.getElementById('newFeatures').scrollIntoView({ behavior: 'smooth' });
        }

        function showNotification(message, type) {
            const notification = document.createElement('div');
            notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
                type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
            }`;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.remove();
            }, 3000);
        }

        function checkout() {
            if (cart.length === 0) {
                showNotification('Your cart is empty!', 'error');
                return;
            }
            
            fetch('/checkout', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Order placed successfully!', 'success');
                    cart = [];
                    updateCartUI();
                    toggleCart();
                }
            });
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadData();
        });
    </script>
</body>
</html>
"""

# Existing routes (cart, reviews) remain the same...

# NEW FEATURE: Wishlist routes
@app.route("/toggle_wishlist", methods=["POST"])
def toggle_wishlist():
    if 'wishlist' not in session:
        session['wishlist'] = []
    
    data = request.get_json()
    product_id = data.get('product_id')
    
    product = next((p for p in products if p['id'] == product_id), None)
    
    if product:
        wishlist = session['wishlist']
        wishlist_item = next((item for item in wishlist if item['id'] == product_id), None)
        
        if wishlist_item:
            # Remove from wishlist
            session['wishlist'] = [item for item in wishlist if item['id'] != product_id]
            return jsonify({'success': True, 'wishlist': session['wishlist'], 'message': 'Removed from wishlist'})
        else:
            # Add to wishlist
            wishlist.append({
                'id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'image': product['image'],
                'inStock': product['inStock']
            })
            session['wishlist'] = wishlist
            return jsonify({'success': True, 'wishlist': session['wishlist'], 'message': 'Added to wishlist'})
    
    return jsonify({'success': False, 'message': 'Product not found'})

@app.route("/get_wishlist")
def get_wishlist():
    return jsonify(session.get('wishlist', []))

@app.route("/clear_wishlist", methods=["POST"])
def clear_wishlist():
    session['wishlist'] = []
    return jsonify({'success': True, 'wishlist': []})

# Keep all other existing routes (cart, reviews, etc.)
@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE, products=products)

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    if 'cart' not in session:
        session['cart'] = []
    
    data = request.get_json()
    product_id = data.get('product_id')
    
    product = next((p for p in products if p['id'] == product_id), None)
    
    if product:
        cart = session['cart']
        cart_item = next((item for item in cart if item['id'] == product_id), None)
        
        if cart_item:
            cart_item['quantity'] += 1
        else:
            cart.append({
                'id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'image': product['image'],
                'quantity': 1
            })
        
        session['cart'] = cart
        return jsonify({'success': True, 'cart': cart})
    
    return jsonify({'success': False})

@app.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    
    if 'cart' in session:
        cart = session['cart']
        session['cart'] = [item for item in cart if item['id'] != product_id]
        return jsonify({'success': True, 'cart': session['cart']})
    
    return jsonify({'success': False})

@app.route("/update_quantity", methods=["POST"])
def update_quantity():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    
    if 'cart' in session:
        cart = session['cart']
        cart_item = next((item for item in cart if item['id'] == product_id), None)
        
        if cart_item:
            if quantity <= 0:
                session['cart'] = [item for item in cart if item['id'] != product_id]
            else:
                cart_item['quantity'] = quantity
            
            return jsonify({'success': True, 'cart': session['cart']})
    
    return jsonify({'success': False})

@app.route("/get_cart")
def get_cart():
    return jsonify(session.get('cart', []))

@app.route("/checkout", methods=["POST"])
def checkout():
    if 'cart' in session:
        session['cart'] = []
        return jsonify({'success': True, 'message': 'Order placed successfully!'})
    
    return jsonify({'success': False, 'message': 'Cart is empty!'})

# Review routes (from FeatureA)
@app.route("/add_review", methods=["POST"])
def add_review():
    data = request.get_json()
    product_id = data.get('product_id')
    rating = data.get('rating')
    text = data.get('text')
    author = data.get('author', 'Anonymous')
    
    if product_id not in product_reviews:
        product_reviews[product_id] = []
    
    product_reviews[product_id].append({
        'rating': rating,
        'text': text,
        'author': author,
        'timestamp': datetime.now().isoformat()
    })
    
    return jsonify({'success': True})

@app.route("/get_reviews")
def get_reviews():
    product_id = request.args.get('product_id', type=int)
    reviews = product_reviews.get(product_id, [])
    return jsonify(reviews)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
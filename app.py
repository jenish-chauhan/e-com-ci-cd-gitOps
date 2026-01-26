from flask import Flask, render_template_string, request, jsonify, session
import json
import os
import uuid
from datetime import datetime
from collections import defaultdict

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

# In-memory storage (use database in production)
product_reviews = {}
orders = {}
user_profiles = {}

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
        .cart-badge, .wishlist-badge, .orders-badge {
            position: absolute;
            top: -8px;
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
        .orders-badge {
            background: #8b5cf6;
            right: -8px;
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
        .order-progress {
            height: 8px;
            border-radius: 4px;
            background: #e5e7eb;
            overflow: hidden;
        }
        .order-progress-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s ease;
        }
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        .user-menu {
            transition: all 0.3s ease;
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

                <!-- User Menu -->
                <div class="flex space-x-4">
                    <!-- Orders Icon -->
                    <div class="relative">
                        <button onclick="toggleOrders()" class="p-2 text-gray-600 hover:text-purple-600 relative">
                            <i class="fas fa-clipboard-list text-xl"></i>
                            <span id="ordersCount" class="orders-badge">0</span>
                        </button>
                    </div>
                    
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

                    <!-- User Profile -->
                    <div class="relative">
                        <button onclick="toggleUserMenu()" class="p-2 text-gray-600 hover:text-green-600">
                            <i class="fas fa-user-circle text-xl"></i>
                        </button>
                        <div id="userMenu" class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 hidden z-50 user-menu">
                            <div class="p-4 border-b border-gray-200">
                                <p class="font-semibold" id="userName">Guest User</p>
                                <p class="text-sm text-gray-500" id="userEmail">Not logged in</p>
                            </div>
                            <div class="p-2">
                                <button onclick="showLoginModal()" class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded">
                                    <i class="fas fa-sign-in-alt mr-2"></i>Login / Register
                                </button>
                                <button onclick="showOrderHistory()" class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded">
                                    <i class="fas fa-history mr-2"></i>Order History
                                </button>
                                <button onclick="logout()" class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100 rounded">
                                    <i class="fas fa-sign-out-alt mr-2"></i>Logout
                                </button>
                            </div>
                        </div>
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
            <div class="flex justify-center space-x-4 flex-wrap gap-4">
                <button onclick="scrollToProducts()" class="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition duration-300">
                    Start Shopping
                </button>
                <button onclick="scrollToNewFeature()" class="bg-green-500 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-600 transition duration-300">
                    <i class="fas fa-shipping-fast mr-2"></i>New: Order Tracking
                </button>
                <button onclick="showLoginModal()" class="bg-yellow-500 text-white px-8 py-3 rounded-lg font-semibold hover:bg-yellow-600 transition duration-300">
                    <i class="fas fa-user-plus mr-2"></i>Create Account
                </button>
            </div>
        </div>
    </section>

    <!-- NEW FEATURE: Order Tracking & User Accounts -->
    <section id="newFeatures" class="max-w-7xl mx-auto px-4 py-12">
        <div class="text-center mb-12">
            <h2 class="text-3xl font-bold text-gray-800 mb-4">
                <i class="fas fa-shipping-fast text-green-500 mr-2"></i>
                Order Tracking & User Accounts
            </h2>
            <p class="text-gray-600 text-lg">Track your orders and manage your account with our new features!</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            <!-- Feature 1: Order Tracking -->
            <div class="bg-white p-6 rounded-lg shadow-md border border-green-200">
                <div class="text-center mb-4">
                    <i class="fas fa-map-marker-alt text-green-500 text-4xl mb-3"></i>
                    <h3 class="text-xl font-semibold text-gray-800">Real-time Tracking</h3>
                </div>
                <p class="text-gray-600 text-center">Track your orders from confirmation to delivery with live updates.</p>
            </div>

            <!-- Feature 2: User Accounts -->
            <div class="bg-white p-6 rounded-lg shadow-md border border-blue-200">
                <div class="text-center mb-4">
                    <i class="fas fa-user-shield text-blue-500 text-4xl mb-3"></i>
                    <h3 class="text-xl font-semibold text-gray-800">User Accounts</h3>
                </div>
                <p class="text-gray-600 text-center">Create an account to save your details and view order history.</p>
            </div>

            <!-- Feature 3: Order History -->
            <div class="bg-white p-6 rounded-lg shadow-md border border-purple-200">
                <div class="text-center mb-4">
                    <i class="fas fa-history text-purple-500 text-4xl mb-3"></i>
                    <h3 class="text-xl font-semibold text-gray-800">Order History</h3>
                </div>
                <p class="text-gray-600 text-center">Access your complete order history and reorder favorite items.</p>
            </div>
        </div>

        <!-- Sample Order Tracking -->
        <div class="bg-white rounded-lg shadow-md p-6 mb-8">
            <h3 class="text-xl font-semibold mb-4">Live Order Tracking Demo</h3>
            <div class="space-y-6">
                <div class="flex items-center justify-between">
                    <div class="flex items-center">
                        <span class="status-dot bg-green-500"></span>
                        <span class="font-medium">Order Confirmed</span>
                    </div>
                    <span class="text-sm text-gray-500">Today, 10:30 AM</span>
                </div>
                <div class="order-progress">
                    <div class="order-progress-fill bg-green-500" style="width: 25%"></div>
                </div>
                
                <div class="flex items-center justify-between">
                    <div class="flex items-center">
                        <span class="status-dot bg-blue-500"></span>
                        <span class="font-medium text-gray-500">Preparing for Shipment</span>
                    </div>
                    <span class="text-sm text-gray-400">Estimated: Today, 2:00 PM</span>
                </div>
                <div class="order-progress">
                    <div class="order-progress-fill bg-blue-500" style="width: 0%"></div>
                </div>

                <div class="flex items-center justify-between">
                    <div class="flex items-center">
                        <span class="status-dot bg-gray-300"></span>
                        <span class="font-medium text-gray-400">Shipped</span>
                    </div>
                    <span class="text-sm text-gray-400">Estimated: Tomorrow</span>
                </div>
                <div class="order-progress">
                    <div class="order-progress-fill bg-gray-300" style="width: 0%"></div>
                </div>

                <div class="flex items-center justify-between">
                    <div class="flex items-center">
                        <span class="status-dot bg-gray-300"></span>
                        <span class="font-medium text-gray-400">Delivered</span>
                    </div>
                    <span class="text-sm text-gray-400">Estimated: 2 days</span>
                </div>
            </div>
        </div>
    </section>

    <!-- Customer Reviews Section (from FeatureA) -->
    <section id="reviewsSection" class="max-w-7xl mx-auto px-4 py-12 bg-white mt-8 rounded-lg shadow-md">
        <div class="text-center mb-8">
            <h2 class="text-3xl font-bold text-gray-800 mb-2">
                <i class="fas fa-star text-yellow-400 mr-2"></i>
                Customer Reviews
            </h2>
            <p class="text-gray-600">See what our customers are saying about our products</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {% for product in products %}
            <div class="border border-gray-200 rounded-lg p-4">
                <div class="flex items-center mb-3">
                    <img src="{{ product.image }}" alt="{{ product.name }}" class="w-12 h-12 object-cover rounded">
                    <div class="ml-3">
                        <h4 class="font-semibold">{{ product.name }}</h4>
                        <div class="flex items-center">
                            {% for i in range(5) %}
                                {% if i < product.rating|int %}
                                    <i class="fas fa-star text-yellow-400 text-sm"></i>
                                {% else %}
                                    <i class="far fa-star text-yellow-400 text-sm"></i>
                                {% endif %}
                            {% endfor %}
                        </div>
                    </div>
                </div>
                
                <!-- Reviews for this product -->
                <div id="reviews-{{ product.id }}" class="space-y-3 max-h-40 overflow-y-auto">
                    <!-- Reviews will be loaded here -->
                </div>
                
                <!-- Add Review Form -->
                <div class="mt-4 border-t pt-3">
                    <h5 class="font-semibold mb-2">Add Your Review</h5>
                    <div class="flex mb-2" id="stars-{{ product.id }}">
                        {% for i in range(1, 6) %}
                        <i class="far fa-star text-yellow-400 review-star cursor-pointer mr-1" 
                           data-rating="{{ i }}" 
                           data-product="{{ product.id }}"
                           onmouseover="highlightStars({{ i }}, {{ product.id }})"
                           onmouseout="resetStars({{ product.id }})"
                           onclick="setRating({{ i }}, {{ product.id }})"></i>
                        {% endfor %}
                    </div>
                    <textarea id="review-text-{{ product.id }}" 
                              placeholder="Write your review..." 
                              class="w-full px-3 py-2 border border-gray-300 rounded text-sm mb-2"></textarea>
                    <button onclick="submitReview({{ product.id }})" 
                            class="w-full bg-blue-600 text-white py-2 rounded text-sm hover:bg-blue-700">
                        Submit Review
                    </button>
                </div>
            </div>
            {% endfor %}
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

    <!-- NEW: Orders Sidebar -->
    <div id="ordersSidebar" class="fixed top-0 right-0 h-full w-96 bg-white shadow-2xl transform translate-x-full transition-transform duration-300 z-50">
        <div class="p-4 border-b border-gray-200 flex justify-between items-center">
            <h3 class="text-lg font-semibold">Your Orders</h3>
            <button onclick="toggleOrders()" class="text-gray-500 hover:text-gray-700">
                <i class="fas fa-times text-xl"></i>
            </button>
        </div>
        <div id="ordersItems" class="p-4 h-3/4 overflow-y-auto">
            <div id="emptyOrders" class="text-center text-gray-500 py-8">
                <i class="fas fa-clipboard-list text-4xl mb-4 text-gray-300"></i>
                <p>No orders yet</p>
                <p class="text-sm mt-2">Complete your first purchase to see orders here</p>
            </div>
        </div>
    </div>

    <!-- NEW: Login/Register Modal -->
    <div id="loginModal" class="fixed inset-0 bg-black bg-opacity-50 hidden z-50 flex items-center justify-center">
        <div class="bg-white rounded-lg w-full max-w-md mx-4">
            <div class="p-6 border-b border-gray-200 flex justify-between items-center">
                <h3 class="text-lg font-semibold">Login / Register</h3>
                <button onclick="hideLoginModal()" class="text-gray-500 hover:text-gray-700">
                    <i class="fas fa-times text-xl"></i>
                </button>
            </div>
            <div class="p-6">
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
                    <input type="email" id="loginEmail" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500" placeholder="your@email.com">
                </div>
                <div class="mb-6">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Password</label>
                    <input type="password" id="loginPassword" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500" placeholder="••••••••">
                </div>
                <div class="flex space-x-4">
                    <button onclick="login()" class="flex-1 bg-blue-600 text-white py-2 rounded-lg font-semibold hover:bg-blue-700">
                        Login
                    </button>
                    <button onclick="register()" class="flex-1 bg-green-600 text-white py-2 rounded-lg font-semibold hover:bg-green-700">
                        Register
                    </button>
                </div>
                <p class="text-xs text-gray-500 mt-4 text-center">
                    Demo: Use any email and password to test
                </p>
            </div>
        </div>
    </div>

    <!-- Overlays -->
    <div id="cartOverlay" class="fixed inset-0 bg-black bg-opacity-50 hidden z-40" onclick="toggleCart()"></div>
    <div id="wishlistOverlay" class="fixed inset-0 bg-black bg-opacity-50 hidden z-40" onclick="toggleWishlist()"></div>
    <div id="ordersOverlay" class="fixed inset-0 bg-black bg-opacity-50 hidden z-40" onclick="toggleOrders()"></div>
    <div id="loginOverlay" class="fixed inset-0 bg-black bg-opacity-50 hidden z-40" onclick="hideLoginModal()"></div>

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
        let orders = [];
        let currentUser = null;
        let currentRatings = {};
        
        // Load user data
        function loadUserData() {
            fetch('/get_current_user')
                .then(response => response.json())
                .then(data => {
                    currentUser = data.user;
                    updateUserUI();
                });
            
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
            
            fetch('/get_orders')
                .then(response => response.json())
                .then(data => {
                    orders = data;
                    updateOrdersUI();
                });

            // Load reviews
            {% for product in products %}
            fetch('/get_reviews?product_id={{ product.id }}')
                .then(response => response.json())
                .then(reviews => {
                    displayReviews({{ product.id }}, reviews);
                });
            {% endfor %}
        }

        // User account functions
        function showLoginModal() {
            document.getElementById('loginModal').classList.remove('hidden');
            document.getElementById('loginOverlay').classList.remove('hidden');
        }

        function hideLoginModal() {
            document.getElementById('loginModal').classList.add('hidden');
            document.getElementById('loginOverlay').classList.add('hidden');
        }

        function login() {
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;
            
            if (!email || !password) {
                showNotification('Please enter email and password', 'error');
                return;
            }

            fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({email: email, password: password})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    currentUser = data.user;
                    updateUserUI();
                    hideLoginModal();
                    showNotification('Login successful!', 'success');
                    loadUserData(); // Reload all data
                } else {
                    showNotification(data.message, 'error');
                }
            });
        }

        function register() {
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;
            
            if (!email || !password) {
                showNotification('Please enter email and password', 'error');
                return;
            }

            fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({email: email, password: password, name: email.split('@')[0]})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    currentUser = data.user;
                    updateUserUI();
                    hideLoginModal();
                    showNotification('Registration successful!', 'success');
                    loadUserData(); // Reload all data
                } else {
                    showNotification(data.message, 'error');
                }
            });
        }

        function logout() {
            fetch('/logout', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    currentUser = null;
                    updateUserUI();
                    showNotification('Logged out successfully', 'success');
                    loadUserData(); // Reload all data
                }
            });
        }

        function updateUserUI() {
            const userName = document.getElementById('userName');
            const userEmail = document.getElementById('userEmail');
            
            if (currentUser) {
                userName.textContent = currentUser.name;
                userEmail.textContent = currentUser.email;
            } else {
                userName.textContent = 'Guest User';
                userEmail.textContent = 'Not logged in';
            }
        }

        function toggleUserMenu() {
            document.getElementById('userMenu').classList.toggle('hidden');
        }

        // Orders functions
        function toggleOrders() {
            const sidebar = document.getElementById('ordersSidebar');
            const overlay = document.getElementById('ordersOverlay');
            sidebar.classList.toggle('translate-x-full');
            overlay.classList.toggle('hidden');
        }

        function updateOrdersUI() {
            const ordersCount = document.getElementById('ordersCount');
            const ordersItems = document.getElementById('ordersItems');
            const emptyOrders = document.getElementById('emptyOrders');

            ordersCount.textContent = orders.length;

            if (orders.length === 0) {
                emptyOrders.style.display = 'block';
                ordersItems.innerHTML = '<div id="emptyOrders" class="text-center text-gray-500 py-8"><i class="fas fa-clipboard-list text-4xl mb-4 text-gray-300"></i><p>No orders yet</p><p class="text-sm mt-2">Complete your first purchase to see orders here</p></div>';
            } else {
                emptyOrders.style.display = 'none';
                ordersItems.innerHTML = orders.map(order => `
                    <div class="border border-gray-200 rounded-lg p-4 mb-4">
                        <div class="flex justify-between items-start mb-3">
                            <div>
                                <h4 class="font-semibold">Order #${order.id.slice(-6)}</h4>
                                <p class="text-sm text-gray-500">${new Date(order.timestamp).toLocaleDateString()}</p>
                            </div>
                            <span class="px-2 py-1 rounded text-xs font-semibold 
                                ${order.status === 'delivered' ? 'bg-green-100 text-green-800' : 
                                  order.status === 'shipped' ? 'bg-blue-100 text-blue-800' : 
                                  'bg-yellow-100 text-yellow-800'}">
                                ${order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                            </span>
                        </div>
                        <div class="space-y-2">
                            ${order.items.map(item => `
                                <div class="flex justify-between text-sm">
                                    <span>${item.name} x${item.quantity}</span>
                                    <span>$${(item.price * item.quantity).toFixed(2)}</span>
                                </div>
                            `).join('')}
                        </div>
                        <div class="flex justify-between items-center mt-3 pt-3 border-t border-gray-200">
                            <span class="font-semibold">Total</span>
                            <span class="font-bold text-green-600">$${order.total.toFixed(2)}</span>
                        </div>
                        <div class="mt-3">
                            <div class="order-progress">
                                <div class="order-progress-fill 
                                    ${order.status === 'confirmed' ? 'bg-yellow-500 w-1/4' : 
                                      order.status === 'shipped' ? 'bg-blue-500 w-2/3' : 
                                      'bg-green-500 w-full'}"></div>
                            </div>
                        </div>
                    </div>
                `).join('');
            }
        }

        function showOrderHistory() {
            toggleOrders();
            toggleUserMenu();
        }

        // Enhanced checkout to create orders
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
                    loadUserData(); // Reload to get new order
                }
            });
        }

        // Review functions (from FeatureA)
        function displayReviews(productId, reviews) {
            const container = document.getElementById(`reviews-${productId}`);
            if (reviews.length === 0) {
                container.innerHTML = '<p class="text-gray-500 text-sm">No reviews yet. Be the first to review!</p>';
                return;
            }

            container.innerHTML = reviews.map(review => `
                <div class="bg-gray-50 p-2 rounded">
                    <div class="flex justify-between items-center mb-1">
                        <div class="flex">
                            ${Array.from({length: 5}, (_, i) => 
                                `<i class="fas fa-star ${i < review.rating ? 'text-yellow-400' : 'text-gray-300'} text-xs"></i>`
                            ).join('')}
                        </div>
                        <span class="text-xs text-gray-500">${new Date(review.timestamp).toLocaleDateString()}</span>
                    </div>
                    <p class="text-sm text-gray-700">${review.text}</p>
                    <p class="text-xs text-gray-500 mt-1">- ${review.author}</p>
                </div>
            `).join('');
        }

        function highlightStars(rating, productId) {
            const stars = document.querySelectorAll(`#stars-${productId} .fa-star`);
            stars.forEach((star, index) => {
                if (index < rating) {
                    star.classList.add('fas', 'text-yellow-400');
                    star.classList.remove('far');
                }
            });
        }

        function resetStars(productId) {
            const currentRating = currentRatings[productId] || 0;
            const stars = document.querySelectorAll(`#stars-${productId} .fa-star`);
            stars.forEach((star, index) => {
                if (index < currentRating) {
                    star.classList.add('fas', 'text-yellow-400');
                    star.classList.remove('far');
                } else {
                    star.classList.add('far');
                    star.classList.remove('fas');
                }
            });
        }

        function setRating(rating, productId) {
            currentRatings[productId] = rating;
            resetStars(productId);
        }

        function submitReview(productId) {
            const rating = currentRatings[productId];
            const text = document.getElementById(`review-text-${productId}`).value;
            
            if (!rating) {
                showNotification('Please select a rating!', 'error');
                return;
            }
            
            if (!text.trim()) {
                showNotification('Please write a review!', 'error');
                return;
            }

            fetch('/add_review', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    product_id: productId,
                    rating: rating,
                    text: text,
                    author: currentUser ? currentUser.name : 'Customer'
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Review submitted successfully!', 'success');
                    document.getElementById(`review-text-${productId}`).value = '';
                    currentRatings[productId] = 0;
                    resetStars(productId);
                    // Reload reviews
                    fetch('/get_reviews?product_id=' + productId)
                        .then(response => response.json())
                        .then(reviews => {
                            displayReviews(productId, reviews);
                        });
                }
            });
        }

        // Wishlist functions (from FeatureB)
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

        // Cart functions
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

        // Utility functions
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

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadUserData();
            // Close user menu when clicking outside
            document.addEventListener('click', function(event) {
                if (!event.target.closest('#userMenu') && !event.target.closest('button[onclick="toggleUserMenu()"]')) {
                    document.getElementById('userMenu').classList.add('hidden');
                }
            });
        });
    </script>
</body>
</html>
"""

# Routes for FeatureC: User Accounts & Order Tracking
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password required'})
    
    # Simple demo - in real app, use proper authentication
    user_id = str(uuid.uuid4())
    user_profiles[user_id] = {
        'id': user_id,
        'email': email,
        'name': name,
        'joined': datetime.now().isoformat()
    }
    
    session['user_id'] = user_id
    return jsonify({'success': True, 'user': user_profiles[user_id]})

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    # Simple demo - in real app, verify credentials properly
    user_id = str(uuid.uuid4())
    user_profiles[user_id] = {
        'id': user_id,
        'email': email,
        'name': email.split('@')[0],
        'joined': datetime.now().isoformat()
    }
    
    session['user_id'] = user_id
    return jsonify({'success': True, 'user': user_profiles[user_id]})

@app.route("/logout", methods=["POST"])
def logout():
    session.pop('user_id', None)
    return jsonify({'success': True})

@app.route("/get_current_user")
def get_current_user():
    user_id = session.get('user_id')
    user = user_profiles.get(user_id) if user_id else None
    return jsonify({'user': user})

@app.route("/get_orders")
def get_orders():
    user_id = session.get('user_id')
    if user_id:
        user_orders = [order for order in orders.values() if order['user_id'] == user_id]
        return jsonify(user_orders)
    return jsonify([])

# Enhanced checkout to create orders
@app.route("/checkout", methods=["POST"])
def checkout():
    if 'cart' not in session or not session['cart']:
        return jsonify({'success': False, 'message': 'Cart is empty!'})
    
    user_id = session.get('user_id')
    cart = session['cart']
    
    # Create order
    order_id = str(uuid.uuid4())
    total = sum(item['price'] * item['quantity'] for item in cart)
    
    orders[order_id] = {
        'id': order_id,
        'user_id': user_id,
        'items': cart.copy(),
        'total': total,
        'status': 'confirmed',
        'timestamp': datetime.now().isoformat()
    }
    
    # Clear cart
    session['cart'] = []
    
    return jsonify({'success': True, 'message': 'Order placed successfully!', 'order_id': order_id})

# Routes for FeatureB: Wishlist
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

# Routes for FeatureA: Reviews
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

# Routes for Cart (Base Feature)
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
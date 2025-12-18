<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Profile - Nakhrali</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style_profile.css') }}">
</head>
<body>
    <div class="profile-container">
        <!-- Sidebar -->
        <div class="sidebar">
            <h2 class="logo">Nakhrali</h2>
            <ul>
                <li><a href="{{ url_for('profile', section='profile') }}" class="{{ 'active' if section=='profile' else '' }}">Basic Information</a></li>
                <li><a href="{{ url_for('profile', section='address') }}" class="{{ 'active' if section=='address' else '' }}">Delivery Address</a></li>
                <li><a href="{{ url_for('profile', section='orders') }}" class="{{ 'active' if section=='orders' else '' }}">My Orders</a></li>
                <li><a href="{{ url_for('profile', section='change-password') }}" class="{{ 'active' if section=='change-password' else '' }}">Change Password</a></li>
                <li><a href="{{ url_for('logout') }}">Logout</a></li>
                <li><a href="{{ url_for('home') }}">← Back to Home</a></li>
            </ul>
        </div>

        <!-- Content -->
        <div class="content">
            {% if section == "profile" %}
                <h2>Basic Information</h2>
                <p><strong>Name:</strong> {{ user.name }}</p>
                <p><strong>Email:</strong> {{ user.email }}</p>
                <p><strong>DOB:</strong> {{ user.dob or "Not set" }}</p>
                <p><strong>Gender:</strong> {{ user.gender or "Not set" }}</p>
                <p><strong>Phone:</strong> {{ user.phone }}</p>

            {% elif section == "address" %}
                <h2>My Delivery Addresses</h2>

                
{% if user.addresses %}
    <div class="address-container">
        {% for addr in user.addresses %}
            <div class="address-card">
                <p class="address-text">
                    <strong>Address:</strong> {{ addr.address }}<br>
                    <strong>City:</strong> {{ addr.city }}<br>
                    <strong>State:</strong> {{ addr.state }}<br>
                    <strong>Pincode:</strong> {{ addr.pincode }}
                </p>
                <a href="{{ url_for('delete_address', address_id=addr.id) }}" 
                  class="delete-btn" 
                  onclick="return confirm('Delete this address?')">
                  Delete
                </a>
            </div>
        {% endfor %}
    </div>
{% else %}
    <p class="no-address">No delivery addresses saved yet.</p>
{% endif %}


                <!-- Add new address form -->
                <h3>Add New Address</h3>
                <form method="POST" action="{{ url_for('add_address') }}">
                  <input type="text" name="address" placeholder="Address" required>
                  <input type="text" name="city" placeholder="City" required>
                  <input type="text" name="state" placeholder="State" required>
                  <input type="text" name="pincode" placeholder="Pincode" required>
                  <button type="submit">Save Address</button>
                </form>


            {% elif section == "orders" %}
                <h2>My Orders</h2>
                {% if orders %}
                    <ul class="orders-list">
                        {% for order in orders %}
                            <li>
                                <strong>Order #{{ order.id }}</strong> - {{ order.product_name }} - ₹{{ order.price }}
                                <small>Status: {{ order.status }}</small>
                            </li>
                        {% endfor %}
                    </ul>
                {% else %}
                    <p>No orders found.</p>
                {% endif %}

            {% elif section == "change-password" %}
                <h2>Change Password</h2>
                <form method="POST" action="{{ url_for('profile', section='change-password') }}">
                    <label>Current Password</label>
                    <input type="password" name="current_password" required>
                    <label>New Password</label>
                    <input type="password" name="new_password" required>
                    <button type="submit">Update Password</button>
                </form>
            {% endif %}
        </div>
    </div>
</body>
</html>

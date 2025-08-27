#!/bin/bash
# Silent MariaDB Setup Script for AI Language Tutor App

echo "🗄️  AI Language Tutor - Silent Database Setup"
echo "=============================================="

# Function to check if MariaDB is running
check_mariadb_status() {
    if brew services list | grep -q "mariadb.*started"; then
        echo "✅ MariaDB is running"
        return 0
    else
        echo "❌ MariaDB is not running"
        return 1
    fi
}

# Function to setup database using expect (non-interactive)
setup_database() {
    # Create SQL setup file
    cat > /tmp/db_setup.sql << 'EOF'
CREATE DATABASE IF NOT EXISTS ai_language_tutor
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'ai_tutor_user'@'localhost' IDENTIFIED BY 'ai_tutor_pass_2024';
GRANT ALL PRIVILEGES ON ai_language_tutor.* TO 'ai_tutor_user'@'localhost';
FLUSH PRIVILEGES;

SELECT 'Database Setup Complete' as Status;
SHOW DATABASES;
EOF

    # Try to execute SQL without password first
    if mysql -u root < /tmp/db_setup.sql 2>/dev/null; then
        echo "✅ Database setup completed successfully"
        rm /tmp/db_setup.sql
        return 0
    fi
    
    # Try with sudo if first attempt failed
    if sudo mysql -u root < /tmp/db_setup.sql 2>/dev/null; then
        echo "✅ Database setup completed successfully (with sudo)"
        rm /tmp/db_setup.sql
        return 0
    fi
    
    echo "❌ Database setup failed - need manual intervention"
    rm /tmp/db_setup.sql
    return 1
}

# Function to test connection
test_connection() {
    if mysql -u ai_tutor_user -pai_tutor_pass_2024 -D ai_language_tutor -e "SELECT 'Connection successful' as Test;" 2>/dev/null; then
        echo "✅ Application user connection test successful"
        return 0
    else
        echo "❌ Application user connection test failed"
        return 1
    fi
}

# Function to update environment file
update_env_file() {
    ENV_FILE="$(dirname "$0")/.env"
    
    if [ -f "$ENV_FILE" ]; then
        # Backup original .env
        cp "$ENV_FILE" "$ENV_FILE.backup"
        
        # Update database URL
        sed -i '' 's|DATABASE_URL=.*|DATABASE_URL=mysql+pymysql://ai_tutor_user:ai_tutor_pass_2024@localhost/ai_language_tutor|' "$ENV_FILE"
        echo "✅ Environment file updated"
    else
        echo "⚠️  Environment file not found: $ENV_FILE"
    fi
}

# Main execution
echo "1. Checking MariaDB status..."
check_mariadb_status

if [ $? -eq 0 ]; then
    echo -e "\n2. Setting up database..."
    setup_database
    
    if [ $? -eq 0 ]; then
        echo -e "\n3. Testing connection..."
        test_connection
        
        if [ $? -eq 0 ]; then
            echo -e "\n4. Updating environment configuration..."
            update_env_file
            echo -e "\n🎉 Database setup completed successfully!"
            echo "You can now test the application with MariaDB."
        fi
    fi
else
    echo "Please start MariaDB first: brew services start mariadb"
fi
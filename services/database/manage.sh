#!/bin/bash
set -e

# MongoDB Management Script for Project Manager
# This script provides easy commands to manage the MongoDB instance

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTAINER_NAME="project-manager-mongodb"
MONGO_EXPRESS_CONTAINER_NAME="project-manager-mongo-express"
COMPOSE_FILE="$SCRIPT_DIR/podman-compose.yml"
BACKUP_DIR="$SCRIPT_DIR/backups"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "MongoDB Management Script for Project Manager"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  start                 Start MongoDB and optional web admin"
    echo "  stop                  Stop all services"
    echo "  restart               Restart all services"
    echo "  status                Show status of all services"
    echo "  logs                  Show logs (use -f to follow)"
    echo "  shell                 Connect to MongoDB shell"
    echo "  backup                Create a database backup"
    echo "  restore <file>        Restore from backup file"
    echo "  clean                 Remove all containers and volumes"
    echo "  build                 Build the container image"
    echo "  health                Check health of MongoDB service"
    echo "  monitor               Show real-time container stats"
    echo "  collections           List all collections in database"
    echo "  users                 List database users"
    echo "  help                  Show this help message"
    echo ""
    echo "Options:"
    echo "  --no-admin           Skip starting MongoDB Express admin interface"
    echo "  -f, --follow         Follow logs (for logs command)"
    echo ""
    echo "Examples:"
    echo "  $0 start              # Start MongoDB with web admin"
    echo "  $0 start --no-admin   # Start only MongoDB"
    echo "  $0 logs -f            # Follow logs in real-time"
    echo "  $0 backup             # Create backup"
    echo "  $0 restore backup.gz  # Restore from backup"
}

# Function to check if podman-compose is available
check_podman_compose() {
    if ! command -v podman-compose &> /dev/null; then
        print_error "podman-compose is not installed. Please install it first."
        exit 1
    fi
}

# Function to start services
start_services() {
    local no_admin=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-admin)
                no_admin=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done
    
    check_podman_compose
    print_info "Starting MongoDB services..."
    
    cd "$SCRIPT_DIR"
    
    if [ "$no_admin" = true ]; then
        podman-compose up -d mongodb
        print_success "MongoDB started without web admin interface"
    else
        podman-compose up -d
        print_success "MongoDB and web admin interface started"
        print_info "Web admin available at: http://localhost:8081"
    fi
    
    print_info "MongoDB connection: mongodb://localhost:27017"
}

# Function to stop services
stop_services() {
    check_podman_compose
    print_info "Stopping MongoDB services..."
    
    cd "$SCRIPT_DIR"
    podman-compose down
    print_success "All services stopped"
}

# Function to restart services
restart_services() {
    stop_services
    start_services "$@"
}

# Function to show status
show_status() {
    check_podman_compose
    print_info "Service Status:"
    
    cd "$SCRIPT_DIR"
    podman-compose ps
}

# Function to show logs
show_logs() {
    local follow=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -f|--follow)
                follow=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done
    
    check_podman_compose
    cd "$SCRIPT_DIR"
    
    if [ "$follow" = true ]; then
        podman-compose logs -f
    else
        podman-compose logs
    fi
}

# Function to connect to MongoDB shell
connect_shell() {
    print_info "Connecting to MongoDB shell..."
    podman exec -it "$CONTAINER_NAME" mongo -u admin -p projectmanager123 --authenticationDatabase admin
}

# Function to create backup
create_backup() {
    print_info "Creating database backup..."
    "$SCRIPT_DIR/backup.sh"
}

# Function to restore from backup
restore_backup() {
    if [ -z "$1" ]; then
        print_error "Please provide backup file name"
        print_info "Usage: $0 restore <backup_file>"
        exit 1
    fi
    
    print_info "Restoring from backup: $1"
    "$SCRIPT_DIR/restore.sh" "$1"
}

# Function to clean all containers and volumes
clean_all() {
    print_warning "This will remove all containers and volumes (data will be lost!)"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        check_podman_compose
        cd "$SCRIPT_DIR"
        podman-compose down -v
        podman-compose rm -f
        print_success "All containers and volumes removed"
    else
        print_info "Operation cancelled"
    fi
}

# Function to build container image
build_image() {
    check_podman_compose
    print_info "Building MongoDB container image..."
    
    cd "$SCRIPT_DIR"
    podman-compose build
    print_success "Container image built successfully"
}

# Function to check health
check_health() {
    print_info "Checking MongoDB health..."
    
    # Check if container is running
    if podman ps --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
        print_success "Container is running"
        
        # Check MongoDB connection
        if podman exec "$CONTAINER_NAME" mongo --eval "db.adminCommand('ping')" &> /dev/null; then
            print_success "MongoDB is responding"
        else
            print_error "MongoDB is not responding"
        fi
        
        # Show detailed health
        podman inspect "$CONTAINER_NAME" | grep -A 10 '"Health"'
    else
        print_error "Container is not running"
    fi
}

# Function to show real-time stats
show_monitor() {
    print_info "Showing real-time container stats (Press Ctrl+C to stop)"
    podman stats "$CONTAINER_NAME"
}

# Function to list collections
list_collections() {
    print_info "Listing collections in project_manager database..."
    podman exec "$CONTAINER_NAME" mongo -u admin -p projectmanager123 --authenticationDatabase admin --eval "use project_manager; db.getCollectionNames()"
}

# Function to list users
list_users() {
    print_info "Listing database users..."
    podman exec "$CONTAINER_NAME" mongo -u admin -p projectmanager123 --authenticationDatabase admin --eval "use project_manager; db.getUsers()"
}

# Main script logic
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

case $1 in
    start)
        shift
        start_services "$@"
        ;;
    stop)
        stop_services
        ;;
    restart)
        shift
        restart_services "$@"
        ;;
    status)
        show_status
        ;;
    logs)
        shift
        show_logs "$@"
        ;;
    shell)
        connect_shell
        ;;
    backup)
        create_backup
        ;;
    restore)
        shift
        restore_backup "$@"
        ;;
    clean)
        clean_all
        ;;
    build)
        build_image
        ;;
    health)
        check_health
        ;;
    monitor)
        show_monitor
        ;;
    collections)
        list_collections
        ;;
    users)
        list_users
        ;;
    help)
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac 
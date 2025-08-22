const { ipcRenderer } = require('electron');

class AguaApp {
    constructor() {
        this.currentPage = 'dashboard';
        this.isLoggedIn = false;
        this.clients = [];
        this.filteredClients = [];
        this.currentFilter = 'all';
        this.currentView = 'table';
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.updateCurrentDate();
        this.setupFilterButtons();
        this.setupViewToggle();
    }

    setupEventListeners() {
        // Login form
        const loginForm = document.getElementById('loginForm');
        loginForm.addEventListener('submit', (e) => this.handleLogin(e));

        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => this.handleNavigation(e));
        });

        // Logout
        document.getElementById('logoutBtn').addEventListener('click', () => this.logout());

        // Sidebar toggle
        document.getElementById('sidebarToggle').addEventListener('click', () => this.toggleSidebar());
    }

    async handleLogin(e) {
        e.preventDefault();
        const pinInput = document.getElementById('pinInput');
        const pin = pinInput.value;
        const errorDiv = document.getElementById('loginError');

        if (!pin) {
            this.showLoginError('Por favor ingrese su PIN');
            return;
        }

        try {
            const isValid = await ipcRenderer.invoke('db-login', pin);
            
            if (isValid) {
                this.isLoggedIn = true;
                this.showMainApp();
                await this.loadDashboard();
            } else {
                this.showLoginError('PIN incorrecto. Intente nuevamente.');
                pinInput.value = '';
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showLoginError('Error al verificar PIN');
        }
    }

    showLoginError(message) {
        const errorDiv = document.getElementById('loginError');
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
        
        setTimeout(() => {
            errorDiv.classList.add('hidden');
        }, 3000);
    }

    showMainApp() {
        document.getElementById('loginScreen').classList.add('hidden');
        document.getElementById('mainApp').classList.remove('hidden');
    }

    logout() {
        this.isLoggedIn = false;
        document.getElementById('loginScreen').classList.remove('hidden');
        document.getElementById('mainApp').classList.add('hidden');
        document.getElementById('pinInput').value = '';
    }

    handleNavigation(e) {
        e.preventDefault();
        const page = e.currentTarget.dataset.page;
        this.navigateToPage(page);
    }

    navigateToPage(page) {
        // Update active nav item
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('bg-gray-700');
        });
        document.querySelector(`[data-page="${page}"]`).classList.add('bg-gray-700');

        // Hide all pages
        document.querySelectorAll('.page-content').forEach(pageEl => {
            pageEl.classList.add('hidden');
        });

        // Show selected page
        document.getElementById(`${page}Page`).classList.remove('hidden');

        // Update page title
        const titles = {
            dashboard: 'Dashboard',
            clients: 'Gestión de Clientes',
            calendar: 'Calendario',
            settings: 'Ajustes'
        };
        document.getElementById('pageTitle').textContent = titles[page];

        this.currentPage = page;

        // Load page specific data
        if (page === 'dashboard') {
            this.loadDashboard();
        } else if (page === 'clients') {
            this.loadClientsPage();
        } else if (page === 'calendar') {
            this.loadCalendarPage();
        }
    }

    async loadDashboard() {
        try {
            // Load dashboard stats
            const stats = await ipcRenderer.invoke('db-get-dashboard-stats');
            this.updateDashboardStats(stats);

            // Load clients for table
            this.clients = await ipcRenderer.invoke('db-get-clients');
            this.filteredClients = [...this.clients];
            this.renderClientsTable();
            this.updateChart();
        } catch (error) {
            console.error('Error loading dashboard:', error);
        }
    }

    updateDashboardStats(stats) {
        document.getElementById('totalClients').textContent = stats.totalClients || 0;
        document.getElementById('clientsPaid').textContent = stats.clientsPaid || 0;
        document.getElementById('clientsWithDebt').textContent = stats.clientsWithDebt || 0;
        document.getElementById('excessConsumption').textContent = stats.excessConsumption || 0;
    }

    renderClientsTable() {
        const tbody = document.getElementById('clientsTableBody');
        tbody.innerHTML = '';

        this.filteredClients.forEach(client => {
            const row = document.createElement('tr');
            row.className = 'hover:bg-gray-50 cursor-pointer';
            
            const statusIcon = this.getStatusIcon(client);
            const lastPayment = client.last_payment_date ? 
                new Date(client.last_payment_date).toLocaleDateString('es-ES') : 
                'Sin pagos';

            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${client.id}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${client.name}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${client.address}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${statusIcon}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${lastPayment}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button class="text-water-600 hover:text-water-900 mr-3" onclick="app.viewClient(${client.id})">Ver</button>
                    <button class="text-primary-600 hover:text-primary-900" onclick="app.editClient(${client.id})">Editar</button>
                </td>
            `;

            tbody.appendChild(row);
        });
    }

    getStatusIcon(client) {
        if (client.excess_consumption > 0) {
            return '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-water-100 text-water-800">💧 Exceso</span>';
        } else if (client.payment_status === 'paid') {
            return '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">✅ Pagado</span>';
        } else {
            return '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">❌ Pendiente</span>';
        }
    }

    setupFilterButtons() {
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Update active filter button
                document.querySelectorAll('.filter-btn').forEach(b => {
                    b.classList.remove('active', 'bg-primary-500', 'text-white');
                    b.classList.add('bg-gray-100', 'text-gray-700', 'hover:bg-gray-200');
                });
                
                e.target.classList.remove('bg-gray-100', 'text-gray-700', 'hover:bg-gray-200');
                e.target.classList.add('active', 'bg-primary-500', 'text-white');

                const filter = e.target.dataset.filter;
                this.applyFilter(filter);
            });
        });

        // Set initial active state
        const activeBtn = document.querySelector('.filter-btn.active');
        if (activeBtn) {
            activeBtn.classList.add('bg-primary-500', 'text-white');
        }
    }

    applyFilter(filter) {
        this.currentFilter = filter;
        
        switch (filter) {
            case 'all':
                this.filteredClients = [...this.clients];
                break;
            case 'paid':
                this.filteredClients = this.clients.filter(c => c.payment_status === 'paid' && c.excess_consumption <= 0);
                break;
            case 'debt':
                this.filteredClients = this.clients.filter(c => c.payment_status !== 'paid');
                break;
            case 'excess':
                this.filteredClients = this.clients.filter(c => c.excess_consumption > 0);
                break;
        }

        this.renderClientsTable();
        this.updateChart();
    }

    setupViewToggle() {
        document.getElementById('tableViewBtn').addEventListener('click', () => {
            this.switchView('table');
        });

        document.getElementById('chartViewBtn').addEventListener('click', () => {
            this.switchView('chart');
        });
    }

    switchView(view) {
        // Update button states
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.classList.remove('active', 'bg-primary-500', 'text-white');
            btn.classList.add('bg-gray-100', 'text-gray-700');
        });

        if (view === 'table') {
            document.getElementById('tableViewBtn').classList.add('active', 'bg-primary-500', 'text-white');
            document.getElementById('tableView').classList.remove('hidden');
            document.getElementById('chartView').classList.add('hidden');
        } else {
            document.getElementById('chartViewBtn').classList.add('active', 'bg-primary-500', 'text-white');
            document.getElementById('tableView').classList.add('hidden');
            document.getElementById('chartView').classList.remove('hidden');
            this.updateChart();
        }

        this.currentView = view;
    }

    updateChart() {
        if (this.currentView !== 'chart') return;

        const ctx = document.getElementById('dashboardChart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.chart) {
            this.chart.destroy();
        }

        const statusCounts = {
            paid: this.filteredClients.filter(c => c.payment_status === 'paid' && c.excess_consumption <= 0).length,
            debt: this.filteredClients.filter(c => c.payment_status !== 'paid').length,
            excess: this.filteredClients.filter(c => c.excess_consumption > 0).length
        };

        this.chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Al Corriente', 'Con Deuda', 'Exceso Consumo'],
                datasets: [{
                    data: [statusCounts.paid, statusCounts.debt, statusCounts.excess],
                    backgroundColor: [
                        '#10B981', // Green
                        '#EF4444', // Red
                        '#0EA5E9'  // Water blue
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }

    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.toggle('-translate-x-full');
    }

    updateCurrentDate() {
        const now = new Date();
        const options = { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        };
        document.getElementById('currentDate').textContent = 
            now.toLocaleDateString('es-ES', options);
    }

    // Placeholder methods for client management
    viewClient(id) {
        console.log('View client:', id);
        // TODO: Implement client detail view
    }

    editClient(id) {
        console.log('Edit client:', id);
        // TODO: Implement client edit modal
    }

    loadClientsPage() {
        if (!clientsManager) {
            clientsManager = new ClientsManager(this);
            clientsManager.init();
        } else {
            clientsManager.loadClients();
        }
    }

    loadCalendarPage() {
        if (!calendarManager) {
            calendarManager = new CalendarManager(this);
            calendarManager.init();
        } else {
            calendarManager.refresh();
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new AguaApp();
});

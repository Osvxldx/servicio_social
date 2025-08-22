class ClientsManager {
    constructor(app) {
        this.app = app;
        this.clients = [];
        this.searchTimeout = null;
        this.selectedClient = null;
    }

    async init() {
        this.setupClientSearch();
        this.setupClientModals();
        await this.loadClients();
    }

    setupClientSearch() {
        const searchInput = document.getElementById('clientSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                clearTimeout(this.searchTimeout);
                this.searchTimeout = setTimeout(() => {
                    this.performSearch(e.target.value);
                }, 300);
            });
        }
    }

    async performSearch(query) {
        if (!query.trim()) {
            this.clients = await ipcRenderer.invoke('db-get-clients');
        } else {
            this.clients = await ipcRenderer.invoke('db-search-clients', query.trim());
        }
        this.renderClientsList();
    }

    async loadClients() {
        try {
            this.clients = await ipcRenderer.invoke('db-get-clients');
            this.renderClientsList();
        } catch (error) {
            console.error('Error loading clients:', error);
        }
    }

    renderClientsList() {
        const container = document.getElementById('clientsList');
        if (!container) return;

        container.innerHTML = '';

        if (this.clients.length === 0) {
            container.innerHTML = `
                <div class="text-center py-12">
                    <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                    </svg>
                    <h3 class="mt-2 text-sm font-medium text-gray-900">No hay clientes</h3>
                    <p class="mt-1 text-sm text-gray-500">Comience agregando un nuevo cliente.</p>
                </div>
            `;
            return;
        }

        this.clients.forEach(client => {
            const clientCard = this.createClientCard(client);
            container.appendChild(clientCard);
        });
    }

    createClientCard(client) {
        const card = document.createElement('div');
        card.className = 'bg-white rounded-lg shadow hover:shadow-md transition-shadow duration-200 p-6 cursor-pointer';
        
        const statusIcon = this.getStatusIcon(client);
        const lastPayment = client.last_payment_date ? 
            new Date(client.last_payment_date).toLocaleDateString('es-ES') : 
            'Sin pagos';

        card.innerHTML = `
            <div class="flex items-start justify-between">
                <div class="flex-1">
                    <div class="flex items-center">
                        <h3 class="text-lg font-medium text-gray-900">${client.name}</h3>
                        <span class="ml-2 text-sm text-gray-500">#${client.id}</span>
                    </div>
                    <p class="text-sm text-gray-600 mt-1">${client.address}</p>
                    <div class="mt-2 flex items-center space-x-4">
                        <div>${statusIcon}</div>
                        <span class="text-xs text-gray-500">Último pago: ${lastPayment}</span>
                    </div>
                </div>
                <div class="flex space-x-2">
                    <button class="text-water-600 hover:text-water-800 p-1" onclick="clientsManager.viewClient(${client.id})" title="Ver detalles">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                        </svg>
                    </button>
                    <button class="text-primary-600 hover:text-primary-800 p-1" onclick="clientsManager.editClient(${client.id})" title="Editar">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                        </svg>
                    </button>
                </div>
            </div>
        `;

        card.addEventListener('click', (e) => {
            if (!e.target.closest('button')) {
                this.viewClient(client.id);
            }
        });

        return card;
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

    setupClientModals() {
        // Add client modal
        const addBtn = document.getElementById('addClientBtn');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.showAddClientModal());
        }

        // Add client form
        const addForm = document.getElementById('addClientForm');
        if (addForm) {
            addForm.addEventListener('submit', (e) => this.handleAddClient(e));
        }

        // Edit client form
        const editForm = document.getElementById('editClientForm');
        if (editForm) {
            editForm.addEventListener('submit', (e) => this.handleEditClient(e));
        }

        // Modal close buttons
        document.querySelectorAll('[data-modal-close]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modalId = e.target.getAttribute('data-modal-close');
                this.closeModal(modalId);
            });
        });
    }

    showAddClientModal() {
        document.getElementById('addClientModal').classList.remove('hidden');
        document.getElementById('clientName').focus();
    }

    async handleAddClient(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const clientData = {
            name: formData.get('name'),
            address: formData.get('address'),
            status: formData.get('status') || 'active'
        };

        try {
            await ipcRenderer.invoke('db-add-client', clientData);
            this.closeModal('addClientModal');
            e.target.reset();
            await this.loadClients();
            this.app.loadDashboard(); // Refresh dashboard stats
        } catch (error) {
            console.error('Error adding client:', error);
            alert('Error al agregar cliente');
        }
    }

    async editClient(id) {
        try {
            const client = await ipcRenderer.invoke('db-get-client', id);
            if (client) {
                this.selectedClient = client;
                document.getElementById('editClientId').value = client.id;
                document.getElementById('editClientName').value = client.name;
                document.getElementById('editClientAddress').value = client.address;
                document.getElementById('editClientStatus').value = client.status;
                document.getElementById('editClientModal').classList.remove('hidden');
            }
        } catch (error) {
            console.error('Error loading client:', error);
        }
    }

    async handleEditClient(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const clientData = {
            name: formData.get('name'),
            address: formData.get('address'),
            status: formData.get('status')
        };

        try {
            const clientId = parseInt(formData.get('id'));
            await ipcRenderer.invoke('db-update-client', clientId, clientData);
            this.closeModal('editClientModal');
            await this.loadClients();
            this.app.loadDashboard(); // Refresh dashboard stats
        } catch (error) {
            console.error('Error updating client:', error);
            alert('Error al actualizar cliente');
        }
    }

    async viewClient(id) {
        try {
            const client = await ipcRenderer.invoke('db-get-client', id);
            const payments = await ipcRenderer.invoke('db-get-payments', id);
            
            if (client) {
                this.selectedClient = client;
                this.showClientDetailModal(client, payments);
            }
        } catch (error) {
            console.error('Error loading client details:', error);
        }
    }

    showClientDetailModal(client, payments) {
        const modal = document.getElementById('clientDetailModal');
        
        // Update client info
        document.getElementById('detailClientName').textContent = client.name;
        document.getElementById('detailClientId').textContent = `#${client.id}`;
        document.getElementById('detailClientAddress').textContent = client.address;
        document.getElementById('detailClientStatus').textContent = client.status === 'active' ? 'Activo' : 'Inactivo';

        // Update payments history
        const paymentsContainer = document.getElementById('clientPayments');
        paymentsContainer.innerHTML = '';

        if (payments.length === 0) {
            paymentsContainer.innerHTML = '<p class="text-gray-500 text-center py-4">No hay pagos registrados</p>';
        } else {
            payments.forEach(payment => {
                const paymentDiv = document.createElement('div');
                paymentDiv.className = 'flex justify-between items-center py-2 border-b border-gray-200';
                paymentDiv.innerHTML = `
                    <div>
                        <span class="font-medium">$${payment.amount}</span>
                        <span class="text-sm text-gray-500 ml-2">${new Date(payment.payment_date).toLocaleDateString('es-ES')}</span>
                    </div>
                    <span class="px-2 py-1 text-xs rounded-full ${payment.status === 'paid' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                        ${payment.status === 'paid' ? 'Pagado' : 'Pendiente'}
                    </span>
                `;
                paymentsContainer.appendChild(paymentDiv);
            });
        }

        modal.classList.remove('hidden');
    }

    closeModal(modalId) {
        document.getElementById(modalId).classList.add('hidden');
        this.selectedClient = null;
    }

    async addPayment(clientId, amount, date) {
        try {
            const paymentData = {
                client_id: clientId,
                amount: parseFloat(amount),
                payment_date: date,
                status: 'paid'
            };
            
            await ipcRenderer.invoke('db-add-payment', paymentData);
            await this.loadClients();
            this.app.loadDashboard();
        } catch (error) {
            console.error('Error adding payment:', error);
            throw error;
        }
    }
}

// Initialize clients manager when needed
let clientsManager;

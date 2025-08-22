class CalendarManager {
    constructor(app) {
        this.app = app;
        this.selectedDate = new Date().toISOString().split('T')[0];
        this.payments = [];
    }

    init() {
        this.setupCalendarEvents();
        this.setTodayAsDefault();
        this.loadPaymentsForDate(this.selectedDate);
    }

    setupCalendarEvents() {
        const datePicker = document.getElementById('calendarDatePicker');
        const todayBtn = document.getElementById('todayBtn');

        if (datePicker) {
            datePicker.addEventListener('change', (e) => {
                this.selectedDate = e.target.value;
                this.loadPaymentsForDate(this.selectedDate);
                this.updateSelectedDateDisplay();
            });
        }

        if (todayBtn) {
            todayBtn.addEventListener('click', () => {
                this.setTodayAsDefault();
                this.loadPaymentsForDate(this.selectedDate);
            });
        }
    }

    setTodayAsDefault() {
        const today = new Date().toISOString().split('T')[0];
        this.selectedDate = today;
        
        const datePicker = document.getElementById('calendarDatePicker');
        if (datePicker) {
            datePicker.value = today;
        }
        
        this.updateSelectedDateDisplay();
    }

    updateSelectedDateDisplay() {
        const displayElement = document.getElementById('selectedDateDisplay');
        if (displayElement) {
            const today = new Date().toISOString().split('T')[0];
            if (this.selectedDate === today) {
                displayElement.textContent = 'Hoy';
            } else {
                const date = new Date(this.selectedDate);
                displayElement.textContent = date.toLocaleDateString('es-ES', {
                    weekday: 'short',
                    day: 'numeric',
                    month: 'short'
                });
            }
        }
    }

    async loadPaymentsForDate(date) {
        try {
            this.payments = await ipcRenderer.invoke('db-get-payments-by-date', date);
            this.updateCalendarStats();
            this.renderPaymentsList();
        } catch (error) {
            console.error('Error loading payments for date:', error);
            this.payments = [];
            this.updateCalendarStats();
            this.renderPaymentsList();
        }
    }

    updateCalendarStats() {
        const dailyPaymentsEl = document.getElementById('dailyPayments');
        const dailyTotalEl = document.getElementById('dailyTotal');

        if (dailyPaymentsEl) {
            dailyPaymentsEl.textContent = this.payments.length;
        }

        if (dailyTotalEl) {
            const total = this.payments.reduce((sum, payment) => sum + payment.amount, 0);
            dailyTotalEl.textContent = `$${total.toFixed(2)}`;
        }
    }

    renderPaymentsList() {
        const tbody = document.getElementById('calendarPaymentsBody');
        const noPaymentsMsg = document.getElementById('noPaymentsMessage');
        
        if (!tbody || !noPaymentsMsg) return;

        tbody.innerHTML = '';

        if (this.payments.length === 0) {
            tbody.parentElement.parentElement.classList.add('hidden');
            noPaymentsMsg.classList.remove('hidden');
            return;
        }

        tbody.parentElement.parentElement.classList.remove('hidden');
        noPaymentsMsg.classList.add('hidden');

        this.payments.forEach(payment => {
            const row = document.createElement('tr');
            row.className = 'hover:bg-gray-50';

            const paymentDate = new Date(payment.payment_date);
            const timeString = paymentDate.toLocaleTimeString('es-ES', {
                hour: '2-digit',
                minute: '2-digit'
            });

            const statusBadge = payment.status === 'paid' 
                ? '<span class="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">Pagado</span>'
                : '<span class="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full">Pendiente</span>';

            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">${payment.name}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-500">${payment.address}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">$${payment.amount.toFixed(2)}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-500">${timeString}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    ${statusBadge}
                </td>
            `;

            tbody.appendChild(row);
        });
    }

    // Method to refresh calendar data when called from other parts of the app
    refresh() {
        this.loadPaymentsForDate(this.selectedDate);
    }
}

// Initialize calendar manager when needed
let calendarManager;

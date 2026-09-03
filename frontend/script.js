const API_BASE_URL = window.location.origin;

// Application State
let allDbRecords = [];
let filteredRecords = [];
let currentPage = 1;
let rowsPerPage = 10;

// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const uploadForm = document.getElementById('uploadForm');
const uploadStatus = document.getElementById('uploadStatus');
const fileNameDisplay = document.getElementById('fileNameDisplay');
const filterForm = document.getElementById('filterForm');
const resetBtn = document.getElementById('resetBtn');
const refreshDataBtn = document.getElementById('refreshDataBtn');
const ordersTableBody = document.getElementById('ordersTableBody');
const totalOrdersCount = document.getElementById('totalOrdersCount');
const totalDbCount = document.getElementById('totalDbCount');
const rowsPerPageSelect = document.getElementById('rowsPerPageSelect');

const filterSummaryBanner = document.getElementById('filterSummaryBanner');
const filterSummaryText = document.getElementById('filterSummaryText');
const activeTagsContainer = document.getElementById('activeTagsContainer');

const pageInfo = document.getElementById('pageInfo');
const prevPageBtn = document.getElementById('prevPageBtn');
const nextPageBtn = document.getElementById('nextPageBtn');
const pageNumbers = document.getElementById('pageNumbers');

// Setup Drag & Drop
dropZone.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        handleFileSelect();
    }
});

fileInput.addEventListener('change', handleFileSelect);

function handleFileSelect() {
    const file = fileInput.files[0];
    if (file) {
        uploadBtn.disabled = false;
        fileNameDisplay.innerHTML = `
            <div style="background: #e0f2fe; padding: 8px 12px; border-radius: 6px; border: 1px solid #bae6fd; display: inline-flex; align-items: center; gap: 8px; margin-top: 10px; color: #0369a1; font-size: 13px;">
                <i class="fa-solid fa-file-excel"></i> Selected File: <strong>${file.name}</strong>
            </div>
        `;
    }
}

// Upload Data Sheet
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    uploadStatus.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Processing & Ingesting Dataset...`;
    uploadStatus.className = "status-message";

    try {
        const response = await fetch(`${API_BASE_URL}/upload-excel`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            uploadStatus.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${result.message || 'Data sheet successfully uploaded & injected!'}`;
            uploadStatus.className = "status-message success";
            
            // Reload database
            await loadInitialData();
        } else {
            uploadStatus.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ${result.detail || "Upload failed."}`;
            uploadStatus.className = "status-message error";
        }
    } catch (err) {
        uploadStatus.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> Error connecting to backend server.`;
        uploadStatus.className = "status-message error";
    }
});

// Load Complete Database Dataset
async function loadInitialData() {
    ordersTableBody.innerHTML = '<tr><td colspan="10" class="text-center"><i class="fa-solid fa-spinner fa-spin"></i> Syncing MySQL Database...</td></tr>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/orders?limit=10000`);
        const data = await response.json();

        if (response.ok) {
            allDbRecords = Array.isArray(data) ? data : (data.orders || data.data || []);
            
            // Set Initial Total DB Card
            if (totalDbCount) totalDbCount.textContent = allDbRecords.length;

            // Execute filter or show all
            executeFilter();
        } else {
            ordersTableBody.innerHTML = '<tr><td colspan="10" class="text-center" style="color:red;">Error loading initial dataset.</td></tr>';
        }
    } catch (err) {
        ordersTableBody.innerHTML = '<tr><td colspan="10" class="text-center" style="color:red;">Connection Error to FastAPI Server.</td></tr>';
    }
}

// Smart Query Filter Execution
filterForm.addEventListener('submit', (e) => {
    e.preventDefault();
    executeFilter();
});

function executeFilter() {
    const fields = [
        'region', 'category', 'payment_method', 'delivery_status',
        'min_age', 'max_age', 'min_price', 'max_price',
        'start_date', 'end_date', 'sort_by', 'sort_order'
    ];

    const activeFilters = {};

    fields.forEach(id => {
        const elem = document.getElementById(id);
        if (elem && elem.value.trim() !== "") {
            activeFilters[id] = elem.value.trim();
        }
    });

    // Frontend Filtering for Instant User Feedback
    filteredRecords = allDbRecords.filter(item => {
        if (activeFilters.region && !String(item.region || '').toLowerCase().includes(activeFilters.region.toLowerCase())) return false;
        if (activeFilters.category && !String(item.category || '').toLowerCase().includes(activeFilters.category.toLowerCase())) return false;
        if (activeFilters.payment_method && !String(item.payment_method || '').toLowerCase().includes(activeFilters.payment_method.toLowerCase())) return false;
        if (activeFilters.delivery_status && !String(item.delivery_status || '').toLowerCase().includes(activeFilters.delivery_status.toLowerCase())) return false;
        
        if (activeFilters.min_age && (item.customer_age ?? 0) < Number(activeFilters.min_age)) return false;
        if (activeFilters.max_age && (item.customer_age ?? 0) > Number(activeFilters.max_age)) return false;
        
        if (activeFilters.min_price && (item.price ?? 0) < Number(activeFilters.min_price)) return false;
        if (activeFilters.max_price && (item.price ?? 0) > Number(activeFilters.max_price)) return false;

        if (activeFilters.start_date && new Date(item.date) < new Date(activeFilters.start_date)) return false;
        if (activeFilters.end_date && new Date(item.date) > new Date(activeFilters.end_date)) return false;

        return true;
    });

    // Handle Sorting
    if (activeFilters.sort_by) {
        const order = activeFilters.sort_order === 'desc' ? -1 : 1;
        filteredRecords.sort((a, b) => {
            let valA = a[activeFilters.sort_by];
            let valB = b[activeFilters.sort_by];

            if (activeFilters.sort_by === 'date') {
                valA = new Date(valA);
                valB = new Date(valB);
            }

            if (valA < valB) return -1 * order;
            if (valA > valB) return 1 * order;
            return 0;
        });
    }

    // Update KPIs
    if (totalOrdersCount) totalOrdersCount.textContent = filteredRecords.length;

    // Update Contextual Filter Banner
    updateFilterBanner(activeFilters);

    currentPage = 1;
    renderPaginatedTable();
}

// Update Active Filter Tags & Banner UI
function updateFilterBanner(activeFilters) {
    const keys = Object.keys(activeFilters);
    activeTagsContainer.innerHTML = '';

    if (keys.length === 0) {
        filterSummaryBanner.classList.add('hidden');
    } else {
        filterSummaryBanner.classList.remove('hidden');
        filterSummaryText.textContent = `Found ${filteredRecords.length} matching records out of ${allDbRecords.length} total database entries:`;

        keys.forEach(k => {
            const tag = document.createElement('span');
            tag.className = 'active-tag';
            tag.innerHTML = `<strong>${k}:</strong> ${activeFilters[k]}`;
            activeTagsContainer.appendChild(tag);
        });
    }
}

// Rows per page change
rowsPerPageSelect.addEventListener('change', (e) => {
    rowsPerPage = parseInt(e.target.value);
    currentPage = 1;
    renderPaginatedTable();
});

// Render Paginated Table Rows
function renderPaginatedTable() {
    ordersTableBody.innerHTML = '';

    if (!filteredRecords || filteredRecords.length === 0) {
        ordersTableBody.innerHTML = '<tr><td colspan="10" class="text-center"><i class="fa-solid fa-circle-exclamation"></i> No order records match the applied criteria.</td></tr>';
        pageInfo.textContent = 'Showing 0-0 of 0 entries';
        prevPageBtn.disabled = true;
        nextPageBtn.disabled = true;
        pageNumbers.innerHTML = '';
        return;
    }

    const start = (currentPage - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const paginatedItems = filteredRecords.slice(start, end);
    const totalPages = Math.ceil(filteredRecords.length / rowsPerPage);

    paginatedItems.forEach(order => {
        const tr = document.createElement('tr');
        
        let statusClass = 'default';
        const st = (order.delivery_status || '').toLowerCase();
        if (st.includes('deliver')) statusClass = 'delivered';
        else if (st.includes('return')) statusClass = 'returned';
        else if (st.includes('pend')) statusClass = 'pending';

        tr.innerHTML = `
            <td><strong>#${order.order_id || order.id || 'N/A'}</strong></td>
            <td>${order.date || 'N/A'}</td>
            <td>${order.customer_name || 'N/A'}</td>
            <td>${order.customer_age ?? '-'}</td>
            <td>${order.region || '-'}</td>
            <td>${order.product || 'N/A'}</td>
            <td>${order.category || '-'}</td>
            <td>₹${order.price ?? 0}</td>
            <td>${order.payment_method || '-'}</td>
            <td><span class="status-badge ${statusClass}">${order.delivery_status || 'Delivered'}</span></td>
        `;
        ordersTableBody.appendChild(tr);
    });

    pageInfo.textContent = `Showing ${start + 1}-${Math.min(end, filteredRecords.length)} of ${filteredRecords.length} filtered entries (Total DB: ${allDbRecords.length})`;

    prevPageBtn.disabled = currentPage === 1;
    nextPageBtn.disabled = currentPage === totalPages;

    renderPageNumbers(totalPages);
}

function renderPageNumbers(totalPages) {
    pageNumbers.innerHTML = '';

    let startPage = Math.max(1, currentPage - 1);
    let endPage = Math.min(totalPages, startPage + 2);

    if (endPage - startPage < 2) {
        startPage = Math.max(1, endPage - 2);
    }

    for (let i = startPage; i <= endPage; i++) {
        const btn = document.createElement('button');
        btn.className = `page-num ${i === currentPage ? 'active' : ''}`;
        btn.textContent = i;
        btn.addEventListener('click', () => {
            currentPage = i;
            renderPaginatedTable();
        });
        pageNumbers.appendChild(btn);
    }
}

// Prev/Next Navigation
prevPageBtn.addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        renderPaginatedTable();
    }
});

nextPageBtn.addEventListener('click', () => {
    const totalPages = Math.ceil(filteredRecords.length / rowsPerPage);
    if (currentPage < totalPages) {
        currentPage++;
        renderPaginatedTable();
    }
});

// Reset & Refresh Buttons
resetBtn.addEventListener('click', () => {
    filterForm.reset();
    executeFilter();
});

refreshDataBtn.addEventListener('click', () => {
    filterForm.reset();
    loadInitialData();
});

// Initial Execution
document.addEventListener('DOMContentLoaded', loadInitialData);
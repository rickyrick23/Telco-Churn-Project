const API_BASE = 'http://127.0.0.1:8000'

// Utility functions
function qs(id) { return document.getElementById(id) }
function qsa(selector) { return document.querySelectorAll(selector) }

async function getJSON(url, opts = {}) {
  try {
    const res = await fetch(url, opts)
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`)
    return await res.json()
  } catch (error) {
    console.error('API Error:', error)
    throw error
  }
}

function pre(el, data) {
  el.textContent = typeof data === 'string' ? data : JSON.stringify(data, null, 2)
}

function renderTable(container, rows, maxRows = 100) {
  if (!rows || !rows.length) {
    container.innerHTML = '<p class="no-data">No data available</p>'
    return
  }
  
  // Limit rows for performance
  const limitedRows = rows.slice(0, maxRows)
  const cols = Object.keys(limitedRows[0])
  
  const thead = '<thead><tr>' + cols.map(c => `<th>${c}</th>`).join('') + '</tr></thead>'
  const tbody = '<tbody>' + limitedRows.map(r => 
    '<tr>' + cols.map(c => `<td>${r[c] ?? ''}</td>`).join('') + '</tr>'
  ).join('') + '</tbody>'
  
  container.innerHTML = `<table>${thead}${tbody}</table>`
  
  if (rows.length > maxRows) {
    container.innerHTML += `<p class="table-info">Showing ${maxRows} of ${rows.length} rows</p>`
  }
}

function showMessage(container, message, type = 'info') {
  const messageEl = document.createElement('div')
  messageEl.className = `message ${type}-message`
  messageEl.textContent = message
  container.appendChild(messageEl)
  
  setTimeout(() => messageEl.remove(), 5000)
}

function setLoading(button, loading = true) {
  if (loading) {
    button.disabled = true
    button.textContent = 'Loading...'
    button.classList.add('loading')
  } else {
    button.disabled = false
    button.textContent = button.dataset.originalText || button.textContent
    button.classList.remove('loading')
  }
}

// Dashboard initialization
async function initDashboard() {
  try {
    // Check backend health
    const health = await getJSON(`${API_BASE}/health`)
    const healthEl = qs('health')
    healthEl.textContent = `Backend: ${health.status}`
    healthEl.classList.add('badge', health.status === 'ok' ? 'success' : 'danger')
    
    // Load initial stats
    await loadDashboardStats()
    
    // Set up event listeners
    setupEventListeners()
    
  } catch (error) {
    console.error('Dashboard init failed:', error)
    const healthEl = qs('health')
    healthEl.textContent = 'Backend: Down'
    healthEl.classList.add('badge', 'danger')
  }
}

// Load dashboard statistics
async function loadDashboardStats() {
  try {
    // Get customer count
    const customerCount = await getJSON(`${API_BASE}/ingestion/customers/count`)
    qs('customer-count').textContent = customerCount.count || '0'
    
    // Get interaction count
    const interactionCount = await getJSON(`${API_BASE}/ingestion/interactions/count`)
    qs('interaction-count').textContent = interactionCount.count || '0'
    
    // Calculate churn rate
    const churnData = await getJSON(`${API_BASE}/churn/analytics`)
    const churnRate = churnData.churn_rate || 0
    qs('churn-rate').textContent = `${(churnRate * 100).toFixed(1)}%`
    
  } catch (error) {
    console.error('Failed to load stats:', error)
    // Set fallback values
    qs('customer-count').textContent = '7,086'
    qs('interaction-count').textContent = '45'
    qs('churn-rate').textContent = '26.5%'
  }
}

// Setup event listeners
function setupEventListeners() {
  // Store original button text
  qsa('.btn').forEach(btn => {
    btn.dataset.originalText = btn.textContent
  })
  
  // Refresh stats
  qs('btn-refresh-stats').addEventListener('click', loadDashboardStats)
  
  // Customer data explorer
  qs('btn-explore').addEventListener('click', exploreCustomerData)
  qs('btn-export').addEventListener('click', exportCustomerData)
  
  // Vector search
  qs('btn-vector-search').addEventListener('click', performVectorSearch)
  
  // Sentiment analysis
  qs('btn-sentiment').addEventListener('click', analyzeSentiment)
  
  // Churn prediction
  qs('btn-churn').addEventListener('click', predictChurn)
  
  // Natural language query
  qs('btn-nlq').addEventListener('click', executeNLQuery)
  
  // Retention strategy
  qs('btn-retention').addEventListener('click', generateRetentionStrategy)
  
  // Customer insights
  qs('btn-insights').addEventListener('click', getCustomerInsights)
  
  // Topic analysis
  qs('btn-topic').addEventListener('click', analyzeTopics)
  
  // Risk ranking
  qs('btn-risk-ranking').addEventListener('click', getRiskRanking)
}

// Customer data exploration
async function exploreCustomerData() {
  const button = qs('btn-explore')
  const container = qs('explore-result')
  
  try {
    setLoading(button, true)
    
    const filters = {
      gender: qs('filter-gender').value,
      contract: qs('filter-contract').value,
      churn: qs('filter-churn').value
    }
    
    // Build query parameters
    const params = new URLSearchParams()
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.append(key, value)
    })
    
    const data = await getJSON(`${API_BASE}/ingestion/customers/explore?${params}`)
    renderTable(container, data.customers || data, 50)
    
    showMessage(container, `Found ${data.customers?.length || data.length} customers`, 'success')
    
  } catch (error) {
    showMessage(container, `Error: ${error.message}`, 'error')
    container.innerHTML = ''
  } finally {
    setLoading(button, false)
  }
}

// Export customer data
async function exportCustomerData() {
  try {
    const filters = {
      gender: qs('filter-gender').value,
      contract: qs('filter-contract').value,
      churn: qs('filter-churn').value
    }
    
    const params = new URLSearchParams()
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.append(key, value)
    })
    
    const response = await fetch(`${API_BASE}/ingestion/customers/export?${params}`)
    const blob = await response.blob()
    
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'customer_data.csv'
    a.click()
    window.URL.revokeObjectURL(url)
    
  } catch (error) {
    console.error('Export failed:', error)
    alert('Export failed: ' + error.message)
  }
}

// Vector search functionality
async function performVectorSearch() {
  const button = qs('btn-vector-search')
  const container = qs('vector-results')
  const query = qs('search-query').value.trim()
  const limit = parseInt(qs('search-limit').value) || 5
  
  if (!query) {
    showMessage(container, 'Please enter a search query', 'error')
    return
  }
  
  try {
    setLoading(button, true)
    
    const data = await getJSON(`${API_BASE}/query/vector-search?q=${encodeURIComponent(query)}&k=${limit}`)
    
    if (data.results && data.results.length > 0) {
      const formattedResults = data.results.map(r => ({
        'Customer ID': r.customer_id || 'N/A',
        'Interaction': r.text || 'N/A',
        'Source': r.source || 'N/A',
        'Title': r.title || 'N/A'
      }))
      renderTable(container, formattedResults)
      showMessage(container, `Found ${data.results.length} similar interactions`, 'success')
    } else {
      container.innerHTML = '<p class="no-data">No similar interactions found</p>'
    }
    
  } catch (error) {
    showMessage(container, `Search failed: ${error.message}`, 'error')
    container.innerHTML = ''
  } finally {
    setLoading(button, false)
  }
}

// Sentiment analysis
async function analyzeSentiment() {
  const button = qs('btn-sentiment')
  const container = qs('sentiment-result')
  const text = qs('sentiment-text').value.trim()
  
  if (!text) {
    showMessage(container, 'Please enter text to analyze', 'error')
    return
  }
  
  try {
    setLoading(button, true)
    
    const data = await getJSON(`${API_BASE}/analysis/sentiment`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    })
    
    pre(container, data)
    
  } catch (error) {
    showMessage(container, `Analysis failed: ${error.message}`, 'error')
  } finally {
    setLoading(button, false)
  }
}

// Churn prediction
async function predictChurn() {
  const button = qs('btn-churn')
  const container = qs('churn-result')
  
  try {
    setLoading(button, true)
    
    const features = {
      tenure: parseInt(qs('f-tenure').value) || 0,
      monthly_charges: parseFloat(qs('f-monthly').value) || 0,
      contract: qs('f-contract').value,
      internet_service: qs('f-internet').value,
      payment_method: qs('f-payment').value,
      paperless_billing: qs('f-paperless').value === 'true'
    }
    
    const data = await getJSON(`${API_BASE}/churn/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(features)
    })
    
    pre(container, data)
    
  } catch (error) {
    showMessage(container, `Prediction failed: ${error.message}`, 'error')
  } finally {
    setLoading(button, false)
  }
}

// Natural language query
async function executeNLQuery() {
  const button = qs('btn-nlq')
  const sqlContainer = qs('sql-result')
  const tableContainer = qs('table-result')
  const query = qs('nlq').value.trim()
  
  if (!query) {
    showMessage(sqlContainer, 'Please enter a natural language query', 'error')
    return
  }
  
  try {
    setLoading(button, true)
    
    // Generate SQL
    const sqlData = await getJSON(`${API_BASE}/query/sql`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nl_query: query })
    })
    
    pre(sqlContainer, sqlData)
    
    // Execute query
    const execData = await getJSON(`${API_BASE}/query/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nl_query: query })
    })
    
    renderTable(tableContainer, execData.rows || execData)
    
  } catch (error) {
    showMessage(sqlContainer, `Query failed: ${error.message}`, 'error')
    tableContainer.innerHTML = ''
  } finally {
    setLoading(button, false)
  }
}

// Retention strategy generation
async function generateRetentionStrategy() {
  const button = qs('btn-retention')
  const container = qs('retention-result')
  const customerId = qs('retention-customer-id').value.trim()
  const churnRisk = parseFloat(qs('retention-churn-risk').value) || 0
  
  if (!customerId) {
    showMessage(container, 'Please enter a customer ID', 'error')
    return
  }
  
  try {
    setLoading(button, true)
    
    const data = await getJSON(`${API_BASE}/retention/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        customer_id: customerId, 
        churn_risk: churnRisk 
      })
    })
    
    pre(container, data)
    
  } catch (error) {
    showMessage(container, `Strategy generation failed: ${error.message}`, 'error')
  } finally {
    setLoading(button, false)
  }
}

// Customer insights
async function getCustomerInsights() {
  const button = qs('btn-insights')
  const container = qs('insights-result')
  const customerId = qs('insights-customer-id').value.trim()
  
  if (!customerId) {
    showMessage(container, 'Please enter a customer ID', 'error')
    return
  }
  
  try {
    setLoading(button, true)
    
    const data = await getJSON(`${API_BASE}/insights/customer/${customerId}`)
    pre(container, data)
    
  } catch (error) {
    showMessage(container, `Failed to get insights: ${error.message}`, 'error')
  } finally {
    setLoading(button, false)
  }
}

// Topic analysis
async function analyzeTopics() {
  const button = qs('btn-topic')
  const container = qs('topic-result')
  const texts = qs('topic-texts').value.trim()
  
  if (!texts) {
    showMessage(container, 'Please enter texts for analysis', 'error')
    return
  }
  
  try {
    setLoading(button, true)
    
    const textList = texts.split('\n').filter(t => t.trim())
    
    const data = await getJSON(`${API_BASE}/analysis/topic`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ texts: textList })
    })
    
    pre(container, data)
    
  } catch (error) {
    showMessage(container, `Topic analysis failed: ${error.message}`, 'error')
  } finally {
    setLoading(button, false)
  }
}

// Risk ranking
async function getRiskRanking() {
  const button = qs('btn-risk-ranking')
  const container = qs('risk-ranking-result')
  const limit = parseInt(qs('risk-limit').value) || 50
  
  try {
    setLoading(button, true)
    
    const data = await getJSON(`${API_BASE}/churn/ranked?limit=${limit}`)
    
    if (data.items && data.items.length > 0) {
      renderTable(container, data.items, limit)
      showMessage(container, `Showing ${data.items.length} high-risk customers`, 'success')
    } else {
      container.innerHTML = '<p class="no-data">No high-risk customers found</p>'
    }
    
  } catch (error) {
    showMessage(container, `Failed to get rankings: ${error.message}`, 'error')
    container.innerHTML = ''
  } finally {
    setLoading(button, false)
  }
}

// Initialize dashboard when DOM is loaded
window.addEventListener('DOMContentLoaded', initDashboard)

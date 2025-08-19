# ChurnGuard Pro - AI-Powered Customer Retention Platform

A full-stack machine learning platform for customer churn prediction with RAG capabilities, built with FastAPI, PostgreSQL, and modern web technologies.

**Built with ❤️ by Arjun Yadav, Rohit Mukherjee & Lovneesh Aggarwal**

## 🏗️ Project Structure

```
datascience/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── core/           # Configuration and settings
│   │   ├── db/             # Database models and session
│   │   ├── models/         # SQLAlchemy models
│   │   └── routers/        # API endpoints
│   └── requirements.txt    # Python dependencies
├── frontend/               # Static web dashboard
│   ├── index.html         # Main dashboard
│   ├── styles.css         # Modern CSS styling
│   └── app.js            # Dashboard functionality
├── load_to_datasci.py     # Data loader script
├── *.csv                  # Sample datasets
└── README.md             # This file
```

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Database Setup

```bash
# Create database and tables
python load_to_datasci.py --customers_csv "WA_Fn-UseC_-Telco-Customer-Churn.csv" --interactions_csv "customer_interactions.csv" --database_url "postgresql+psycopg2://postgres:tiger@127.0.0.1:5432/datasci"
```

### 3. Frontend

Open `frontend/index.html` in your browser or serve it with a local server.

## 🎯 Features

### Backend Modules
- **Module 1**: Data Ingestion & Preprocessing
- **Module 2**: Sentiment & Topic Analysis  
- **Module 3**: Churn Prediction Engine
- **Module 4**: Natural Language Query Interface
- **Module 5**: Retention Strategy Generator
- **Module 6**: Multi-Modal Reasoning & Insights
- **Module 7**: Dashboard & Alerts

### Frontend Dashboard
- 📊 Real-time database statistics
- 🔍 Customer data exploration with filters
- 🧠 Vector search (RAG) for interactions
- 📈 Sentiment analysis
- 🎯 Churn prediction with ML models
- 💬 Natural language to SQL queries
- 📤 Data export capabilities
- 🎯 Retention strategy generation
- 🔍 Customer insights & analytics
- 📊 Topic analysis
- 🚨 High-risk customer ranking

## 🛠️ Technology Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, pgvector
- **ML/AI**: Scikit-learn, sentence-transformers, VADER
- **Frontend**: Vanilla JavaScript, CSS3, HTML5
- **Database**: PostgreSQL with vector extensions
- **Vector Search**: Sentence transformers for embeddings

## 📊 Data Models

### Customers Table
- Customer demographics and service details
- Contract information and billing data
- Churn status and risk indicators

### Interactions Table  
- Customer interaction transcripts
- Vector embeddings for semantic search
- Source and timestamp tracking

## 🔌 Complete API Endpoints

### Health & Status
- `GET /health` - Backend health check

### Data Ingestion & Management
- `GET /ingestion/customers/count` - Get total customer count
- `GET /ingestion/interactions/count` - Get total interaction count
- `GET /ingestion/customers/explore` - Explore customers with filters
- `GET /ingestion/customers/export` - Export filtered customers to CSV
- `POST /ingestion/structured/upload` - Upload structured data files
- `POST /ingestion/unstructured/upload` - Upload unstructured data files
- `POST /ingestion/audio/transcripts` - Upload audio transcripts
- `POST /ingestion/documents/csv` - Ingest CSV with vector embeddings

### Analysis & ML
- `POST /analysis/sentiment` - Analyze text sentiment
- `POST /analysis/topic` - Analyze text topics and themes

### Churn Prediction
- `GET /churn/analytics` - Get churn statistics and rates
- `POST /churn/predict` - Predict churn risk for customer
- `GET /churn/ranked` - Get customers ranked by churn risk

### Natural Language & Query
- `POST /query/sql` - Generate SQL from natural language
- `POST /query/execute` - Execute generated SQL queries
- `GET /query/vector-search` - Semantic search using vectors

### Retention & Insights
- `POST /retention/recommend` - Generate retention strategies
- `GET /insights/customer/{customer_id}` - Get customer insights

## 🎨 Dashboard Features

- **Modern UI**: Clean, professional design with animations
- **Responsive**: Works on desktop and mobile devices
- **Real-time**: Live data updates and backend status
- **Interactive**: Filter, search, and explore customer data
- **Export**: Download filtered data as CSV
- **Team Credits**: Built by Arjun Yadav, Rohit Mukherjee & Lovneesh Aggarwal

## 🔧 Configuration

### Environment Variables
```bash
PGUSER=postgres
PGPASSWORD=tiger
PGHOST=localhost
PGPORT=5432
PGDATABASE=datasci
```

### Database Connection
Default connection string: `postgresql+psycopg2://postgres:tiger@127.0.0.1:5432/datasci`

## 📈 Usage Examples

### Vector Search
Search for customer interactions using natural language:
```
"customer complaints about billing"
"technical support issues"
"service quality feedback"
```

### Churn Prediction
Input customer features to predict churn risk:
- Tenure, monthly charges, contract type
- Internet service, payment method
- Paperless billing preferences

### Data Exploration
Filter customers by:
- Gender, contract type, churn status
- Export filtered results to CSV
- View real-time statistics

### Retention Strategies
Generate personalized retention strategies:
- Input customer ID and churn risk
- Get customized offers and scripts
- Campaign recommendations

## 🚨 Troubleshooting

### Common Issues
1. **Backend Connection Failed**: Check if FastAPI is running on port 8000
2. **Database Connection Error**: Verify PostgreSQL credentials and database exists
3. **Vector Search Not Working**: Ensure pgvector extension is installed
4. **Frontend Not Loading**: Check browser console for JavaScript errors

### Debug Mode
Enable detailed logging in the backend:
```bash
uvicorn app.main:app --reload --log-level debug
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs` when backend is running
3. Check browser console for frontend errors
4. Verify database connectivity and permissions

## 🏆 Team

**ChurnGuard Pro** is proudly built by:
- **Arjun Yadav** - Backend Architecture & ML Integration
- **Rohit Mukherjee** - Frontend Development & UI/UX
- **Lovneesh Aggarwal** - Database Design & API Development

---

*Empowering businesses with AI-driven customer retention insights since 2024*

# Saint Record System - Master Development Design Document
**Version**: 3.0
**Last Updated**: 2025-12-09
**Status**: In Development

## 1. Project Overview
**Saint Record System (성도기록부)** is a modern, web-based church management system designed to replace legacy Excel files. It integrates member records and attendance tracking into a unified dashboard, accessible via Streamlit, with Google Sheets acting as the backend database.

### 1.1 Core Objectives
*   **Centralization**: Single source of truth for member data and attendance.
*   **Accessibility**: Web-based access (Streamlit Cloud) without file sharing.
*   **Data Integrity**: Type-safe data entry and atomic ID generation.
*   **Visual Analytics**: Real-time dashboards for church leadership.

### 1.2 Technology Stack
*   **Frontend**: Streamlit (Python Web Framework)
*   **Backend / Database**: Google Sheets (via Google Sheets API)
*   **Server-Side Logic**: Google Apps Script (for atomic ID generation)
*   **Visualization**: Plotly Graph Objects, Custom HTML/CSS
*   **Validation**: Pydantic

---

## 2. System Architecture

### 2.1 Directory Structure
```
g:/내 드라이브/g_dev/#yebom/
├── credentials/                # GCP Service Account Keys (Local Only)
│   └── credentials.json        
├── .streamlit/                 
│   ├── config.toml             # Streamlit Theme Configuration
│   └── secrets.toml            # App Secrets (Database Creds, API URLs)
├── saint-record-system/        
│   ├── app.py                  # Main Dashboard (Home Page)
│   ├── pages/                  # Multipage App Routes
│   │   ├── 1_📋_출석입력.py
│   │   ├── 2_👤_성도관리.py
│   │   ├── 3_👨‍👩‍👧_가정관리.py
│   │   ├── 4_🔍_검색.py
│   │   ├── 5_📊_통계.py
│   │   └── 6_⚙️_설정.py
│   ├── utils/                  # Core Utilities
│   │   ├── apps_script_client.py # Apps Script API Wrapper
│   │   ├── enums.py            # System Constants & Enums
│   │   ├── sheets_api.py       # Google Sheets DAL (Data Access Layer)
│   │   ├── ui.py               # UI Components & CSS System
│   │   └── validators.py       # Pydantic Data Models
│   ├── apps_script/            # Google Apps Script Source
│   │   └── Code.gs             # Backend Logic (ID Generation)
│   └── requirements.txt        # Python Dependencies
└── README_SETUP.md             # Setup Guide
```

### 2.2 Data Flow
1.  **User Action**: User interacts with Streamlit UI (e.g., marks attendance).
2.  **Validation**: `utils.validators` checks data integrity.
3.  **DAL**: `utils.sheets_api` allows access to Google Sheets.
4.  **Backend Logic (Optional)**: If new ID is needed, `AppsScriptClient` calls Google Apps Script.
5.  **Storage**: Data is written to specific Google Sheets (`Members`, `Attendance_202X`).

---

## 3. Database Design (Google Sheets)

The system treats a Google Spreadsheet as a relational database.

### 3.1 Sheet: `Members` (Master Data)
Stores individual member profiles.
*   **Primary Key**: `member_id` (Format: `M10001`)
*   **Columns**:
    *   `member_id`: Unique ID from `_Sequences`
    *   `name`: Full Name
    *   `dept_id`: Foreign Key to `_Departments`
    *   `group_id`: Foreign Key to `_Groups`
    *   `gender`: 'M' or 'F'
    *   `birth_date`: YYYY-MM-DD
    *   `phone`: Contact Number
    *   `status`: `재적`, `전출`, etc. (See `MemberStatus` Enum)
    *   `created_at`, `updated_at`: Timestamps

### 3.2 Sheet: `Attendance_{YEAR}` (Transaction Data)
Stores attendance logs, partitioned by year (e.g., `Attendance_2024`, `Attendance_2025`).
*   **Primary Key**: Composite (`year`, `week_no`, `member_id`) or `attend_id`
*   **Columns**:
    *   `attend_id`: `AT{YEAR}_W{WEEK}_{MEMBER_ID}`
    *   `member_id`: FK to Members
    *   `attend_date`: Date of service (Sunday)
    *   `attend_type`: `1` (Present), `0` (Absent), `2` (Online)
    *   `year`: Integer
    *   `week_no`: Week number (1-53)

### 3.3 Sheet: `_Sequences` (System)
Manages atomic counters to prevent ID collisions.
*   **Columns**:
    *   `seq_name`: `member_id`, `family_id`, `event_id`
    *   `last_value`: Integer (Current max value)
    *   `prefix`: String (e.g., 'M', 'F')
    *   `padding`: Integer (e.g., 5 for `00001`)

### 3.4 Lookup Sheets
*   **`_Departments`**: Church organizational units (e.g., 장년부, 청년부).
*   **`_Groups`**: Small groups/Flocks (e.g., 목장). Link to `dept_id`.

---

## 4. UI Design System (`utils/ui.py`)

A custom design system injected via `st.markdown`.

### 4.1 Color Palette
*   **Background**: `#F8F6F3` (Warm Off-white)
*   **Primary**: `#2C3E50` (Dark Navy)
*   **Secondary**: `#8B7355` (Brown/Gold)
*   **Accent**: `#C9A962` (Gold)
*   **Success**: `#4A9B7F` (Muted Green)

### 4.2 Typography
*   **Main**: `Noto Sans KR` (Google Fonts)
*   **Headings/Numbers**: `Playfair Display` (Serif)

### 4.3 Components
*   **`render_stat_card`**: High-impact KPI card with trend indicators and hover effects.
*   **`render_bar_chart`**: Pure HTML/CSS bar chart for lightweight visualization.
*   **`render_dept_item`**: List item with progress bar for department stats.

---

## 5. Development Details

### 5.1 Configuration (`secrets.toml`)
**Local**: `.streamlit/secrets.toml`
**Prod**: Streamlit Cloud Secrets Manager

```toml
[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----..."
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."

[general]
sheet_name = "성도기록부_시스템"
apps_script_url = "https://script.google.com/macros/s/AKfycb.../exec"
```

### 5.2 ID Generation Logic (`Code.gs`)
To ensure no ID duplicates when multiple users add members simultaneously, we use Google Apps Script's `LockService`.
1.  Acquire Lock (wait up to 30s).
2.  Read `last_value` from `_Sequences`.
3.  Increment and Write `last_value + 1`.
4.  Release Lock.
5.  Return formatted ID (e.g., `M00100`).

### 5.3 Attendance Logic
*   **Upsert Pattern**: When saving attendance for a specific Week & Member list:
    1.  Delete existing records for that Week & Member set.
    2.  Insert new records.
    3.  This prevents duplicates if attendance is modified.

---

## 6. Implementation Status

### 6.1 Completed
*   [x] **Dashboard UI**: Full implementation of `app.py` with custom CSS.
*   [x] **Database Connectivity**: `SheetsAPI` robustly handling read/write.
*   [x] **Backend ID Gens**: Apps Script deployed and connected.
*   [x] **Data Models**: Pydantic models in `validators.py`.

### 6.2 Pending / To-Do
*   [ ] **Page Implementation**:
    *   `1_📋_출석입력.py`: Grid interface for marking attendance.
    *   `2_👤_성도관리.py`: Form for adding/editing members (CRUD).
    *   `3_👨‍👩‍👧_가정관리.py`: Grouping members into families.
    *   `4_🔍_검색.py`: Elastic search-like interface.
    *   `5_📊_통계.py`: Detailed reporting (monthly/yearly).
    *   `6_⚙️_설정.py`: Department/Group management.

---

## 7. Recovery & Continuity
If all chat history is lost:
1.  **Read this document**.
2.  **Verify Environment**: Ensure `secrets.toml` handles the GCP connection.
3.  **Run Locally**: `streamlit run app.py`
4.  **Next Step**: Pick a pending page (e.g., "Attendance Input") and implement using `sheets_api.save_attendance` and `ui.py` components.

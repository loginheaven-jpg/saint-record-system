# Saint Record System - Design Review & Proposals

## 1. Overall Assessment
The draft `saint_record_system_design.md` provides a solid foundation. The architecture (Streamlit + Google Sheets) is appropriate for the current scale (~200 members) and allows for rapid development. The data model is well-normalized, facilitating future migration to PostgreSQL.

However, there are critical areas regarding data integrity and concurrency that need addressing to prevent data corruption during actual usage.

## 2. Critical Improvements

### 2.1 Indempotent Attendance Saving (Critical)
**Issue**: The current design's `save_attendance` function (Section 6.2) uses `appendRow`. If a leader modifies attendance for the same week/group, it will append *duplicate* rows.
**Proposal**: Implement an "Upsert" (Update or Insert) strategy.
- **Option A (Simpler)**: Before saving, delete all existing records for the specific `(year, week_no, member_id in group)` combination, then insert new ones.
- **Option B (Robust)**: Use a unique key column in Sheets (e.g., `AT2025_M0001_W01`) and check existence before appending.
*recommendation*: Use Option A for the MVP as it's easier to implement with `gspread` by batch filtering.

### 2.2 Safe ID Generation
**Issue**: `member_id = f"M{len(all_data) + 1:05d}"` is risky. If the last row is deleted, the ID is reused. If multiple admins add members simultaneously, they might get the same ID.
**Proposal**:
- Create a `_Config` or `_Sequences` sheet to store the `last_member_id` counter.
- Function: Lock sheet -> Read counter -> Increment -> Write counter -> Release Lock -> Return new ID.
- Alternatively, use UUIDs (e.g., `uuid4()`) which are collision-safe without locking, though less readable than `M0001`.
*recommendation*: Stick to readable IDs (`M0001`) but strictly manage the counter in a separate `_Sequences` sheet.

### 2.3 Attendance Codes
**Issue**: `attend_type` mixing '1', '0', 'O' is inconsistent.
**Proposal**: Define a strict Enum in Python and Database.
- **DB (Sheets)**: Store as single characters: 'P' (Present), 'A' (Absent), 'O' (Online).
- **Python**: `Enum AttendType { PRESENT='P', ABSENT='A', ONLINE='O' }`
- **Migration**: 'P' -> `1` (or `status_id`), 'A' -> `0`, 'O' -> `2` in Postgres later.

## 3. Recommended Additions

### 3.1 Authentication
**Issue**: No auth mechanism specified. Anyone with the URL could potentially edit if not secured.
**Proposal**:
- **Phase 1**: Use Streamlit's built-in simple password protection (secrets.toml) or a hardcoded login screen in `app.py` checking against a password in Secrets.
- **Phase 1.5**: Simple "Pin Code" per Mokja if needed, but a single Admin password is likely sufficient for the start.

### 3.2 Data Validation Layer
**Issue**: Direct writes to Sheets can bypass logic.
**Proposal**: Add a `Validator` class in Python that runs before any `sheets_api.save_*` call.
- Check if `member_id` exists.
- Check if `date` is valid.
- Check if `dept_id` matches `group_id`'s parent (integrity check).

## 4. Migration Readiness
To ensure smooth migration to PostgreSQL later:
- **Strict Typing**: Enforce types in the Python model (Pydantic models recommended).
- **No Formulas**: Do not rely on Sheet formulas (like `VLOOKUP` or `QUERY` inside the data sheets) for business logic. Calculate in Python or use `view` sheets only for read-only debugging. The current design's `View_*` sheets are good for transparency but the App should read from raw tables and aggregate in Pandas.

## 5. Next Steps
1. Update `saint_record_system_design.md` with:
   - `_Sequences` sheet definition.
   - Revised `save_attendance` logic (Upsert).
   - `AttendType` Enum definition.
2. Proceed to Implementation Planning.

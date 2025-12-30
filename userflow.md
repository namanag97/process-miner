# User Flow Documentation
## Process Mining & Analytics Platform

This document outlines all customer interactions and user flows in the frontend application.

---

## Table of Contents
1. [Authentication & Onboarding](#1-authentication--onboarding)
2. [Dashboard & Home](#2-dashboard--home)
3. [Event Log Management](#3-event-log-management)
4. [Event Log Upload](#4-event-log-upload)
5. [Process Discovery & Exploration](#5-process-discovery--exploration)
6. [Analytics Workflows](#6-analytics-workflows)
7. [AI & Machine Learning Features](#7-ai--machine-learning-features)
8. [User Settings & Account Management](#8-user-settings--account-management)
9. [Notifications Management](#9-notifications-management)
10. [Activity Log & Audit Trail](#10-activity-log--audit-trail)
11. [Help Center](#11-help-center)

---

## 1. Authentication & Onboarding

### 1.1 Login Flow

**Entry Point**: Application start or unauthenticated access to protected routes

**User Flow**:
1. User navigates to `/login`
2. **System displays**: Login form with email and password fields
3. **User action**: Enter email address
4. **User action**: Enter password
5. **User action**: Click "Sign In" button
   - **System response**: Show loading state on button
   - **System response**: Validate credentials (mock auth accepts any credentials)
   - **System response**: Store user session in localStorage
   - **System response**: Redirect to `/home`

**Alternative Path - Guest Login**:
1. User navigates to `/login`
2. **User action**: Click "Continue as Guest" button
   - **System response**: Create guest user session
   - **System response**: Redirect to `/home`

**Exit Points**:
- Success: Navigate to `/home` (Dashboard)
- Protected routes redirect here if not authenticated

---

## 2. Dashboard & Home

### 2.1 Home Page Overview

**Entry Point**: `/home` (default landing after login)

**System displays**:
- Summary metrics cards:
  - Total event logs count
  - Total cases count
  - Last activity timestamp
- Recent event logs list (latest uploads)
- Quick action buttons

**User Interactions**:

1. **View Recent Event Log**
   - **User action**: Click "View" button on any recent log
   - **System response**: Navigate to `/processes/:id`

2. **Upload New Event Log**
   - **User action**: Click "Upload Event Log" button
   - **System response**: Navigate to `/processes/upload`

3. **Explore Processes**
   - **User action**: Click "Explore Processes" button
   - **System response**: Navigate to `/explorer`

4. **Open Settings**
   - **User action**: Click "Settings" button
   - **System response**: Navigate to `/settings/profile`

**Navigation**:
- Sidebar navigation available to all main sections
- Active section highlighted in sidebar

---

## 3. Event Log Management

### 3.1 View Event Logs

**Entry Point**: `/processes` (via sidebar navigation or quick actions)

**System displays**:
- Table with all uploaded event logs
- Columns: Name, Cases, Events, Uploaded date, Actions
- Search bar
- Upload File button

**User Interactions**:

1. **Search Event Logs**
   - **User action**: Type in search field
   - **System response**: Filter table by log name in real-time
   - **User action**: Click clear button (X)
   - **System response**: Reset search filter

2. **Sort Event Logs**
   - **User action**: Click column header (Name, Cases, Events, Date)
   - **System response**: Sort table by selected column (ascending/descending)

3. **View Event Log Details**
   - **User action**: Click on any table row OR click actions dropdown > "View log"
   - **System response**: Navigate to `/processes/:id`

4. **Delete Event Log**
   - **User action**: Click actions dropdown > "Delete log"
   - **System response**: Show confirmation modal
   - **User action**: Confirm deletion
   - **System response**: Delete log from system
   - **System response**: Refresh table, show success toast

5. **Download Event Log** (Coming Soon)
   - **User action**: Click actions dropdown > "Download"
   - **System response**: Show "Feature coming soon" message

6. **Navigate to Upload**
   - **User action**: Click "Upload File" button
   - **System response**: Navigate to `/processes/upload`

**Empty State**:
- If no logs exist: Display "Upload File" action button

---

### 3.2 Event Log Details

**Entry Point**: `/processes/:id`

**System displays**:
- Log name in header
- Tab navigation: Overview, Statistics
- Action buttons: "Explore Process", Actions dropdown

**Tab 1: Overview**

**System displays**:
- Key metrics cards:
  - Total cases
  - Total events
  - Unique activities
  - Unique variants
- Log details card:
  - Source file name
  - Upload date
  - Date range of data
  - Average case duration
  - Source format (CSV/XES)

**User Interactions**:

1. **Explore Process**
   - **User action**: Click "Explore Process" button
   - **System response**: Navigate to `/explorer/:id`

2. **Export Log**
   - **User action**: Click Actions dropdown > "Export log"
   - **System response**: Initiate export process

3. **Open in Explorer**
   - **User action**: Click Actions dropdown > "Open in explorer"
   - **System response**: Navigate to `/explorer/:id`

4. **Delete Log**
   - **User action**: Click Actions dropdown > "Delete log"
   - **System response**: Show confirmation modal
   - **User action**: Confirm deletion
   - **System response**: Delete log, navigate back to `/processes`

**Tab 2: Statistics**

**System displays**:
- Activities list table (activity names and counts)
- Quick action buttons

**User Interactions**:

1. **Open Process Explorer**
   - **User action**: Click "Open Process Explorer" button
   - **System response**: Navigate to `/explorer/:id`

2. **View Analytics**
   - **User action**: Click "View Analytics" button
   - **System response**: Navigate to `/analytics` with selected log

---

## 4. Event Log Upload

### 4.1 Upload Wizard (4-Step Process)

**Entry Point**: `/processes/upload`

**System displays**: Multi-step wizard interface

---

#### Step 1: Select File

**System displays**:
- Drag & drop upload area
- File browse button
- Supported formats: .csv, .xes
- Max file size: 100MB

**User Interactions**:

1. **Select File via Drag & Drop**
   - **User action**: Drag file and drop into upload area
   - **System response**: Validate file type and size
   - **System response**: If valid, show file name and proceed to Step 2
   - **System response**: If invalid, show error message

2. **Select File via Browse**
   - **User action**: Click "Browse" button
   - **System response**: Open file picker dialog
   - **User action**: Select file
   - **System response**: Validate file type and size
   - **System response**: If valid, proceed to Step 2

3. **Cancel Upload**
   - **User action**: Click "Cancel" button
   - **System response**: Navigate back to `/processes`

---

#### Step 2: Validate

**System displays**:
- File name confirmation
- Detected columns list
- Sample data preview (first 5 rows in table format)
- Auto-detected column names

**User Interactions**:

1. **Review Data**
   - **User action**: Scroll through sample data preview
   - **System response**: Display preview table with detected columns

2. **Proceed to Configuration**
   - **User action**: Click "Next" button
   - **System response**: Navigate to Step 3

3. **Go Back**
   - **User action**: Click "Back" button
   - **System response**: Return to Step 1 (file selection)

4. **Cancel Upload**
   - **User action**: Click "Cancel" button
   - **System response**: Navigate back to `/processes`

---

#### Step 3: Configure Mapping

**System displays**:
- Column mapping form with dropdowns
- Pre-populated suggestions based on auto-detection

**Required Mappings**:
- Case ID (dropdown)
- Activity (dropdown)
- Timestamp (dropdown)

**Optional Mappings**:
- Resource (dropdown)

**User Interactions**:

1. **Map Case ID Column**
   - **User action**: Select column from Case ID dropdown
   - **System response**: Update mapping, enable/disable Next button

2. **Map Activity Column**
   - **User action**: Select column from Activity dropdown
   - **System response**: Update mapping, enable/disable Next button

3. **Map Timestamp Column**
   - **User action**: Select column from Timestamp dropdown
   - **System response**: Update mapping, enable/disable Next button

4. **Map Resource Column (Optional)**
   - **User action**: Select column from Resource dropdown
   - **System response**: Update mapping

5. **Proceed to Processing**
   - **User action**: Click "Next" button (enabled only when required fields mapped)
   - **System response**: Navigate to Step 4, start processing

6. **Go Back**
   - **User action**: Click "Back" button
   - **System response**: Return to Step 2

7. **Cancel Upload**
   - **User action**: Click "Cancel" button
   - **System response**: Navigate back to `/processes`

---

#### Step 4: Process/Complete

**System displays**:
- Progress indicator
- Processing status message

**Automatic System Actions**:
- Upload file to backend
- Process and ingest data
- Create event log entry

**Success State**:

**System displays**:
- Success message with checkmark
- Created log details

**User Interactions**:

1. **View Uploaded Event Log**
   - **User action**: Click "View Event Log" button
   - **System response**: Navigate to `/processes/:id`

2. **Upload Another File**
   - **User action**: Click "Upload Another" button
   - **System response**: Reset wizard, return to Step 1

**Error State**:

**System displays**:
- Error message
- Error details

**User Interactions**:

1. **Retry Upload**
   - **User action**: Click "Retry" button
   - **System response**: Attempt processing again

2. **Cancel**
   - **User action**: Click "Cancel" button
   - **System response**: Navigate back to `/processes`

---

## 5. Process Discovery & Exploration

### 5.1 Select Log for Exploration

**Entry Point**: `/explorer`

**System displays**:
- List of available event logs
- Selection interface

**User Interactions**:

1. **Select Event Log**
   - **User action**: Click on event log card
   - **System response**: Navigate to `/explorer/:logId`

---

### 5.2 Process Explorer Interface

**Entry Point**: `/explorer/:logId`

**System displays**:
- Toolbar with breadcrumb navigation
- KPI metrics bar
- Interactive process graph (DFG - Directly Follows Graph)
- Right panel with 3 tabs: Variants, Activity Details, Transition Details
- Applied filters bar (if any filters active)

---

#### 5.2.1 KPI Metrics Bar

**System displays**:
- Total cases count
- Unique variants count
- Unique activities count
- Average throughput time
- Happy path percentage
- Rework rate percentage

---

#### 5.2.2 Process Graph Interactions

**User Interactions**:

1. **Select Activity Node**
   - **User action**: Click on activity node
   - **System response**: Highlight node
   - **System response**: Switch to "Activity Details" tab in right panel
   - **System response**: Display activity metrics and details
   - **User action**: Click again to deselect
   - **System response**: Clear selection, return to previous tab

2. **Select Transition/Edge**
   - **User action**: Click on edge between two activities
   - **System response**: Highlight edge
   - **System response**: Switch to "Transition Details" tab in right panel
   - **System response**: Display transition frequency and performance
   - **User action**: Click again to deselect
   - **System response**: Clear selection

3. **View Process Flow**
   - Visual representation of activities and their relationships
   - Thickness of edges indicates frequency
   - Color coding for performance metrics

---

#### 5.2.3 Variants Panel (Tab 1)

**System displays**:
- Search bar
- Sort dropdown
- List of process variants with metrics

**User Interactions**:

1. **Search Variants**
   - **User action**: Type in search field
   - **System response**: Filter variants by activity name

2. **Sort Variants**
   - **User action**: Click sort dropdown
   - **User action**: Select sort criteria:
     - By frequency
     - By duration
     - By complexity
     - By activity count
   - **System response**: Reorder variant list

3. **View Variant Details**
   - **System displays** for each variant:
     - Rank badge
     - Case count
     - Frequency percentage with progress bar
     - Mini process path visualization
     - Duration metric
     - Activity count
     - Complexity score
     - Rework indicator (if applicable)
     - Happy path badge (if applicable)

4. **Select Variant for Filtering**
   - **User action**: Click on variant card
   - **System response**: Highlight variant
   - **System response**: Show "Filter" button
   - **User action**: Click "Filter" button
   - **System response**: Apply filter to show only cases following this variant
   - **System response**: Update graph to highlight variant path
   - **System response**: Add filter tag to Applied Filters bar

5. **Compare Variants**
   - **User action**: Toggle compare mode switch
   - **System response**: Enable multi-select mode
   - **User action**: Select 2-3 variants
   - **System response**: Enable "Compare" button
   - **User action**: Click "Compare" button
   - **System response**: Display comparison view (side-by-side metrics)

---

#### 5.2.4 Activity Details Panel (Tab 2)

**Triggered by**: Clicking on activity node in graph

**System displays**:
- Activity name
- Total occurrences
- Case percentage
- Duration statistics (min, avg, max)
- Associated resources

**User Interactions**:

1. **Filter Cases With Activity**
   - **User action**: Click "Filter with this activity" button
   - **System response**: Apply filter to show only cases containing this activity
   - **System response**: Update graph visualization
   - **System response**: Add filter tag to Applied Filters bar

2. **Filter Cases Without Activity**
   - **User action**: Click "Filter without this activity" button
   - **System response**: Apply filter to exclude cases with this activity
   - **System response**: Update graph visualization
   - **System response**: Add filter tag to Applied Filters bar

---

#### 5.2.5 Transition Details Panel (Tab 3)

**Triggered by**: Clicking on edge in graph

**System displays**:
- Source activity name
- Target activity name
- Frequency count
- Performance metrics (average duration)

---

#### 5.2.6 Filtering System

**Entry Point**: Click "Filters" button in toolbar

**System displays**: Filter drawer with multiple filter sections

---

**Filter 1: Activity Occurrence**

**User Interactions**:

1. **Set Filter Type**
   - **User action**: Select radio option: "Cases With" or "Cases Without"
   - **System response**: Update filter mode

2. **Select Activities**
   - **User action**: Open multi-select dropdown
   - **User action**: Select one or more activities
   - **System response**: Update selection

3. **Apply Filter**
   - **User action**: Click "Apply Filter" button
   - **System response**: Filter graph to show matching cases
   - **System response**: Add filter tag to Applied Filters bar
   - **System response**: Close filter drawer

---

**Filter 2: Activity Sequence**

**User Interactions**:

1. **Set Sequence Type**
   - **User action**: Select radio option: "Directly Follows" or "Eventually Follows"
   - **System response**: Update filter mode

2. **Select Source Activity**
   - **User action**: Select from dropdown
   - **System response**: Update filter criteria

3. **Select Target Activity**
   - **User action**: Select from dropdown
   - **System response**: Update filter criteria

4. **Apply Filter**
   - **User action**: Click "Apply Filter" button
   - **System response**: Filter graph to show matching sequence patterns
   - **System response**: Add filter tag to Applied Filters bar

---

**Filter 3: Duration**

**User Interactions**:

1. **Set Time Unit**
   - **User action**: Select radio option: "Hours" or "Days"
   - **System response**: Update duration unit

2. **Set Minimum Duration**
   - **User action**: Enter number in min duration field
   - **System response**: Validate input

3. **Set Maximum Duration**
   - **User action**: Enter number in max duration field
   - **System response**: Validate input

4. **Apply Filter**
   - **User action**: Click "Apply Duration Filter" button
   - **System response**: Filter graph to show cases within duration range
   - **System response**: Add filter tag to Applied Filters bar
   - **System displays**: Average and p90 statistics

---

**Filter 4: Time Range**

**User Interactions**:

1. **Select Date Range**
   - **User action**: Click date range picker
   - **User action**: Select start date
   - **User action**: Select end date
   - **System response**: Update date range

2. **Apply Filter**
   - **User action**: Click "Apply Time Filter" button
   - **System response**: Filter graph to show cases in date range
   - **System response**: Add filter tag to Applied Filters bar

---

**Filter 5: Resource**

**User Interactions**:

1. **Select Resources**
   - **User action**: Open multi-select dropdown
   - **User action**: Select one or more resources
   - **System response**: Update selection

2. **Apply Filter**
   - **User action**: Click "Apply Resource Filter" button
   - **System response**: Filter graph to show cases with selected resources
   - **System response**: Add filter tag to Applied Filters bar

---

**Filter 6: Rework/Loops**

**User Interactions**:

1. **Select Activity (Optional)**
   - **User action**: Select activity from dropdown
   - **System response**: Update filter criteria (if blank, searches all activities)

2. **Set Minimum Repetitions**
   - **User action**: Enter number (2-10)
   - **System response**: Validate input

3. **Apply Filter**
   - **User action**: Click "Find Rework" button
   - **System response**: Identify and filter cases with rework patterns
   - **System response**: Add filter tag to Applied Filters bar

---

#### 5.2.7 Managing Applied Filters

**System displays**: Applied Filters bar with filter tags

**User Interactions**:

1. **Remove Individual Filter**
   - **User action**: Click X on filter tag
   - **System response**: Remove that filter
   - **System response**: Refresh graph visualization

2. **Clear All Filters**
   - **User action**: Click "Clear all" link
   - **System response**: Remove all active filters
   - **System response**: Reset graph to original state

---

#### 5.2.8 Toolbar Actions

**User Interactions**:

1. **Navigate Back**
   - **User action**: Click "Back" button
   - **System response**: Return to `/explorer`

2. **Export Visualization**
   - **User action**: Click "Export SVG" button
   - **System response**: Download process graph as SVG file (coming soon)

3. **Toggle Side Panel**
   - **User action**: Click panel expand/collapse toggle
   - **System response**: Show/hide right panel for larger graph view

---

## 6. Analytics Workflows

### 6.1 Analytics Overview

**Entry Point**: `/analytics`

**System displays**:
- Process log selector dropdown
- Summary metrics cards
- Tab navigation: Performance, Conformance, Rework Analysis

---

#### 6.1.1 Process Log Selection

**User Interactions**:

1. **Select Process Log**
   - **User action**: Click log selector dropdown
   - **User action**: Select event log
   - **System response**: Load analytics for selected log
   - **System response**: Refresh all metrics and charts

---

#### 6.1.2 Summary Metrics

**System displays**:
- Average cycle time (days)
- Throughput (cases/day)
- Rework rate (%)
- Number of bottlenecks

---

### 6.2 Performance Tab

**Entry Point**: `/analytics/performance` (default tab)

**System displays**:
- Bottleneck Analysis table
- Cycle Time Distribution card
- Throughput Metrics card

---

**Section 1: Bottleneck Analysis**

**System displays**:
- Table with columns: Rank, Activity, Avg Wait Time, Impact Score
- Color-coded impact progress bars (red/orange/yellow/green)
- Sortable by any column

**User Interactions**:

1. **Sort Bottlenecks**
   - **User action**: Click column header
   - **System response**: Sort table by selected column

2. **Review Activity Details**
   - **User action**: Click on activity row
   - **System response**: Display detailed bottleneck information

---

**Section 2: Cycle Time Distribution**

**System displays**:
- Minimum cycle time
- Median cycle time
- Average cycle time
- 75th percentile
- Maximum cycle time

---

**Section 3: Throughput Metrics**

**System displays**:
- Cases per day
- Cases per week
- Cases per month

---

### 6.3 Conformance Tab

**Entry Point**: `/analytics/conformance`

**System displays**:
- Conformance checking metrics
- Compliance analysis
- Deviation patterns

**User Interactions**:
- Review conformance reports
- Analyze deviation patterns

---

### 6.4 Rework Analysis Tab

**Entry Point**: `/analytics/rework`

**System displays**:
- Rework pattern analysis
- Activity repetition metrics
- Rework impact on performance

**User Interactions**:
- Review rework patterns
- Identify improvement opportunities

---

## 7. AI & Machine Learning Features

### 7.1 AI Hub

**Entry Point**: `/ai`

**System displays**:
- Overview of AI features
- Quick links to Insights and Predictions

**User Interactions**:

1. **Navigate to Insights**
   - **User action**: Click "AI Insights" link
   - **System response**: Navigate to `/ai/insights`

2. **Navigate to Predictions**
   - **User action**: Click "Predictions" link
   - **System response**: Navigate to `/ai/predictions`

---

### 7.2 AI Insights

**Entry Point**: `/ai/insights`

**System displays**:
- Log selector dropdown
- Summary statistics (total insights, high priority, patterns, anomalies)
- Natural language query interface
- Insights organized in collapsible sections

---

#### 7.2.1 Log Selection

**User Interactions**:

1. **Select Log to Analyze**
   - **User action**: Click log selector dropdown
   - **User action**: Select event log
   - **System response**: Load AI insights for selected log
   - **System response**: Refresh all insight sections

---

#### 7.2.2 Natural Language Query

**User Interactions**:

1. **Ask Question About Process**
   - **User action**: Type question in text input (e.g., "What are the main bottlenecks?")
   - **User action**: Click "Send" button or press Enter
   - **System response**: Process natural language query
   - **System response**: Generate and display relevant insights

---

#### 7.2.3 View Insights

**System displays** three collapsible sections:

**Performance Insights Section**

**System displays**:
- Insight cards with:
  - Severity level badge (high/medium/warning/info)
  - Icon and title
  - Type tag (e.g., "Performance", "Bottleneck")
  - Description text
  - Impact information
  - Recommendation box

**User Interactions**:

1. **Expand/Collapse Section**
   - **User action**: Click section header
   - **System response**: Show/hide insight cards

2. **Review Recommendations**
   - **User action**: Read recommendation text
   - **User action**: Click action link (if provided)
   - **System response**: Navigate to relevant feature (e.g., Process Explorer with filters)

---

**Pattern Insights Section**

**System displays**:
- Similar insight cards for discovered patterns
- Frequent pattern highlights
- Rework rate information

**User Interactions**: Same as Performance Insights

---

**Anomalies Section**

**System displays**:
- Unusual activity sequence warnings
- Process violation indicators
- Outlier detection results

**User Interactions**: Same as Performance Insights

---

### 7.3 Predictions Management

**Entry Point**: `/ai/predictions`

**System displays**:
- "Train New Predictor" button
- Predictor table with columns: Name, Type, Event Log, Accuracy, Status, Predictions, Actions
- Pagination controls

---

#### 7.3.1 Train New Predictor

**User Interactions**:

1. **Open Training Modal**
   - **User action**: Click "Train New Predictor" button
   - **System response**: Display predictor training modal

2. **Configure Predictor**
   - **User action**: Enter predictor name
   - **User action**: Select event log from dropdown
   - **User action**: Select prediction type:
     - Next activity prediction
     - Remaining time prediction
     - Outcome prediction
   - **System response**: Validate inputs, enable/disable "Start Training" button

3. **Start Training**
   - **User action**: Click "Start Training" button
   - **System response**: Close modal
   - **System response**: Add new predictor row to table with "Training" status
   - **System response**: Show progress indicator
   - **System response**: Disable actions while training

4. **Training Complete**
   - **System response**: Update status to "Ready" with checkmark
   - **System response**: Display accuracy percentage
   - **System response**: Enable "View" and "Delete" actions

5. **Training Failed**
   - **System response**: Update status to "Failed" with error icon
   - **System response**: Enable "Delete" action
   - **User action**: Click "Delete" to remove failed predictor

---

#### 7.3.2 Manage Predictors

**User Interactions**:

1. **View Predictor Details**
   - **User action**: Click "View" button on predictor row
   - **System response**: Navigate to `/ai/predictions/:id`

2. **Delete Predictor**
   - **User action**: Click "Delete" button
   - **System response**: Show confirmation modal
   - **User action**: Confirm deletion
   - **System response**: Remove predictor from table
   - **System response**: Show success toast

3. **Sort Predictors**
   - **User action**: Click column header
   - **System response**: Sort table by selected column

4. **Navigate Pages**
   - **User action**: Click pagination controls
   - **System response**: Load next/previous page of predictors

---

### 7.4 Predictor Details

**Entry Point**: `/ai/predictions/:id`

**System displays**:
- Predictor performance metrics
- Prediction results
- Model evaluation charts

**User Interactions**:
- Review prediction accuracy
- Analyze model performance
- Export predictions

---

## 8. User Settings & Account Management

### 8.1 Settings Overview

**Entry Point**: `/settings/profile` (default tab)

**System displays**:
- Tab navigation: Profile, Preferences, Notifications
- Tab-specific content
- Save/Cancel buttons

---

### 8.2 Profile Tab

**Entry Point**: `/settings/profile`

**System displays**:
- User avatar with background color
- "Change photo" button
- Full name input field
- Email display (read-only)
- Cancel and Save Changes buttons

**User Interactions**:

1. **Change Profile Photo**
   - **User action**: Click "Change photo" button
   - **System response**: Open file picker (mock implementation)

2. **Edit Full Name**
   - **User action**: Click in full name field
   - **User action**: Type new name
   - **System response**: Enable Save Changes button

3. **Save Profile Changes**
   - **User action**: Click "Save Changes" button
   - **System response**: Show loading state on button
   - **System response**: Save changes
   - **System response**: Show success toast "Profile updated successfully"
   - **System response**: Disable Save Changes button

4. **Cancel Changes**
   - **User action**: Click "Cancel" button
   - **System response**: Revert all changes to original values
   - **System response**: Disable Save Changes button

---

### 8.3 Preferences Tab

**Entry Point**: `/settings/preferences`

**System displays**:
- Display Settings card
- Data & Privacy card
- Save/Cancel buttons

---

**Display Settings**

**User Interactions**:

1. **Change Theme**
   - **User action**: Click theme selector dropdown
   - **User action**: Select option:
     - Light
     - Dark
     - System default
   - **System response**: Update theme preference
   - **System response**: Enable Save Changes button

2. **Change Date Format**
   - **User action**: Click date format selector
   - **User action**: Select format (e.g., MM/DD/YYYY, DD/MM/YYYY, YYYY-MM-DD)
   - **System response**: Update date format preference
   - **System response**: Enable Save Changes button

3. **Change Timezone**
   - **User action**: Click timezone selector (searchable)
   - **User action**: Search for timezone
   - **User action**: Select timezone
   - **System response**: Update timezone preference
   - **System response**: Enable Save Changes button

---

**Data & Privacy Settings**

**User Interactions**:

1. **Toggle Usage Data Sharing**
   - **User action**: Click "Share anonymous usage data" toggle
   - **System response**: Toggle setting on/off
   - **System response**: Enable Save Changes button

2. **Toggle Keyboard Shortcuts**
   - **User action**: Click "Enable keyboard shortcuts" toggle
   - **System response**: Toggle setting on/off
   - **System response**: Enable Save Changes button

---

**Save Preferences**

**User Interactions**:

1. **Save All Preferences**
   - **User action**: Click "Save Changes" button
   - **System response**: Show loading state
   - **System response**: Save all preference changes
   - **System response**: Show success toast
   - **System response**: Disable Save Changes button

2. **Cancel Changes**
   - **User action**: Click "Cancel" button
   - **System response**: Revert all changes
   - **System response**: Disable Save Changes button

---

### 8.4 Notifications Tab

**Entry Point**: `/settings/notifications`

**System displays**:
- Notification preference settings
- Toggle switches for different notification types

**User Interactions**:
- Configure notification preferences
- Save changes

---

## 9. Notifications Management

### 9.1 Notifications Center

**Entry Point**: `/notifications` (via sidebar navigation)

**System displays**:
- Tab navigation: "All" and "Unread" (with badge count)
- "Mark all as read" button (when unread exist)
- List of notifications

---

#### 9.1.1 Tab Navigation

**User Interactions**:

1. **View All Notifications**
   - **User action**: Click "All" tab
   - **System response**: Display all notifications (read and unread)

2. **View Unread Notifications**
   - **User action**: Click "Unread" tab (shows badge with unread count)
   - **System response**: Display only unread notifications

---

#### 9.1.2 Notification List

**System displays** for each notification:
- Unread indicator (blue dot)
- Icon based on type (success, info, warning, error)
- Title (bold if unread)
- Description (truncated to 2 lines)
- Relative timestamp (e.g., "2h ago", "1d ago")

**User Interactions**:

1. **Mark Single Notification as Read**
   - **User action**: Click on notification item
   - **System response**: Remove unread indicator (blue dot)
   - **System response**: Change title from bold to regular
   - **System response**: Decrement unread count in badge
   - **System response**: If in "Unread" tab, remove from view

2. **Mark All as Read**
   - **User action**: Click "Mark all as read" button
   - **System response**: Mark all notifications as read
   - **System response**: Remove all unread indicators
   - **System response**: Reset unread badge to 0
   - **System response**: If in "Unread" tab, clear the list

---

#### 9.1.3 Empty States

**No Notifications**:
- **System displays**: "No notifications" message

**No Unread Notifications**:
- **System displays**: "No unread notifications" message

---

## 10. Activity Log & Audit Trail

### 10.1 Activity Log

**Entry Point**: `/activity`

**System displays**:
- Filter controls (date range, action type)
- "Export" button
- Activity table
- Pagination controls
- Total activity count

---

#### 10.1.1 Filter Activities

**User Interactions**:

1. **Filter by Date Range**
   - **User action**: Click date range selector
   - **User action**: Select option:
     - Last 7 days
     - Last 30 days
     - Last 90 days
     - All time
   - **System response**: Filter activity table by date range

2. **Filter by Action Type**
   - **User action**: Click action type filter
   - **User action**: Select option:
     - All actions
     - Upload
     - View
     - Settings
     - Login
     - Delete
     - Export
   - **System response**: Filter activity table by action type

3. **Combine Filters**
   - Both filters work together
   - **System response**: Apply both date range and action type filters

---

#### 10.1.2 Activity Table

**System displays**:
- Columns: Action (color-coded tag), Description, Date (relative time)
- Sortable columns
- Pagination

**User Interactions**:

1. **Sort Activities**
   - **User action**: Click column header
   - **System response**: Sort table by selected column

2. **Navigate Pages**
   - **User action**: Click pagination controls
   - **System response**: Load next/previous page of activities

3. **Export Activity Log**
   - **User action**: Click "Export" button
   - **System response**: Download activity log as file (CSV/Excel)

---

## 11. Help Center

### 11.1 Help Center

**Entry Point**: `/help`

**System displays**:
- Getting started documentation
- FAQs
- Feature guides
- Support resources

**User Interactions**:
- Browse documentation
- Search for help topics
- Access support resources

---

## 12. Global Navigation & Actions

### 12.1 Sidebar Navigation

**Always Available** (except on login page)

**Navigation Items**:
- Home → `/home`
- Processes (Event Logs) → `/processes`
- Explorer (Process Explorer) → `/explorer`
- Analytics → `/analytics`
- AI/Insights → `/ai/insights`
- Predictions → `/ai/predictions`
- Settings → `/settings/profile`
- Help → `/help`
- Notifications (with unread badge) → `/notifications`
- Activity Log → `/activity`

**User Interactions**:

1. **Navigate to Section**
   - **User action**: Click sidebar navigation item
   - **System response**: Navigate to selected route
   - **System response**: Highlight active navigation item

2. **View Unread Notifications Count**
   - **System displays**: Badge with unread count on Notifications item
   - Updates in real-time as notifications are marked read

---

### 12.2 User Account Menu

**User Interactions**:

1. **Open Account Menu**
   - **User action**: Click user avatar/name in header
   - **System response**: Display dropdown menu

2. **Logout**
   - **User action**: Click "Logout" from dropdown
   - **System response**: Clear user session from localStorage
   - **System response**: Navigate to `/login`

---

## 13. Cross-Cutting Interactions

### 13.1 Loading States

**System behavior** throughout the application:
- Display skeleton loaders while fetching data
- Show spinner overlays during operations
- Disable buttons with loading state during submission
- Display progress bars for long-running tasks

---

### 13.2 Error Handling

**System behavior** throughout the application:
- Display error alerts/messages when operations fail
- Show toast notifications for errors
- Provide retry buttons on error states
- Display fallback empty states when data fails to load

---

### 13.3 Success Feedback

**System behavior** throughout the application:
- Show toast notifications for successful operations
- Display success states in modals/wizards
- Update UI optimistically where appropriate
- Provide confirmation messages for critical actions

---

### 13.4 Responsive Behaviors

**System behavior**:
- Adapt layouts for different screen sizes
- Collapse/expand panels for optimal viewing
- Adjust table displays for mobile views
- Provide mobile-friendly navigation

---

## Summary

This document covers all major user flows and interactions in the Process Mining & Analytics Platform frontend, including:

- **7 major feature areas** with detailed user interactions
- **50+ distinct user actions** across the application
- **4-step upload wizard** with validation and configuration
- **Comprehensive filtering system** with 6 filter types
- **Interactive process visualization** with graph exploration
- **AI-powered features** including insights and predictions
- **Complete account management** with settings and preferences
- **Notification and activity tracking** systems

Each flow documents entry points, user actions, system responses, decision points, and exit points to provide a complete understanding of customer interactions.

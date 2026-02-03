# isabl_web Analysis

> Vue.js Frontend for the Isabl Platform

**Repository**: Local (`~/isabl/isabl_web`)
**Framework**: Vue.js 2.5+ with Vuetify 2.6
**State Management**: Vuex 3
**Published**: `@papaemmelab/isabl-web` on NPM

## Purpose

isabl_web is the web UI client for browsing and managing Isabl data:

- Search and browse biomedical research data
- Manage projects with role-based access control
- Submit and track analysis jobs
- Visualize hierarchical biological data
- Download and export research data

## Tech Stack

| Category | Technology |
|----------|------------|
| Core | Vue.js 2, Vue Router 3, Vuex 3 |
| UI | Vuetify 2.6, Material Design Icons |
| Visualization | D3.js 5, dc.js 3.1, Crossfilter2 |
| HTTP | Axios 0.21 with token auth |
| Build | Vue CLI 5, Webpack, Babel 7 |
| Testing | Jest (unit), Cypress (E2E) |

## Architecture

```
src/
├── main.js           # Entry point, Vue/Vuetify setup
├── App.vue           # Root: navbar, alerts, modals, router-view
├── router/           # Route definitions
├── store/            # Vuex modules
│   └── modules/      # auth, user, alert, modals, panels, files
├── components/       # 49 Vue components
│   ├── base/         # NavBar, BasePanel, Footer
│   ├── table/        # DataTable, filters
│   ├── search/       # HomeSearch, MainSearch
│   ├── bioModels/    # BioModelTree, BioModelPanel
│   ├── analyses/     # AnalysisPanel, ResultsGallery
│   ├── submissions/  # NewSubmissionModal
│   └── projects/     # ProjectPanel, SharingSettings
├── views/            # Page components (Home, Login, etc.)
├── mixins/           # Reusable logic (auth, fields, files)
└── utils/            # API, settings, helpers
```

## API Integration

### Authentication Flow

1. POST credentials to `/rest-auth/login/`
2. Receive `{ key: "token" }`
3. Store token in localStorage
4. Use `Authorization: Token {token}` header

### Key Endpoints

```
/api/v1/
├── rest-auth/         # login, registration, password reset
├── system_id/         # Biomodels (individuals, samples)
├── analyses/          # CRUD + raw/, download/, igv/
├── experiments/       # CRUD
├── submissions/       # CRUD + process/, download/
├── projects/          # CRUD + epic/, ticket/ (Jira)
├── individuals/       # CRUD + tree/
├── applications/      # Pipeline definitions
└── preferences/       # User settings
```

### API Utilities (`utils/api.js`)

```javascript
fetchListRecords(model, params)  // Paginated list
fetchRecord(model, id)           // Single record
createRecord(model, data)        // POST
updateRecord(model, id, data)    // PATCH
getMediaFile(url, type)          // Download with auth
```

## Key Components

### Panel System

5 collapsible panels managed by Vuex:
- Search, Project, Submission, BioModel, Analysis

### Data Tables

- Server-side pagination
- Sorting via `sort_by` parameter
- Export to Excel/CSV

### BioModel Tree

Visualizes biological hierarchy:
```
Individual → Sample → Experiment → Aliquot → Analysis
```

### Search

- HomeSearch: Global entity search
- MainSearch: Field-value filtering
- DataTableFiltered: Client-side filtering

## Configuration

All customization via `window.$isabl` object:

```javascript
window.$isabl = {
  apiHost: "https://api.isabl.io",
  theme: "dark",
  customFields: {...},
  integrations: {
    jira: true,
    oncoTree: true,
    redcap: true
  }
}
```

## State Management (Vuex)

| Module | Purpose |
|--------|---------|
| auth | Login, logout, permissions |
| user | Profile, theme, favorites |
| alert | Notifications |
| modals | Modal visibility |
| panels | Active panel state |
| files | Upload/download state |

## Key Patterns

### Field Metadata

```javascript
{
  section: "Basic",
  verboseName: "Sample ID",
  field: "sample.identifier",
  editable: true,
  accessor: (val) => val.toUpperCase(),
  rules: [required, maxLength(50)]
}
```

### Mixins

- `auth.js`: `$isAuthorized()`, `$canShareProject()`
- `fields.js`: Field rendering helpers
- `files.js`: File operations

## Third-Party Integrations

- **Jira**: Epic lookup, ticket creation
- **OncoTree**: Disease classification
- **REDCap**: Clinical data forms
- **Segment**: Analytics tracking

## Build Modes

```bash
yarn serve      # Development with hot reload
yarn build-lib  # UMD bundle for NPM
yarn build-wc   # Web Components
```

## Key Concepts for AI Agents

1. **Configuration-driven UI**: Most customization via `window.$isabl`
2. **Panel-based layout**: 5 independent panels for different data views
3. **Token authentication**: Stored in localStorage, sent with all requests
4. **Vuex for state**: Actions dispatch API calls, mutations update state
5. **Server-side pagination**: Tables request data page by page
6. **Hierarchical data**: Individual → Sample → Experiment → Analysis

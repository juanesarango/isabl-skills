# Isabl Web

> Vue.js frontend for the Isabl genomics platform

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | Vue.js 2.5+ |
| UI Components | Vuetify 2.6 |
| State | Vuex 3 |
| Routing | Vue Router 3 |
| HTTP | Axios |
| Visualization | D3.js, dc.js |

## Project Structure

```
src/
├── main.js              # Entry point
├── App.vue              # Root component
├── router/              # Route definitions
├── store/modules/       # Vuex: auth, user, alert, modals, panels, files
├── components/          # 49 Vue components by domain
├── views/               # Page components
├── mixins/              # Reusable logic
└── utils/               # API, settings, helpers
```

## API Integration

### Authentication
```javascript
// Token stored in localStorage as 'user-token'
// Header: Authorization: Token {token}

// Login
POST /api/v1/rest-auth/login/
// Returns: { key: "token" }
```

### API Utilities (`utils/api.js`)
```javascript
import { fetchListRecords, fetchRecord, createRecord, updateRecord } from '@/utils/api'

// Paginated list
const experiments = await fetchListRecords('experiments', { projects: 102 })

// Single record
const exp = await fetchRecord('experiments', 12345)

// Create/Update
await createRecord('analyses', { application: 123, targets: [...] })
await updateRecord('analyses', pk, { status: 'STARTED' })
```

## Configuration

All customization via `window.$isabl` in `public/index.html`:

```javascript
window.$isabl = {
  apiHost: 'https://api.isabl.io',
  theme: 'dark',
  customFields: {
    Individual: [...],
    Sample: [...],
    Experiment: [...]
  },
  integrations: {
    jira: true,
    oncoTree: true
  }
}
```

## Vuex State Management

| Module | Purpose |
|--------|---------|
| `auth` | Login, logout, permissions |
| `user` | Profile, theme, favorites |
| `alert` | Notifications |
| `modals` | Modal visibility |
| `panels` | Active panel state |
| `files` | Upload/download state |

```javascript
// In component
import { mapGetters, mapActions } from 'vuex'

export default {
  computed: {
    ...mapGetters('auth', ['isAuthenticated', 'userPermissions'])
  },
  methods: {
    ...mapActions('auth', ['login', 'logout'])
  }
}
```

## Component Patterns

### Panel System
5 collapsible panels: Search, Project, Submission, BioModel, Analysis

### Data Tables
```vue
<DataTable
  :model="experiments"
  :default-params="{ projects: 102 }"
  :columns="experimentColumns"
/>
```

### Field Definitions (`utils/fields.js`)
```javascript
{
  section: 'Basic',
  verboseName: 'Sample ID',
  field: 'sample.identifier',
  editable: true,
  accessor: (val) => val.toUpperCase(),
  rules: [required, maxLength(50)]
}
```

## Routing

```javascript
// src/router/index.js
{
  path: '/',
  name: 'Home',
  component: Home
},
{
  path: '/login',
  name: 'Login',
  component: Login
}
```

## Mixins

| Mixin | Purpose |
|-------|---------|
| `auth.js` | `$isAuthorized()`, `$canShareProject()` |
| `fields.js` | Field rendering helpers |
| `files.js` | File operations |

## Third-Party Integrations

- **Jira**: `getJiraEpic()`, `createJiraTicket()`
- **OncoTree**: Disease classification
- **REDCap**: Clinical data forms

## Build Commands

```bash
yarn serve      # Development
yarn build      # Production
yarn build-lib  # NPM library
yarn test:unit  # Jest tests
yarn test:e2e   # Cypress tests
```

## Conventions

- PascalCase for component names
- camelCase for JavaScript
- snake_case from API (auto-converted)
- kebab-case for custom field file names

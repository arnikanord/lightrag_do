# UI Enhancements - Dynamic Parameters & Graph Visualization

## ✅ Features Added

### 1. Dynamic Query Parameters
- **Collapsible Advanced Parameters Panel**
  - Query Edges Top-K (5-50, default: 20)
  - Query Edges Cosine Threshold (0.1-1.0, default: 0.2)
  - Query Nodes Top-K (5-50, default: 20)
  - Query Nodes Cosine Threshold (0.1-1.0, default: 0.2)
  - Chunk Top-K (5-30, default: 10)
  - Chunk Cosine Threshold (0.1-1.0, default: 0.2)
  - Enable Reranking (checkbox, default: false)

- **Real-time Slider Updates**
  - Values update as you move sliders
  - Visual feedback with current values
  - Reset to defaults button

- **Mode-Specific Parameters**
  - Parameters automatically apply based on selected mode
  - Hybrid mode: Uses all parameters
  - Global mode: Uses edge/node parameters
  - Naive mode: Uses chunk parameters
  - Local mode: Uses node parameters

### 2. Knowledge Graph Visualization
- **Interactive Graph Display**
  - Uses vis.js library for network visualization
  - Nodes represent entities
  - Edges represent relations
  - Interactive: Click, drag, zoom, hover

- **Graph Features**
  - Automatic layout with physics simulation
  - Color-coded nodes and edges
  - Hover tooltips showing descriptions
  - Click to select nodes
  - Responsive design (600px height)

- **Graph Endpoint**
  - `/graph` - Get full knowledge graph (up to 100 nodes/edges by default)
  - `/graph/query?query=...` - Get graph filtered by query (future enhancement)
  - Returns nodes and edges in JSON format

### 3. Backend Updates

#### Query Endpoint (`POST /query`)
- Accepts optional parameters:
  - `query_edges_top_k`
  - `query_edges_cosine`
  - `query_nodes_top_k`
  - `query_nodes_cosine`
  - `chunk_top_k`
  - `chunk_cosine`
  - `enable_rerank`

- Uses user-provided parameters or defaults
- Returns parameters used in response

#### Graph Endpoint (`GET /graph`)
- Retrieves entities and relations from LightRAG storage
- Multiple access methods:
  1. Direct storage access (entity_storage, relation_storage)
  2. JSON file reading (entities.json, relations.json)
- Validates and filters data for visualization
- Returns format:
  ```json
  {
    "nodes": [...],
    "edges": [...],
    "node_count": 50,
    "edge_count": 30
  }
  ```

## 🎨 UI Components

### Parameter Controls
- Located in "Advanced Parameters" section (collapsible)
- Sliders with value displays
- Reset button for defaults
- Mode-aware (shows relevant parameters)

### Graph Visualization
- Located below query form
- "Load Knowledge Graph" button
- Graph container (600px height, full width)
- Info display showing node/edge counts
- Auto-layout with physics simulation

## 📊 Usage

### Adjusting Query Parameters
1. Click "⚙️ Advanced Parameters" button
2. Adjust sliders for desired values
3. Parameters are automatically included in query
4. Click "Reset to Defaults" to restore defaults

### Viewing Knowledge Graph
1. Click "📊 Load Knowledge Graph" button
2. Graph loads from storage (entities and relations)
3. Interactive exploration:
   - Click and drag nodes
   - Zoom with mouse wheel
   - Hover for descriptions
   - Click nodes to select

### Query with Custom Parameters
1. Enter your query
2. Select query mode
3. (Optional) Adjust advanced parameters
4. Click "Execute Query"
5. Query uses your custom parameters

## 🔧 Technical Details

### Libraries Used
- **vis.js Network** - Graph visualization
  - CDN: `https://unpkg.com/vis-network/standalone/umd/vis-network.min.js`
  - Physics-based layout
  - Interactive features

### Graph Data Format
- **Nodes (Entities)**:
  ```json
  {
    "id": "entity_name",
    "name": "Entity Name",
    "description": "Description",
    "type": "entity"
  }
  ```

- **Edges (Relations)**:
  ```json
  {
    "from": "entity_id_1",
    "to": "entity_id_2",
    "relation": "relation_type",
    "description": "Relation description"
  }
  ```

### Storage Access
- Tries multiple methods to access LightRAG storage:
  1. Direct attribute access (`entity_storage`, `relation_storage`)
  2. JSON file reading from `WORKING_DIR`
- Handles different storage formats (dict, list, JSON)

## 🚀 Future Enhancements

1. **Query-Filtered Graph**
   - Show only entities/relations relevant to query
   - Highlight query-related nodes

2. **Graph Export**
   - Export as PNG/SVG
   - Export as JSON

3. **Graph Statistics**
   - Node/edge counts by type
   - Degree distribution
   - Community detection

4. **Interactive Query Building**
   - Click nodes to add to query
   - Filter graph by node type
   - Search nodes in graph

5. **Parameter Presets**
   - Save/load parameter sets
   - Quick presets: "Fast", "Balanced", "Quality"

## 📝 Notes

- Graph visualization works best with < 200 nodes
- Large graphs may be slow to render
- Parameters apply only if "Advanced Parameters" section is visible
- Graph endpoint may return empty if no documents ingested yet

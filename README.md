# 🌐 SOK - Graph Visualization Platform

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

> A powerful, extensible graph visualization platform with a plugin-based architecture for loading, analyzing, and visualizing graph data from multiple sources.

## ✨ Features

- **🔌 Plugin Architecture**: Extensible system for data sources and visualizers
- **📊 Multiple Visualizers**: Choose between Simple and Block visualization styles
- **🔍 Advanced Search & Filter**: Query and filter graph nodes with intuitive syntax
- **📁 Multiple Data Sources**: Support for JSON and XML graph formats
- **🖥️ Dual Interface**: Both web UI and interactive CLI available
- **🔄 Workspace Management**: Handle multiple graphs simultaneously
- **🌳 Multiple Views**: Graph, Tree, and Bird's-eye view modes
- **📈 Graph Analysis**: Built-in cycle detection and graph statistics

## 🛠️ Technologies Used

### Backend
- **Python 3.8+** - Core programming language
- **Django 4.2.7** - Web framework
- **SQLite** - Database for persistence

### Data Processing
- **xmltodict 0.13.0** - XML parsing
- **Pillow 10.1.0** - Image processing
- **requests 2.31.0** - HTTP client

### Frontend
- **HTML5/CSS3** - Modern web interface
- **JavaScript** - Interactive UI components
- **D3.js** (implied) - Graph visualizations

### Architecture
- **Plugin System** - Modular, extensible architecture
- **Singleton Pattern** - Centralized platform management
- **MVC Pattern** - Clean separation of concerns

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/teodora525/SOK.git
cd SOK/graph-visualization
```

### 2. Create and activate virtual environment
```bash
# On Linux/Mac
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Django
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

## 💻 Usage

### Web Interface

Start the Django development server:
```bash
python manage.py runserver
```

Then open your browser and navigate to `http://localhost:8000`

**Web Interface Features:**
- Upload graph files (JSON/XML)
- Select visualization style
- Search and filter nodes
- Switch between multiple workspaces
- View graph statistics
- Interactive node exploration

### Command Line Interface (CLI)

Start the interactive CLI:
```bash
python run_cli.py
```

**Available CLI Commands:**
```
load <data_source> <file_path>     - Load graph from file
visualize <visualizer>              - Display current graph
search <query>                      - Search for nodes
filter <expression>                 - Filter graph
reset                               - Reset to original graph
workspace <id>                      - Switch workspace
plugins                             - List available plugins
help                                - Show help
quit                                - Exit CLI
```

## 📦 Project Structure

```
SOK/
└── graph-visualization/
    ├── api/                        # Core API models and operations
    │   ├── models/                 # Graph, Node, Edge models
    │   ├── operations/             # Search, filter operations
    │   └── plugins/                # Plugin base classes
    ├── explorer/                   # Django web interface
    │   ├── templates/              # HTML templates
    │   ├── views.py                # Web API endpoints
    │   └── urls.py                 # URL routing
    ├── graph_platform/             # Core platform logic
    │   ├── core.py                 # Platform singleton
    │   └── cli.py                  # CLI implementation
    ├── graph_explorer/             # Django project settings
    │   └── settings.py             # Configuration
    ├── plugins/                    # Built-in plugins
    │   ├── data_source_json_plugin.py
    │   ├── data_source_xml_plugin.py
    │   ├── simple_visualizer_plugin.py
    │   └── block_visualizer_plugin.py
    ├── manage.py                   # Django management
    ├── run_cli.py                  # CLI entry point
    └── requirements.txt            # Python dependencies
```

## 🔌 Plugin System

### Data Source Plugins
Data source plugins load graph data from different formats:

- **JSON Parser**: Loads graphs from JSON files
- **XML Parser**: Parses XML formatted graphs

### Visualizer Plugins
Visualizer plugins render graphs in different styles:

- **Simple Visualizer**: Clean, minimalist graph rendering
- **Block Visualizer**: Enhanced visualization with node blocks

### Creating Custom Plugins

Extend the base plugin classes to create your own:

```python
from api.plugins.base import DataSourcePlugin

class MyCustomPlugin(DataSourcePlugin):
    def get_plugin_name(self):
        return "My Custom Plugin"
    
    def get_required_parameters(self):
        return ['file_path']
    
    def load_graph(self, **kwargs):
        # Your implementation here
        pass
```

## 🎯 Use Cases

- **Network Analysis**: Visualize and analyze network topologies
- **Family Trees**: Display genealogical relationships
- **Organizational Charts**: Map company structures
- **Dependency Graphs**: Explore software dependencies
- **Knowledge Graphs**: Represent interconnected information
- **Social Networks**: Analyze social connections

## 🔍 Advanced Features

### Search Syntax
```
name:John              # Search by node name
type:person           # Filter by node type
age>30                # Numeric comparisons
```

### Filter Expressions
```
node.type == 'person'
node.age > 25
node.name.contains('John')
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Graph Visualization Team** - *Initial work*

## 🙏 Acknowledgments

- Django framework for the robust web foundation
- The open-source community for inspiration and tools
- All contributors who have helped shape this project

## 📧 Contact

For questions and support, please open an issue in the GitHub repository.

---

<div align="center">
  Made with ❤️ by the Graph Visualization Team
</div>
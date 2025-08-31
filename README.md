# Apotheosis Workbench

**A web-based, interactive visualizer for dependency graphs.**

The Apotheosis Workbench is a stateful web application designed to be the central hub for viewing and analyzing dependency graphs. It combines a powerful Flask backend with a responsive, modern frontend to provide a seamless visualization experience.

![Screenshot](workbench.png)

---

-   [Core Concepts](#core-concepts)
-   [Features](#features)
-   [Project Structure](#project-structure)
-   [Setup and Running](#setup-and-running)
-   [How to Add Graphs](#how-to-add-graphs)
-   [The Local Service API Endpoint](#the-local-service-api-endpoint)

## Core Concepts

The Workbench is more than just a file viewer; it's a **stateful manager**. It maintains a persistent database (`db.json`) of all graphs it knows about, regardless of where they are stored on your local filesystem. This allows it to:

1.  **Reference External Files:** Track graphs located deep within project directories without needing to copy them.
2.  **Monitor Status:** Automatically detect when a graph file has been updated, gone missing, or is newly added.
3.  **Provide a Central UI:** Act as a single source of truth for all relevant dependency graphs for a developer or a team.

While the Workbench UI allows for manual interaction, it is designed to be primarily controlled by its companion tool, the **`apotheosis` CLI**. The CLI is the professional's "power tool" for this workbench.

## Features

-   **Interactive Visualization:** Utilizes Cytoscape.js to render complex graphs with a clean, navigable interface.
-   **Stateful Graph Management:** Remembers all registered graphs and their metadata between sessions.
-   **Real-time Status Updates:** The graph list automatically highlights new, updated, or missing graph files on every refresh.
-   **Responsive UI:** A clean interface with a slide-out drawer provides a seamless experience on both desktop and mobile devices.
-   **Local File System Integration:** Via a secure, localhost-only API, the `apotheosis` CLI can add graphs from anywhere on the filesystem.
-   **Local File Preview:** Quickly view a local graph file without permanently adding it to the workbench.
-   **Manual Upload & Creation:** A built-in modal allows for manually uploading files or pasting raw JSON data.

## Project Structure

The workbench is composed of a few key files within the `ap_workbench` directory:

```
ap_workbench/
├── uploads/              # Default storage for graphs uploaded via the web UI.
├── app.py                # The Flask backend server; the brains of the operation.
├── db.json               # The persistent database tracking all known graphs.
└── index.html            # The complete frontend single-page application.
```
-   `app.py`: The Python server that handles API requests, file serving, and status checks.
-   `index.html`: Contains all the HTML, CSS, and JavaScript for the user interface.
-   `db.json`: A simple JSON file that acts as the database. It stores the path, label, and status of each graph. **It is recommended to add this file to your `.gitignore`**.
-   `uploads/`: A convenient place for graphs managed entirely by the web UI.

## Setup and Running

Follow these steps to get the Apotheosis Workbench running on your local machine.

### 1. Prerequisites

-   **Python 3.6+**
-   **Flask library:** If you don't have it, install it via pip:
    ```bash
    pip install Flask
    ```

### 2. Get the Code

Clone or download the `ap_workbench` project directory to your local machine.

### 3. Run the Server

Navigate into the project directory with your terminal and run the `app.py` script.

```bash
cd /path/to/your/ap_workbench
python app.py
```

The server will start, and you should see output similar to this:

```text
 * Serving Flask app 'app'
 * Running on http://127.0.0.1:8001
Press CTRL+C to quit
```

### 4. Access the Workbench

Open your web browser and navigate to the URL provided:

**[http://localhost:8001](http://localhost:8001)**

The Workbench UI should now be visible.

## How to Add Graphs

There are three primary ways to add graphs to the workbench, listed in order of recommendation.

### Method 1: The `apotheosis` CLI (Recommended)

This is the primary and most powerful method. The CLI allows you to add graphs from any location and process raw dependency files (like `build/knit.json`) directly from your project's root directory.

**See the [Apotheosis CLI Documentation] for full installation and usage instructions.**

**Example:**
```bash
# From your project's root directory
apotheosis process --yes ./app/build/knit.json "My App Dependencies"
```

### Method 2: Previewing Local Files

For quick, one-off analysis, you can view a local file without permanently adding it to the workbench.

-   Click the **"Preview Local File"** button.
-   Select a valid Cytoscape.js `.json` file from your computer.
-   The graph will be rendered for viewing. It will disappear on the next page refresh.

### Method 3: Manual Upload / Creation

The UI provides a modal for manual additions.

-   Click the **"Add Graph"** button.
-   You will be presented with two choices:
    1.  **Upload a File:** This will open a file picker and save the selected `.json` file to the `uploads/` directory on the server.
    2.  **Create by Pasting Text:** This allows you to paste raw JSON data and provide a filename, which will then be saved to the `uploads/` directory.

## The Local Service API Endpoint

The workbench exposes a secure, localhost-only endpoint for programmatic integration. This is the API used by the `apotheosis` CLI.

**Endpoint:** `POST /_localservice/add`
-   **Access:** This endpoint will only accept requests originating from `127.0.0.1` (localhost).
-   **Payload:** A JSON object with the following structure:

    ```json
    {
        "path": "/absolute/path/to/your/graph.json",
        "label": "A User-Friendly Label for the Graph"
    }
    ```

**Example with `curl`:**
```bash
curl -X POST http://localhost:8001/_localservice/add \
-H "Content-Type: application/json" \
-d '{
    "path": "/Users/dev/my-project/build/knit.json",
    "label": "Graph from Curl"
}'
```
# Apotheosis CLI

**The Command-Line Interface for the Apotheosis Workbench**

Apotheosis is the professional's command-line partner to the Apotheosis Workbench visualizer. It is a powerful, scriptable tool designed to bridge your local development environment with the web UI, allowing you to seamlessly add, process, and manage complex dependency graphs directly from your terminal.

---

-   [Overview](#overview)
-   [Features](#features)
-   [Prerequisites](#prerequisites)
-   [Installation](#installation)
-   [The Workflow](#the-workflow)
-   [Command Reference](#command-reference)
    -   [`apotheosis init`](#apotheosis-init)
    -   [`apotheosis add`](#apotheosis-add)
    -   [`apotheosis process`](#apotheosis-process)
-   [Recommended Setup for Knit Users](#recommended-setup-for-knit-users)
    -   [The Core Workflow](#the-core-workflow)
    -   [Automating with Gradle](#automating-with-gradle)
-   [The Local Service Endpoint](#the-local-service-endpoint)

## Overview

While the Apotheosis Workbench provides a rich, interactive visualization experience, `apotheosis` provides the automation and integration layer. It is designed to be the primary way developers and build systems interact with the workbench, allowing you to:

-   **Process** raw, unstructured dependency data into the standardized Cytoscape.js format required by the visualizer.
-   **Add** any graph file on your local system—whether in a project directory or a shared folder—to the workbench's list of viewable graphs.
-   **Automate** your documentation and analysis pipeline by integrating graph generation directly into your build scripts.

## Features

-   **Zero-Configuration Start:** Works out-of-the-box for local setups with sensible defaults.
-   **Powerful Data Processing:** Includes a built-in converter to transform raw dependency JSON into a clean, viewable graph, handling noise-filtering, multi-bindings, and parent-child relationships automatically.
-   **Local File System Integration:** Add graphs from any path on your machine, not just a dedicated `uploads` folder. The workbench maintains a reference, keeping your files where they belong.
-   **Interactive & Scriptable:** Use it interactively with helpful prompts for guided use, or pass all arguments and the `--yes` flag for silent execution in automated scripts.
-   **Elegant Workflow:** Designed to fit naturally into a developer's workflow, making graph visualization a trivial part of any build or analysis process.

## Prerequisites

1.  **Python 3.6+**
2.  The **`requests` library**: `pip install requests`
3.  The **Apotheosis Workbench Server** (`app.py`) must be running. Apotheosis is a client that communicates with this server.

## Installation

The script is designed to be run as a standalone executable.

1.  **Save the Script:** Save the Python code as a file named `apotheosis` (no extension) in a temporary location from `scripts/apotheosis`

2.  **Make it Executable:** Open your terminal and grant execute permissions.
    ```bash
    chmod +x apotheosis
    ```

3.  **Move to your PATH:** For system-wide access, move the script to a directory in your system's `PATH`. `/usr/local/bin` is a common choice for macOS and Linux.
    ```bash
    # On macOS or Linux
    sudo mv ./apotheosis /usr/local/bin/apotheosis
    ```
    On Windows, you can place the script in a dedicated folder and add that folder to your system's `Path` Environment Variable.

## The Workflow

The intended workflow is simple and powerful:

1.  **Start the Server:** In your `ap_workbench` project directory, run the web UI server.
    ```bash
    python app.py
    ```

2.  **Use the CLI:** In another terminal, from any directory, use `apotheosis` to add or process your graph files.
    ```bash
    # Process a raw dependency file generated by your build tool
    apotheosis process ./my-project/build/raw-deps.json "My Project Dependencies"
    ```

3.  **View the Results:** Open or refresh your browser at `http://localhost:8001`. Your newly added graph will appear at the top of the list, highlighted and ready for analysis.

## Command Reference

### `apotheosis init`

Initializes or updates the Apotheosis configuration file. **This is an optional command**, only needed if your Apotheosis Workbench server is not running on `http://localhost:8001`.

**Usage:**

```bash
apotheosis init
```

The CLI will guide you through the setup process. This creates a configuration file at `~/.config/apotheosis/config.json`.

**Example:**
```text
$ apotheosis init
i Initialize or update Apotheosis configuration.
? Configuration file already exists. Overwrite? (y/N): y
? Enter the Visualizer Server URL [http://localhost:8001]: http://192.168.1.100:9000
✓ Configuration saved to /Users/yourname/.config/apotheosis/config.json
```

---

### `apotheosis add`

Adds a **pre-formatted Cytoscape.js JSON file** to the workbench. Use this command when your graph file is already in the correct format.

**Syntax:**
```text
apotheosis add [--yes] [graph_path] [label]
```
-   `graph_path`: The absolute or relative path to the `.json` file.
-   `label`: A user-friendly name for the graph in the UI.
-   `--yes` or `-y`: Skips the final confirmation prompt.

**Examples:**

1.  **Interactive Mode:**
    ```bash
    apotheosis add
    ```
    The CLI will prompt you for the path and label.

2.  **With Arguments:**
    ```bash
    apotheosis add ./docs/graphs/final-graph.json "Final Production Graph"
    ```
    The CLI will parse the arguments and ask for a final confirmation.

3.  **Scripting Mode:**
    ```bash
    apotheosis add --yes /path/to/graph.json "Automated Graph Entry"
    ```
    The command executes without any user interaction.

---

### `apotheosis process`

The most powerful command. It takes a **raw, unprocessed dependency file**, converts it into the Cytoscape.js format, saves the result in a local `.apotheosis` directory, and adds it to the workbench.

**The Output:** The processed graph is saved locally to `./.apotheosis/graphs/<input_filename>.cytoscape.json` relative to your current working directory. This new file is the one added to the workbench.

**Syntax:**
```text
apotheosis process [--yes] [input_path] [label]
```
-   `input_path`: The path to the raw input `.json` file.
-   `label`: A user-friendly name for the processed graph.
-   `--yes` or `-y`: Skips the final confirmation prompt.

**Examples:**

1.  **Interactive Mode:**
    ```bash
    apotheosis process
    ```
    The CLI will prompt you for the input file path and the desired label.

2.  **With Arguments:**
    ```bash
    apotheosis process ./app/build/knit.json "MyApp Main Dependencies"
    ```

3.  **Scripting Mode (Build Pipeline Integration):**
    ```bash
    # Imagine this command running at the end of a Gradle or Maven build
    apotheosis process --yes ./build/reports/deps.json "CI Build #${BUILD_NUMBER}"
    ```

---

## Recommended Setup for Knit Users

Apotheosis is an ideal companion for dependency injection frameworks like [Knit](https://github.com/Knit-From-A-Pancake/Knit). The `process` command is specifically designed to consume the raw dependency output from Knit's annotation processor and prepare it for visualization.

### The Core Workflow

The standard workflow involves two steps:
1.  Your build system (e.g., Gradle) compiles your project, and the Knit annotation processor generates a raw dependency file located at `build/knit.json` in your module's directory.
2.  You run `apotheosis process` on this generated file to add it to the workbench.

**Example Command:**
```bash
# Assuming you are in your project's root directory
apotheosis process --yes ./app/build/knit.json "My Awesome App - Dependencies"
```

### Automating with Gradle

To make this process seamless, you can add a custom task to your `build.gradle` file. This allows you to update your dependency graph with a single command.

Add the following to your module-level `build.gradle` (e.g., `app/build.gradle`):

```groovy
// In your app/build.gradle file

task visualizeDependencies(type: Exec) {
    group = "documentation"
    description = "Processes the Knit dependency graph and adds it to the Apotheosis workbench."
    
    // Ensure this task runs after the project is built and the dependency file exists
    dependsOn 'assembleDebug' 

    // The command to execute. Assumes 'apotheosis' is in your system's PATH.
    commandLine 'apotheosis', 'process', '--yes', 'build/knit.json', "My Awesome App (Debug Build)"
}
```

You can now automatically process and add your graph by running:
```bash
./gradlew visualizeDependencies
```

This integrates graph visualization directly into your development lifecycle, ensuring your documentation and analysis tools are always up-to-date.

---

## The Local Service Endpoint

Apotheosis communicates with the workbench via a special, localhost-only API endpoint: `/_localservice/add`. Advanced users can interact with this endpoint directly from other tools or scripts.

**Endpoint:** `POST /_localservice/add`
**Payload:**
```json
{
    "path": "/absolute/path/to/your/graph.json",
    "label": "My Custom-Added Graph"
}
```

**Example with `curl`:**
```bash
curl -X POST http://localhost:8001/_localservice/add \
-H "Content-Type: application/json" \
-d '{
    "path": "/Users/dev/my-project/graph.json",
    "label": "Graph from Curl"
}'
```

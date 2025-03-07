# ComfyUI Workflow Customization Guide

This guide provides detailed instructions on how to customize your ComfyUI workflow for deployment on Replicate using the cog-comfyui template.

## Table of Contents

1. [Exporting Your Workflow](#exporting-your-workflow)
2. [Understanding the Workflow Structure](#understanding-the-workflow-structure)
3. [Customizing the Prediction Interface](#customizing-the-prediction-interface)
4. [Managing Model Weights](#managing-model-weights)
5. [Handling Custom Nodes](#handling-custom-nodes)
6. [Testing and Deployment](#testing-and-deployment)
7. [Troubleshooting](#troubleshooting)

## Exporting Your Workflow

To export your workflow from ComfyUI:

1. Create and test your workflow in ComfyUI
2. Click on the "Save" button in the ComfyUI interface
3. Select "Save (API Format)" to export the workflow in API format
4. Save the exported file as `workflow_api.json` in the root directory of your project
5. Optionally, also save the UI format as `workflow_ui.json` for reference

## Understanding the Workflow Structure

The `workflow_api.json` file contains a JSON object where each key is a node ID, and each value is an object with the following structure:

```json
{
  "inputs": {
    "param1": value1,
    "param2": value2,
    ...
  },
  "class_type": "NodeClassName",
  "_meta": {
    "title": "Node Title"
  }
}
```

Node connections are represented as arrays with two elements: the node ID and the output index.

For example:
```json
"image": [
  "694",
  0
]
```
This connects to output 0 of node 694.

## Customizing the Prediction Interface

To customize the prediction interface, you need to modify the `predict.py` file:

1. Update the `predict` method to include the parameters you want to expose:

```python
def predict(
    self,
    prompt: str = Input(
        description="Text prompt for image generation",
        default="Your default prompt here"
    ),
    negative_prompt: str = Input(
        description="Negative prompt to specify what not to include",
        default="Your default negative prompt here"
    ),
    # Add more parameters as needed
) -> List[Path]:
    # ...
```

2. Update the `update_workflow` method to map your parameters to the workflow:

```python
def update_workflow(self, workflow, **kwargs):
    # Find the nodes you want to update
    for node_id, node in workflow.items():
        # Example: Update prompt node
        if "class_type" in node and node["class_type"] == "CLIPTextEncode":
            if "_meta" in node and node["_meta"].get("title") == "CLIP Text Encode":
                node["inputs"]["text"] = kwargs["prompt"]
                
        # Example: Update negative prompt node
        if "class_type" in node and node["class_type"] == "CLIPTextEncode":
            if "_meta" in node and node["_meta"].get("title") == "CLIP Text Encode (Negative)":
                node["inputs"]["text"] = kwargs["negative_prompt"]
                
        # Example: Update seed
        if "class_type" in node and node["class_type"] == "Seed Everywhere":
            node["inputs"]["seed"] = kwargs["seed"]
            
        # Add more mappings as needed
```

## Managing Model Weights

To manage model weights:

1. Update the `weights_to_download` list in the `setup` method of `predict.py`:

```python
weights_to_download = [
    # Checkpoints
    "your_checkpoint.safetensors",
    
    # LoRAs
    "your_lora.safetensors",
    
    # VAE
    "your_vae.safetensors",
    
    # Other weights as needed
]
```

2. Ensure that the weights are correctly referenced in your workflow

3. If you need custom weight handling, you can modify the `handle_weights` method in `comfyui.py`

## Handling Custom Nodes

To add custom nodes:

1. Add the node repository to `custom_nodes.json`:

```json
[
  {
    "repo": "https://github.com/username/repo-name",
    "commit": "commit-hash"
  }
]
```

2. Add any required dependencies to `cog.yaml`:

```yaml
build:
  python_packages:
    - package-name==version
```

3. If the custom node requires special handling, you can add a helper in `custom_node_helpers/`

## Testing and Deployment

To test and deploy your workflow:

1. Build the container:
   ```bash
   cog build
   ```

2. Test locally:
   ```bash
   cog predict -i prompt="your test prompt"
   ```

3. Push to Replicate:
   ```bash
   cog push r8.im/yourusername/your-model-name
   ```

## Troubleshooting

Common issues and solutions:

### Missing Weights
- Check if the weight files are correctly listed in `weights_to_download`
- Verify that the weights are available from the sources configured in `weights.json`

### Custom Node Errors
- Ensure the custom node is compatible with the ComfyUI version
- Check if all dependencies are installed
- Look for error messages in the logs

### Workflow Execution Errors
- Test the workflow in ComfyUI locally first
- Check for node compatibility issues
- Ensure all node connections are correct

### Parameter Mapping Issues
- Verify that the node IDs in `update_workflow` match those in your workflow
- Check that parameter types match between `predict` and the workflow nodes

### Container Build Issues
- Check for dependency conflicts in `cog.yaml`
- Ensure all required packages are listed
- Monitor the build logs for errors 
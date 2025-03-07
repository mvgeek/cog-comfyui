# Cursor Rules for ComfyUI Workflow Development

This document outlines the rules and best practices for developing and maintaining the ComfyUI workflow deployment project in Cursor. Following these guidelines will help ensure that the project remains maintainable and functions correctly.

## Workflow Modification Rules

### General Guidelines
- Always maintain the JSON structure of the workflow_api.json file
- Keep node IDs consistent when modifying the workflow
- Test changes with ComfyUI locally before deploying

### Adding New Nodes
- Ensure the node class_type is compatible with the installed custom nodes
- Add any new required weights to the weights_to_download list in predict.py
- Update the update_workflow method in predict.py to handle any new parameters

### Modifying Existing Nodes
- Preserve the existing node IDs to maintain connections
- When changing node parameters, update the corresponding section in update_workflow
- Document changes to the workflow in comments or documentation

## Weight Management Rules

### Adding Model Weights
- Add new model files to the weights_to_download list in predict.py
- Ensure the model is placed in the correct directory structure
- Update .dockerignore if necessary to include the weight files

### Directory Structure
- Checkpoints go in ComfyUI/models/checkpoints/
- LoRAs go in ComfyUI/models/loras/
- VAE models go in ComfyUI/models/vae/
- CLIP models go in ComfyUI/models/clip/
- SAM models go in ComfyUI/models/sam/
- Detection models go in ComfyUI/models/bbox/
- LUT files go in ComfyUI/models/luts/

### Weight References
- When referencing weights in the workflow, use the exact filename
- Ensure weights are compatible with the ComfyUI version being used

## Custom Node Management Rules

### Adding Custom Nodes
- Add new custom nodes to custom_nodes.json with the correct repo URL and commit hash
- Install any dependencies required by the custom node in cog.yaml
- Test custom nodes locally before deploying
- If the node has configuration requirements, add them to custom_node_configs/

### Removing Custom Nodes
- Remove the entry from custom_nodes.json
- Remove any corresponding helpers in custom_node_helpers/
- Remove configurations from custom_node_configs/
- Remove dependencies from cog.yaml if they're not used by other nodes

## Input Parameter Rules

### Adding New Parameters
- Add the parameter to the predict method in predict.py
- Update the update_workflow method to handle the new parameter
- Provide sensible defaults and input validation
- Document the parameter with a clear description

### Modifying Existing Parameters
- Update both the predict method and update_workflow method
- Ensure backward compatibility if possible
- Update documentation to reflect changes

### Parameter Types
- Use appropriate Cog Input types for parameters
- For categorical parameters, use the choices parameter
- For numerical parameters, use ge and le for bounds
- For file inputs, use the Path type

## Deployment Rules

### Pre-Deployment Checklist
- Ensure all custom nodes are correctly installed and configured
- Verify all required weights are in the weights_to_download list
- Test the model locally with cog predict
- Check for any potential issues in the workflow

### Building the Container
- Use cog build to build the container
- Test the built container with cog predict
- Resolve any issues before pushing to Replicate

### Pushing to Replicate
- Use cog push r8.im/<username>/<model-name> to push the container
- Verify the model works correctly on Replicate
- Update documentation and examples as needed

## Code Style and Documentation

### Python Code Style
- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Limit line length to 100 characters

### JSON Style
- Use consistent indentation (2 spaces recommended)
- Format JSON files for readability
- Validate JSON files before committing changes

### Documentation
- Update README.md when making significant changes
- Document any non-obvious behavior or workarounds
- Include examples for new features or parameters

## Version Control

### Commits
- Write clear and concise commit messages
- Group related changes in a single commit
- Include references to issues or tickets when applicable

### Branches
- Use feature branches for new features or significant changes
- Test changes thoroughly before merging to main
- Keep branches up to date with main

## Error Handling

### Validation
- Validate inputs before processing
- Check for required files and directories
- Verify that the workflow is valid before running

### Error Messages
- Provide clear and helpful error messages
- Include information on how to resolve common issues
- Log relevant information for debugging

### Graceful Degradation
- Handle missing weights gracefully
- Provide fallbacks when possible
- Always clean up temporary files and resources 
#!/bin/bash

# Script to verify the model setup and prepare for Replicate deployment

echo "Verifying model setup..."

# Check if required files exist
if [ ! -f "workflow_api.json" ]; then
  echo "ERROR: workflow_api.json is missing"
  exit 1
fi

if [ ! -f "predict.py" ]; then
  echo "ERROR: predict.py is missing"
  exit 1
fi

if [ ! -f "weights_downloader.py" ]; then
  echo "ERROR: weights_downloader.py is missing"
  exit 1
fi

if [ ! -f "cog.yaml" ]; then
  echo "ERROR: cog.yaml is missing"
  exit 1
fi

echo "All required files are present."

# Check if ComfyUI directory exists
if [ ! -d "ComfyUI" ]; then
  echo "WARNING: ComfyUI directory is missing. It will be cloned during the build process."
fi

# Check if LoRA files are already present (optional)
if [ -f "ComfyUI/models/loras/flux_realism_lora.safetensors" ]; then
  echo "LoRA file found: flux_realism_lora.safetensors"
fi

if [ -f "ComfyUI/models/loras/Kasabulibaas.safetensors" ]; then
  echo "LoRA file found: Kasabulibaas.safetensors"
fi

# Build instructions
echo ""
echo "To build and test the model locally, run:"
echo "cog build"
echo "cog predict -i prompt=\"A loving couple dancing on the beach at sunset, purple flowers in the background\""

# Deployment instructions
echo ""
echo "To deploy the model to Replicate, run:"
echo "cog push r8.im/<username>/<model-name>"
echo "Replace <username> and <model-name> with your Replicate username and desired model name."

echo ""
echo "Verification complete!" 
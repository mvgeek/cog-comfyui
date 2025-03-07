# ComfyUI FLUX Workflow Deployment with Cog

This repository contains a deployment of a FLUX image generation workflow using ComfyUI on Replicate. It allows you to generate high-quality images with the FLUX model through a simple API.

## Model Overview

This model uses the FLUX.1-dev workflow from Black Forest Labs, featuring multiple stages of processing:
- Text-to-image generation with the FLUX model
- Hand and face detailing for improved quality
- LUT color grading for professional-looking results

## Input Parameters

The model accepts the following parameters:

- **prompt** - The text description of the image you want to generate
- **loras** - A list of LoRA names to apply to your generation (can use multiple simultaneously)
- **resolution** - Image size to generate (choose from 512x768, 768x1280, 1024x1024, or 1024x1536)
- **steps** - Number of steps for image generation (higher = better quality but slower)
- **seed** - Random seed for reproducible results

## Examples

Here are some example prompts you can try:

```
A loving couple dancing on the beach at sunset, purple flowers in the background
```

```
A professional portrait of a business woman in an office with purple decorations, natural lighting
```

```
A family enjoying a picnic in a park, with purple balloons floating in the background
```

## Using Multiple LoRAs

You can apply multiple LoRAs simultaneously to your generations by providing them in a list. The model comes with two built-in LoRAs:

- `flux_realism_lora` - Improves overall realism
- `Kasabulibaas` - Adds distinct artistic styling

By default, both are applied together. You can specify them with or without the `.safetensors` extension.

### Example of using multiple LoRAs:

```python
loras=["flux_realism_lora", "Kasabulibaas"]
```

You can add as many LoRAs as you need, and they will be applied in the order provided. The first two LoRAs will use the pre-configured slots, and additional LoRAs will be dynamically added to the workflow.

## Technical Details

This model uses:
- FLUX1-dev checkpoint for base image generation
- Custom face, hand, and eye detailing nodes
- Portra 800 LUT color grading

## Acknowledgments

This project builds upon:
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- [Black Forest Labs FLUX models](https://huggingface.co/black-forest-labs/FLUX.1-dev)
- Various custom node repositories (see `custom_nodes.json`)

## Environment Setup

This project requires the following environment variables to be set for downloading model weights:

- `HF_TOKEN`: Hugging Face access token for downloading models from Hugging Face
- `HF_PRIVATE_TOKEN`: Hugging Face access token with specific permissions for private model repositories

You can set these environment variables before running the application:

```bash
export HF_TOKEN="your_huggingface_token"
export HF_PRIVATE_TOKEN="your_private_huggingface_token"
```

For local development, you can create a `.env` file and load it:

```bash
# .env file
HF_TOKEN=your_huggingface_token
HF_PRIVATE_TOKEN=your_private_huggingface_token
```

**Important**: Never commit tokens directly in code. Always use environment variables or secure secrets management.

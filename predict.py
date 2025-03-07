import os
import json
import shutil
import mimetypes
from typing import List
from cog import BasePredictor, Input, Path
from comfyui import ComfyUI
from cog_model_helpers import optimise_images
from cog_model_helpers import seed as seed_helper

OUTPUT_DIR = "/tmp/outputs"
INPUT_DIR = "/tmp/inputs"
COMFYUI_TEMP_OUTPUT_DIR = "ComfyUI/temp"
ALL_DIRECTORIES = [OUTPUT_DIR, INPUT_DIR, COMFYUI_TEMP_OUTPUT_DIR]

mimetypes.add_type("image/webp", ".webp")

# Use the workflow JSON file
api_json_file = "workflow_api.json"

# Force HF offline
os.environ["HF_DATASETS_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

class Predictor(BasePredictor):
    def setup(self):
        self.comfyUI = ComfyUI("127.0.0.1:8188")
        self.comfyUI.start_server(OUTPUT_DIR, INPUT_DIR)

        # Load the workflow to prepare for weight detection
        with open(api_json_file, "r") as file:
            workflow = json.loads(file.read())
            
        # Create directories for custom node models if needed
        os.makedirs("ComfyUI/models/checkpoints", exist_ok=True)
        os.makedirs("ComfyUI/models/loras", exist_ok=True)
        os.makedirs("ComfyUI/models/vae", exist_ok=True)
        os.makedirs("ComfyUI/models/clip", exist_ok=True)
        os.makedirs("ComfyUI/models/unet", exist_ok=True)  # Added for flux1-dev
        os.makedirs("ComfyUI/models/bbox", exist_ok=True)
        os.makedirs("ComfyUI/models/sam", exist_ok=True)
        os.makedirs("ComfyUI/models/luts", exist_ok=True)
            
        # List of model weights to download
        weights_to_download = [
            # Checkpoints
            "flux1-dev.safetensors",
            
            # LoRAs
            "flux_realism_lora.safetensors",
            "Kasabulibaas.safetensors",
            
            # VAE
            "ae.safetensors",
            
            # CLIP models
            "t5xxl_fp16.safetensors",
            "clip_l.safetensors",
            
            # Detector models
            "hand_yolov8s.pt",
            "face_yolov8m.pt",
            "Eyeful_v2-Paired.pt",
            
            # SAM model
            "sam_vit_b_01ec64.pth",
            
            # LUT files
            "Presetpro - Portra 800.cube"
        ]
        
        self.comfyUI.handle_weights(
            workflow,
            weights_to_download=weights_to_download,
        )

    def filename_with_extension(self, input_file, prefix):
        extension = os.path.splitext(input_file.name)[1]
        return f"{prefix}{extension}"

    def handle_input_file(
        self,
        input_file: Path,
        filename: str = "image.png",
    ):
        shutil.copy(input_file, os.path.join(INPUT_DIR, filename))

    # Update our workflow based on user inputs
    def update_workflow(self, workflow, **kwargs):
        # Update prompt text in Jurdn's Groq API Prompt Enhancer (node 662)
        for node_id, node in workflow.items():
            # Update prompt in node 662
            if node_id == "662" and "class_type" in node and node["class_type"] == "JurdnsGroqAPIPromptEnhancer":
                node["inputs"]["text"] = kwargs["prompt"]
                print(f"Updated prompt in node {node_id}")
            
            # Update steps in node 709
            if node_id == "709" and "class_type" in node and node["class_type"] == "BasicScheduler":
                node["inputs"]["steps"] = kwargs["steps"]
                print(f"Updated steps in BasicScheduler to {kwargs['steps']}")
            
            # Update seed in Seed Everywhere node
            if node_id == "735" and "class_type" in node and node["class_type"] == "Seed Everywhere":
                node["inputs"]["seed"] = kwargs["seed"]
                print(f"Updated seed in node {node_id} to {kwargs['seed']}")
            
            # Update LoRAs in node 721 if provided
            if node_id == "721" and "class_type" in node and node["class_type"] == "Power Lora Loader (rgthree)":
                if kwargs.get("loras"):
                    loras = kwargs["loras"]
                    
                    # Always ensure at least the first two default LoRAs are properly configured
                    if len(loras) >= 1:
                        lora_name = loras[0]
                        if not lora_name.endswith(".safetensors"):
                            lora_name += ".safetensors"
                        
                        # Update the lora_1 field
                        node["inputs"]["lora_1"]["on"] = True
                        node["inputs"]["lora_1"]["lora"] = lora_name
                        node["inputs"]["lora_1"]["strength"] = 1
                        print(f"Updated first LoRA in node {node_id} to {lora_name}")
                    
                    if len(loras) >= 2:
                        lora_name = loras[1]
                        if not lora_name.endswith(".safetensors"):
                            lora_name += ".safetensors"
                        
                        # Update the lora_2 field
                        node["inputs"]["lora_2"]["on"] = True
                        node["inputs"]["lora_2"]["lora"] = lora_name
                        node["inputs"]["lora_2"]["strength"] = 1
                        print(f"Updated second LoRA in node {node_id} to {lora_name}")
                    
                    # Add additional LoRAs as needed
                    for i, lora_name in enumerate(loras[2:], start=3):
                        if not lora_name.endswith(".safetensors"):
                            lora_name += ".safetensors"
                        
                        # Add new LoRA field if it doesn't exist
                        lora_key = f"lora_{i}"
                        if lora_key not in node["inputs"]:
                            node["inputs"][lora_key] = {
                                "on": True,
                                "lora": lora_name,
                                "strength": 1
                            }
                            # Also update the "➕ Add Lora" field to trigger the UI to add a new slot
                            node["inputs"]["➕ Add Lora"] = ""
                        else:
                            node["inputs"][lora_key]["on"] = True
                            node["inputs"][lora_key]["lora"] = lora_name
                        
                        print(f"Added additional LoRA in node {node_id} to {lora_name}")
            
            # Update resolution if applicable (keeping this feature from before)
            if "_meta" in node and node["_meta"].get("title") == "Basic Image size":
                if kwargs["resolution"] == "768x1280":
                    node["inputs"]["resolution"] = "768x1280 (0.6)"
                elif kwargs["resolution"] == "512x768":
                    node["inputs"]["resolution"] = "512x768 (0.67)"
                elif kwargs["resolution"] == "1024x1024":
                    node["inputs"]["resolution"] = "1024x1024 (1.0)"
                elif kwargs["resolution"] == "1024x1536":
                    node["inputs"]["resolution"] = "1024x1536 (0.67)"
                print(f"Updated resolution in node {node_id}")

    def predict(
        self,
        prompt: str = Input(
            description="Text prompt for image generation",
            default="Love, at night on the beach, dancing, unity, happiness."
        ),
        loras: list = Input(
            description="List of LoRA names to apply (with or without .safetensors extension)",
            default=["flux_realism_lora", "Kasabulibaas"]
        ),
        resolution: str = Input(
            description="Image resolution (width x height)",
            default="768x1280",
            choices=["512x768", "768x1280", "1024x1024", "1024x1536"]
        ),
        steps: int = Input(
            description="Number of steps for image generation (higher = better quality but slower)",
            default=55,
            ge=20,
            le=100
        ),
        output_format: str = optimise_images.predict_output_format(),
        output_quality: int = optimise_images.predict_output_quality(),
        seed: int = seed_helper.predict_seed(),
    ) -> List[Path]:
        """Run image generation using the ComfyUI workflow"""
        self.comfyUI.cleanup(ALL_DIRECTORIES)

        # Generate a seed if not provided
        seed = seed_helper.generate(seed)
        
        print(f"Generating image with prompt: {prompt}, steps: {steps}, seed: {seed}, loras: {loras}")

        # No input image in this workflow, but handle it if needed in the future
        image_filename = None

        # Load the workflow
        with open(api_json_file, "r") as file:
            workflow = json.loads(file.read())

        # Update workflow with our parameters
        self.update_workflow(
            workflow,
            prompt=prompt,
            loras=loras,
            resolution=resolution,
            steps=steps,
            seed=seed,
        )

        # Run the workflow
        wf = self.comfyUI.load_workflow(workflow)
        self.comfyUI.connect()
        self.comfyUI.run_workflow(wf)

        # Return optimized output images
        return optimise_images.optimise_image_files(
            output_format, output_quality, self.comfyUI.get_files(OUTPUT_DIR)
        )
